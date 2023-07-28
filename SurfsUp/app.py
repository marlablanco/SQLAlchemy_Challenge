# dependencies.
from flask import Flask,jsonify
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import numpy as np
import datetime as dt


#################################################
# Database Setup
#################################################
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect existing db to new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references 
station=Base.classes.station
measurement=Base.classes.measurement

# Create our session 
session=Session(bind=engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return"""<h1> Welcome to the Honolulu, Hawaii API!</h1>(
        f"/api/v1.0/stations<br/>"
        f"/api//v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end note: put date in yyyy-mm-dd""
    )"""

#precipitation
@app.route("/api/v1.0/precipitation")
def prcp ():
    #calculate date one year from last date in data set
    one_year_date=dt.date(2017,8,23)-dt.timedelta(days=365)
    # Query precipitation data from last 12 months from the most recent date from Measurement table
    prcp_data=session.query(measurement.date,measurement.prcp).filter(measurement.date >= one_year_date()).all()
    #close sesssion
    session.close()
    #create dictionary and query results from your precipitation analysis
    prcp_list=[]
    for date,prcp in prcp_data:
        prcp_dict={}
        prcp_dict["date"]=date
        prcp_dict["precipitation"]=prcp
        prcp_list.append(prcp_dict)
    
    #return a list of jsonified precipitation data for last 12 months
    return jsonify(prcp_list)


#stations
@app.route("/api/v1.0/stations")
def stations():
    #start session
    session=Session(bind=engine)

    #query station data
    active_stations=session.query(station.station).all()
    total_stations=list(np.ravel(active_stations))

    #jsonify
    return jsonify(total_stations)

    #close session
    session.close()

#tobs 
@app.route("/api/v1.0/tobs")
def tobs():
    #create session
    session=Session(bind=engine)

    #query tobs from last 12 months
    one_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_data= session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').\
        filter(measurement.date >=one_year_date).all()

    # Close the session                   
    session.close()

    #create dictionary 
    tobs_list=[]
    for date,tobs in tobs_data:
        tobs_dict={}
        tobs_dict["date"]=date
        tobs_dict["tobs"]=tobs
        tobs_list.append(tobs_dict)

    #jsonify
    return jsonify(tobs_list)

# Define what to do when url has specific start date or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start=None, end=None):
    # Create the session
    session = Session(bind=engine)

    #list to query(min,max,avg temp)
    sel=[func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)]

    #check if end date
    if end==None:
        start_query=session.query(*sel).\
            filter(measurement.date>=start).all()

        #list
        start_list=list(np.ravel(start_query))

        #jsonify
        return jsonify(start_list)

        #query the data from start date to the end date
        start_end=session.query(*sel).\
            filter(measurement.date>=start).filter(measurement.date<=end).all()
        #list
        end_list=list(np.ravel(start_query))
    
        #jsonify
        return jsonify(end_list)
