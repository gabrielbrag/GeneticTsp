import folium
from folium.features import DivIcon
import json
import requests
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

  m.save("C:/Users/Gabriel/Documents/Programação/TCC/FlaskWebpage/templates/map.html")
  return m

#Dado uma lista de endereços, busca no google maps as rotas possíveis entre eles
def gMapsRoutes(edges):
  request_routes = []
  for index1, end1 in enumerate(edges):
    if index1 != (len(edges)):
      for index2, end2 in enumerate(edges):
        routes_list = []
        if end1 != end2:
          req_str = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + end1 + '&destination=' + end2 + '&key=' + os.getenv("GMAPS_KEY")
          r = requests.get(req_str)
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
          path_orig = index1
          path_dest = index2
          path_dict = {'origin_name':end1, 'path_orig':index1, 'orig_coords':origCoords, 'end_coords':endCoords, 'dest_name':end2, 'path_dest':index2, 'travelTime':travelTime, 'totalDistance':totalDistance, 'points':points}
          request_routes.append(path_dict)
  with open((os.getenv('ROOT_DIR') + '\\' + 'BackupRequest.json'), 'w') as outfile:
    json.dump(request_routes, outfile)
  return request_routes