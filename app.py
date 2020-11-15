# import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# flask setup
app = Flask(__name__)

# flask routes
@app.route("/")
def home():
    return (
        f"Hawaii Climate Analysis API<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # create a session
    session = Session(engine)    
    """Return precipitation data from the last year"""
    
    # calculate the date 1 year ago from the last date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # query to retrieve the data and precipitation measurements
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # create dictionary with date as the key and precipitation as the value
    prcp = {date: prcp for date, prcp in precipitation}
    return jsonify(precipitation=prcp)

    # close the session
    session.close()

@app.route("/api/v1.0/stations")
def stations():
     # create a session
    session = Session(engine)    
    """Return list of stations"""

    # query to find list of stations
    stquery = session.query(Station.station).all()

    # unravel results and convert to list
    stations = list(np.ravel(stquery))
    return jsonify(stations=stations)

    # close the session
    session.close()

@app.route("/api/v1.0/tobs")
def temp():
     # create a session
    session = Session(engine)
    """Return temperature data from the last year"""

    # calculate the date 1 year ago from the last date
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # query to retrieve the data and temperature measurements
    temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year).all()

    # unravel results and convert to list
    temp = list(np.ravel(temp))
    return jsonify(temperature=temp)

    # close the session
    session.close()

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def tempstats(start=None, end=None):
     # create a session
    session = Session(engine)    
    """Return min temp, avg temp, max temp for given start or start-end range."""

    # select data values
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate stats for dates greater than start
        startqry = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        # unravel results and convert to list
        startstats = list(np.ravel(startqry))
        return jsonify(tempstats=startstats)

    # calculate stats for start and end dates
    endqry = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    # unravel results and convert to list
    endstats = list(np.ravel(endqry))
    return jsonify(tempstats=endstats)

    # close the session
    session.close()

if __name__ == "__main__":
    app.run(debug=True)