import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement

# Save reference to the table
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/date(start of range)<br/>"
        f"/api/v1.0/date(start of range)/date(end of range)"
    )


@app.route("/api/v1.0/precipitation")
def precip():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dictionaries containing last year prcp"""
    final_day = session.query(measurement.date).order_by(measurement.date.desc()).first()
    begin_day = dt.datetime.strptime(final_day[0], '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).\
        filter(begin_day <= measurement.date).all()

    session.close()

    yearlong = []
    for date, prcp in results:
        daily = {}
        daily[date] = prcp
        yearlong.append(daily)

    return jsonify(yearlong)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.query(station.name).all()

    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of last year tobs"""
    final_day = session.query(measurement.date).order_by(measurement.date.desc()).first()
    begin_day = dt.datetime.strptime(final_day[0], '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(begin_day <= measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return min, avg, max after date"""
    results = session.query(func.min(measurement.tobs),\
                            func.avg(measurement.tobs),\
                            func.max(measurement.tobs)).\
                            filter(measurement.date > start).all()

    session.close()

    ret = [{'minimum temperature' : results[0][0]},\
           {'average temperature' : results[0][1]},\
           {'maximum temperature' : results[0][2]}]

    return jsonify(ret)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return min, avg, max between dates"""
    results = session.query(func.min(measurement.tobs),\
                            func.avg(measurement.tobs),\
                            func.max(measurement.tobs)).\
                            filter(measurement.date > start).\
                            filter(measurement.date < end).all()

    session.close()

    ret = [{'minimum temperature' : results[0][0]},\
           {'average temperature' : results[0][1]},\
           {'maximum temperature' : results[0][2]}]

    return jsonify(ret)


if __name__ == '__main__':
    app.run(debug=True)
