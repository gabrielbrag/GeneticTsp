import folium
from folium.features import DivIcon
import json
import requests
from haversine import haversine
from multiprocessing import Pool
import os

#Calcula o custo de uma rota (tempo x distância)
def CostRoute(request_routes, optRoute):
  current_node = 0
  next_node = optRoute[0]
  totalDis = 0
  totalTime = 0
  totalCost = 0
  for next_node in optRoute:
    for path in request_routes:
      if path['orig_node'] == current_node:
        for dest in path['dest']:
          if dest['dest_node'] == next_node:
            totalDis += dest['edge_dis']
            totalTime += dest['edge_time']
            totalCost += dest['edge_cost']
            current_node = next_node
  costs = {"totalDis":totalDis, "totalTime":totalTime, "totalCost":totalCost}
  return costs

#Cria um mapa em html usando a biblioteca folium
def CreateMap(coordsRoute, routesI):
  m = folium.Map(location=[float(coordsRoute[0][0]), float(coordsRoute[0][1])],
               zoom_start=11) #Criamos um objeto mapa da biblioteca Folium, será usado para exibição

  folium.Marker([coordsRoute[0][0], coordsRoute[0][1]], 
              #popup='<b>' + 'oeeee' + '</b>', 
              icon=DivIcon(icon_size=(200,36),
                icon_anchor=(0,0),
                html='<div style="font-size: 12pt; color:blue; font-weight: bold">Ponto Inicial</div>' #Criamos uma legenda indicando o ponto inicial
              )).add_to(m)

  for ende in routesI: #Criamos um ponto no mapa para cada parada
    folium.Marker([ende["orig_coords"]["lat"], ende["orig_coords"]["lng"]], 
                  popup='<b>' + ende["orig_name"] + '</b>',  
                  icon = folium.features.CustomIcon('https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png', icon_size=(18,18))).add_to(m)

  tuples = [tuple(x) for x in coordsRoute] #Percorremos a rota do parâmetro criando uma linha verde indicando o caminho
  folium.PolyLine(tuples, color="green", weight=2.5, opacity=1).add_to(m) 

  m.save(os.getenv('ROOT_DIR') + "/templates/map.html")
  return m

def coordsPoints(points):
  coords = []
  for point in points:
    r = requests.get('https://api.mapbox.com/geocoding/v5/mapbox.places/' + point + '.json?access_token=pk.eyJ1IjoiamVhbmN3YiIsImEiOiJja2VnZmI2czYwa3loMnFyejdhaDVzZzhjIn0.5YA3in_HTwmOM1WOa7CTIg&bbox=-73.9872354804, -33.7683777809, -34.7299934555, 5.24448639569')
    jsonDict = json.loads(r.text)
    lng = jsonDict["features"][0]["geometry"]["coordinates"][1]
    lat = jsonDict["features"][0]["geometry"]["coordinates"][0]
    item = (lng,lat)
    coords.append(item)
  return coords

def createBaseMap(coords):  
  m = folium.Map(location=[float(coords[0]["lat"]), float(coords[0]["lng"])],
               zoom_start=11) #Criamos um objeto mapa da biblioteca Folium, será usado para exibição

  folium.Marker([coords[0]["lng"], coords[0]["lat"]],  
                icon = folium.features.CustomIcon('https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png', icon_size=(18,18))).add_to(m)

  for coord in coords: #Criamos um ponto no mapa para cada parada
    folium.Marker([coord["lat"], coord["lng"]],
                  icon = folium.features.CustomIcon('https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png', icon_size=(18,18))).add_to(m)

  m.save(os.getenv('ROOT_DIR') + "/templates/map.html")
  requests.post('http://localhost:5000/updMap', json=json.dumps(''))
  return m

def gMapsRoutes(edges):
  request_routes = []
  coordsEnde = []
  s = requests.Session()
  mapCreated = False
  for index1, end1 in enumerate(edges):
    if index1 != (len(edges)):
      for index2, end2 in enumerate(edges):
        routes_list = []
        if end1 != end2:
          req_str = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + end1 + '&destination=' + end2 + '&key=' + os.getenv("GMAPS_KEY")
          r = s.get(req_str)
          #print(req_str)
          jsonDict = json.loads(r.text)
          #print(jsonDict)
          jsonDict["routes"][0]["legs"]
          routes_dict = {}
          travelTime = jsonDict["routes"][0]["legs"][0]["duration"]["value"]
          totalDistance = jsonDict["routes"][0]["legs"][0]["distance"]["value"]
          origCoords = jsonDict["routes"][0]["legs"][0]["start_location"]
          endCoords = jsonDict["routes"][0]["legs"][0]["end_location"]
          points = []
          for step in jsonDict["routes"][0]["legs"][0]["steps"]:
            points.append(step["end_location"])
          
          if not mapCreated:
            if index2 == 1:
              coordsEnde.append(origCoords)
              
            coordsEnde.append(endCoords)
          
          path_dict = {'origin_name':end1, 'path_orig':index1, 'orig_coords':origCoords, 'end_coords':endCoords, 'dest_name':end2, 'path_dest':index2, 'travelTime':travelTime, 'totalDistance':totalDistance, 'points':points}
          request_routes.append(path_dict)
  
    if not mapCreated:
      createBaseMap(coordsEnde)
      mapCreated = True
  
  with open((os.getenv('ROOT_DIR') + '\\' + 'BackupRequest.json'), 'w') as outfile:
    json.dump(request_routes, outfile)
  return request_routes