import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Station ids, Dates, and Precipitation"""

    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of Station ids, Dates, and Precipitation
    
    all_stations = list(np.ravel(results))
    # for station, date, prcp in results:
    #     station_dict = {}
    #     station_dict["station"] = station
    #     station_dict["date"] = date
    #     station_dict["prcp"] = precipitation
    #     all_stations.append(station_dict)
        
#HELP error is howing this is a list and can't be jsonify...
    return jsonify(all_stations)


##Working!
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station data including the name, latitude, longitude, and elevation for each station"""
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*sel).all()

    session.close()

    stations = []
    for station,name,lat,lon,el in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)


##HELP - UnboundLocalError: local variable 'start_date_year_past' referenced before assignment
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of the dates and temperature observations of the most active station for the last year of data."""
    
    latest_date_query = (session
                     .query(Measurement.date)
                     .order_by(Measurement.date.desc())
                     .first()
                    )
    latest_date = dt.datetime.strptime(latest_date_query[0], '%Y-%m-%d')
    start_date_year_past = dt.date(latest_date.year -1, latest_date.month, latest_date.day)
    
    query_result = (session.query(Measurement.date, Measurement.tobs)
                .filter(Measurement.date >= start_date_year_past)
                .all()
               )
    
    
    session.close()
    
    
    tobsall = []
    for date, tobs in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

#Working!
@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return calculatation of  TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    query_result = (session
                    .query(*sel)
                    .filter(Measurement.date >= start)
                    .all()
                   )
    session.close()

    tobsall = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


#HELP getting NULL assuming my date formatting is causing this?
@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return calculatation of  TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    queryresult = (session.query(*sel)
                   .filter(Measurement.date >= start)
                   .filter(Measurement.date <= stop)
                   .all()
                  )
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)
