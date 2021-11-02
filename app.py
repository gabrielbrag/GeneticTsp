import json
from forms import CreateRoute
from flask import Flask, escape, request, render_template
from flask_socketio import SocketIO

from dotenv import load_dotenv
load_dotenv()

import sys
import os
sys.path.insert(1, os.getenv('CONTROLLERS_FOLDER'))

import heuristic
import maps
import GA
import files

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'c0eef4a2f5b5bb72e0b3191661dcca02'
socketio = SocketIO(app)

@app.route('/', methods=["GET", "POST"])
def hello():
    file = request.args.get('file')
    arrayAdd = files.getAddressFile(file)
    return render_template('home.html', title="IA Genética", arrayAdd=arrayAdd)

@app.route('/about')
def about():
    return render_template('about.html', title="about")

@app.route('/map')
def map():
    return render_template('map.html', title="about")

@app.route('/progress', methods=["POST"])
def progress():
    mutRate = int(request.form['mutation'])/100
    gens = request.form['gens']
    points = request.form.getlist('points[]')
    #request_routes = maps.gMapsRoutes(points) #Chama a API Gmaps
    #print(points)
    request_routes = {}
    routes = heuristic.routes() #Organiza os resultados
    pathData = heuristic.heuristic(routes)
    print('Params ' + '/' + str(gens) + '/' + str(mutRate))
    genRoute = GA.train(pathData, int(gens), mutRate)
    print("GenRoute " + str(genRoute))
    coords = heuristic.coordsRoute(genRoute["genes"], routes)
    m = maps.CreateMap(coords, routes)
    print('Type ' + str(type(m)))
    m.save("map.html")    
    return ''

@app.route('/initRoute', methods=["POST"])
def initRoute():
    req_data = json.loads(request.data)
    socketio.emit('initRoute', req_data)
    return '1'

@app.route('/updMap', methods=["POST"])
def update():
    req_data = json.loads(request.data)
    socketio.emit('updMap', req_data)
    return '1'

@app.route('/finish', methods=["POST"])
def nxtGen():
    socketio.emit('finish', request.form["endGen"])
    return '1'
