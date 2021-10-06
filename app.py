from forms import CreateRoute
from flask import Flask, escape, request, render_template
from flask_socketio import SocketIO
import folium
import sys
sys.path.insert(1, "C:/Users/Gabriel/Documents/Programação/TCC/FlaskWebpage/app/controllers")
import heuristic
import maps
import GA

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'c0eef4a2f5b5bb72e0b3191661dcca02'
socketio = SocketIO(app)

@app.route('/', methods=["GET", "POST"])
def hello():
    return render_template('home.html', title="blog")

@app.route('/about')
def about():
    return render_template('about.html', title="about")

@app.route('/map')
def map():
    return render_template('map.html', title="about")

@app.route('/progress')
async def progress():
    gens = request.args.get('gens')
    routes = heuristic.routes()
    pathData = heuristic.heuristic(routes)
    genRoute = GA.train(pathData, int(gens))
    print("GenRoute " + str(genRoute))
    coords = heuristic.coordsRoute(genRoute["genes"], routes)
    m = maps.CreateMap(coords, routes)
    m.save("map.html")    
    return ''

@app.route('/updMap')
def update():
    socketio.emit('evento')
    return '1'