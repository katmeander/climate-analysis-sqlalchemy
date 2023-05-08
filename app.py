# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB


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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/ - Enter the start date after '/api/v1.0/' in YYYYMMDD format</br>or Enter the start date, then '/' then end date in YYYYMMDD format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #retrieve only the last 12 months
    year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #get all the query results from precipitation analysis, using the variable for the last year
    last_year_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_from_recent).all()
    
    session.close()

    #convert list of tuples into normal list
    all_prcp_list = list(np.ravel(last_year_prcp))

    #turn query results into a dictionary
    all_prcp = []
    for date, prcp in last_year_prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        all_prcp.append(prcp_dict)
 
    #convert to jsonify
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #query all the stations
    results_stations = session.query(Station.station).all()

    session.close()

    #convert list of tuples into normal list
    all_stations = list(np.ravel(results_stations))

    #convert to json
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #find the most active station
    year_from_recent = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        filter(Measurement.date >= year_from_recent).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    #get the temperature observations and dates
    temp_dates = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_station).all()
    
    session.close()
    
    temp_obs = list(np.ravel(temp_dates))
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start_date>")
def start_temp(start_date):
    #print("Enter the start date after '/api/v1.0/' in YYYYMMDD format")

    #this creates a variable that tells you to look in the Measurement table then calculate the avg, man, min 
    #of the temperature on that date
    sel = [func.avg(Measurement.tobs), 
           func.max(Measurement.tobs), 
           func.min(Measurement.tobs)]
    
    session = Session(engine)

    #changes the date format so that calculations can be made
    query_date =  dt.datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
   
   #perform the calculations on the queried dates
   #this uses that variable to create a session query to get the avg, min, max on all dates greater than start date
    calc = session.query(*sel).\
        filter(Measurement.date >= query_date).all()

#close the session
    session.close() 

#create an empty list    
    all_start_dates = []

#add the calculations to the empty list    
    for func_avg, func_max, func_min in calc:
        dates_dict = {}
        dates_dict["average_temp"] = func_avg
        dates_dict["max_temp"] = func_max
        dates_dict["min_temp"] = func_min
        all_start_dates.append(dates_dict)
        
    return jsonify(all_start_dates)

    return jsonify({"error": f"The date {start_date} not found."}), 404
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
#this is the same as the route above except that you are getting two inputs instead of one    
#this creates a variable that tells you to look in the Measurement table then calculate the avg, man, min 
#of the temperature on that date
    sel = [func.avg(Measurement.tobs), 
           func.max(Measurement.tobs), 
           func.min(Measurement.tobs)]
    
    session = Session(engine)

# this changes the date format so that the calculations can be performed
    query_start =  dt.datetime.strptime(start, '%Y%m%d').strftime('%Y-%m-%d')
    query_end = dt.datetime.strptime(end, '%Y%m%d').strftime('%Y-%m-%d')

#this uses that variable to create a session query to get the avg, min, max on all dates greater than start date, less than end
    calc = session.query(*sel).filter(Measurement.date >= query_start).filter(Measurement.date <= query_end).all()  
    
    session.close() 

    all_start_end_dates = []
    #TAKE THE RETURN LIST AND JSONIFY IT
    for func_avg, func_max, func_min in calc:
        dates_dict = {}
        dates_dict["average_temp"] = func_avg
        dates_dict["max_temp"] = func_max
        dates_dict["min_temp"] = func_min
        all_start_end_dates.append(dates_dict)
        
    return jsonify(all_start_end_dates)

    return jsonify({"error": f"The date {start} or {end} date is not found."}), 404




#This must be the last two lines of code
if __name__ == '__main__':
    app.run(debug=True)