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

#HOME PAGE
@app.route('/', methods=["GET", "POST"])
def hello():
    file = request.args.get('file')
    arrayAdd = files.getAddressFile(file)
    return render_template('home.html', title="IA Genética", arrayAdd=arrayAdd)

#MAPA EXIBIDO NA TELA
@app.route('/map')
def map():
    return render_template('map.html', title="about")


@app.route('/progress', methods=["POST"])
def progress():
    #Recuperando dados da requisição
    mutRate = int(request.form['mutation'])/100
    gens = request.form['gens']
    points = request.form.getlist('points[]')
    print("chegou aqui eeeeee")
    request_routes = maps.gMapsRoutes(points) #Chama a API Gmaps
    #print(points)
    #request_routes = {}
    routes = heuristic.routes() #Organiza os resultados
    pathData = heuristic.heuristic(routes) #Aplicando Heuristica
    genRoute = GA.train(pathData, int(gens), mutRate) #Aciona o algoritimo genético
    coords = heuristic.coordsRoute(genRoute["genes"], routes) #Retorna coordenadas da rota obtida
    m = maps.CreateMap(coords, routes) #Cria um mapa em html
    m.save("map.html") #salva o arquivo
    return ''

#WEBSOCKET: Notifica dados da rota inicial (obtida com heuristica)
@app.route('/initRoute', methods=["POST"])
def initRoute():
    req_data = json.loads(request.data)
    socketio.emit('initRoute', req_data)
    return '1'

#WEBSOCKET: Notifica update no mapa (quando a IA encontra uma rota melhor)
@app.route('/updMap', methods=["POST"])
def update():
    req_data = json.loads(request.data)
    socketio.emit('updMap', req_data)
    return '1'

#WEBSOCKET: Notifica final do processo
@app.route('/finish', methods=["POST"])
def nxtGen():
    socketio.emit('finish', request.form["endGen"])
    return '1'
