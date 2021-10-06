import folium
from folium.features import DivIcon
import json

def CostRoute(request_routes, optRoute):
  current_node = 0
  next_node = optRoute[0]
  totalCost = 0
  for next_node in optRoute:
    for path in request_routes:
      if path['orig_node'] == current_node:
        for dest in path['dest']:
          if dest['dest_node'] == next_node:
            totalCost += dest['edge_cost']
            current_node = next_node
  return totalCost

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
