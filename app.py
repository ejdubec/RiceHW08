import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Flask Time
app = Flask(__name__)

@app.route('/')
def home():
    'List all routes.'
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/START_DATE<br/>"
        f"/api/v1.0/START_DATE/END_DATE"
    )

@app.route('/api/v1.0/precipitation')
def prcpJ():
    prcpD = {}
    results = session.query(Measurement).all()
    for result in results:
        resDict = {}
        if result.date in prcpD.keys():
            prcpD[result.date][result.station] = result.prcp
        else:
            resDict[result.station] = result.prcp
            prcpD[result.date] = resDict

    return jsonify(prcpD)

@app.route('/api/v1.0/stations')
def stationsJ():
    results = session.query(Station).all()
    stationsL = []

    for s in results:
        sDict = {}
        sDict['id'] = s.station
        sDict['name'] = s.name
        sDict['lat'] = s.latitude
        sDict['lon'] = s.longitude
        sDict['ele'] = s.elevation
        stationsL.append(sDict)

    return jsonify(stationsL)

@app.route('/api/v1.0/tobs')
def tobsY():
    last = session.query(Measurement).order_by(Measurement.date.desc()).first()
    lastDT = last.date
    lastDT = dt.datetime.strptime(lastDT, '%Y-%m-%d')
    yearAgo = lastDT - dt.timedelta(days = 365)
    dates = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date.between(yearAgo, lastDT)).order_by(Measurement.date).all()

    dList = []

    for d in dates:
        dDict = {}
        dDict[d.date] = d.tobs
        dList.append(dDict)
    
    return jsonify(dList)

@app.route('/api/v1.0/<start>')
def stToPres(start):
    last = session.query(Measurement).order_by(Measurement.date.desc()).first()
    lastDT = last.date
    lastDT = dt.datetime.strptime(lastDT, '%Y-%m-%d')
    stDT = dt.datetime.strptime(start, '%Y-%m-%d')

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date.between(stDT, lastDT)).all()
    
    tList = []

    for result in results:
        tDict = {}
        tDict['TMIN'] = result[0]
        tDict['TAVG'] = result[1]
        tDict['TMAX'] = result[2]
        tList.append(tDict)
    
    return jsonify(tList)

# start to end is the same but slightly easier

@app.route('/api/v1.0/<start>/<end>')
def stToEnd(start, end):
    endDT = dt.datetime.strptime(end, '%Y-%m-%d')
    stDT = dt.datetime.strptime(start, '%Y-%m-%d')

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date.between(stDT, endDT)).all()
    
    tList = []

    for result in results:
        tDict = {}
        tDict['TMIN'] = result[0]
        tDict['TAVG'] = result[1]
        tDict['TMAX'] = result[2]
        tList.append(tDict)
    
    return jsonify(tList)

if __name__ == '__main__':
    app.run(debug=True)