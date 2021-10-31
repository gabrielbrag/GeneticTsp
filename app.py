import json
from forms import CreateRoute
from flask import Flask, escape, request, render_template
from flask_socketio import SocketIO
import folium
import sys
sys.path.insert(1, "C:/Users/Gabriel/Documents/Programação/TCC/FlaskWebpage/app/controllers")
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
async def progress():
    mutRate = int(request.form['mutation'])/100
    gens = request.form['gens']
    points = []
    points = request.form.getlist('points[]')
    print(str(points))
    routes = heuristic.routes()
    pathData = heuristic.heuristic(routes)
    genRoute = GA.train(pathData, int(gens), mutRate)
    print("GenRoute " + str(genRoute))
    coords = heuristic.coordsRoute(genRoute["genes"], routes)
    m = maps.CreateMap(coords, routes)
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
