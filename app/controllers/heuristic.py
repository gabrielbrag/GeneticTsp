import json

def routes():
    with open('C:/Users/Gabriel/Documents/Programação/TCC/FlaskWebpage/BackupRequest.json') as json_file:
        request_routes = json.load(json_file)

    routesI  = []
    for path in request_routes:
        current_node = path["path_orig"]
        pesoDec = (path['totalDistance'] * path['travelTime']) #Multiplicando os dois fatores para ter um peso de decisão
        pathCoords = []
        pathCoords = path["points"]
        pathCoords.append(path["end_coords"]) 
        #print(len(pathCoords))
        dest_name = path['dest_name']
        edge = {'dest_node':path['path_dest'], 'dest_name':dest_name, 'edge_dis':path['totalDistance'], 'edge_time':path['travelTime'], 'edge_cost': pesoDec, 'route_points':pathCoords}
        found_node = False
        for routeIndex, routeI in enumerate(routesI): #Passando pela lista de rotas ideais
            if routeI['orig_node'] == current_node: #Se achar um item na lista cujo nó de origem é igual a origem atual, usa ele
                routesI[routeIndex]['dest'].append(edge) #Coloca o destino
                found_node = True
        if not found_node: #Senão encontrar o nó origem atual (ponto) na lista de rotas ideias, cria ele e coloca um ponto de destino
            orig_name = path['origin_name']
            new_routeI = {'orig_node':current_node, 'orig_name':orig_name, 'orig_coords':path['orig_coords'], 'dest':[]}
            new_routeI['dest'].append(edge)
            routesI.append(new_routeI)
    return routesI

def bestPath(currentPoint, pathData):
    lowerValue = 0
    isPassed = False
     
    vetor = pathData["idealRoutes"][currentPoint]['dest']
    for value in vetor:
        if lowerValue == 0 or lowerValue > value['edge_cost'] and pathData["currentPoint"] != value['dest_node']:
            for item in pathData["lastPoints"]: #Valida se já passou pelo ponto antes
                if item == value['dest_node']:
                    isPassed = True
            
            if len(pathData["lastPoints"]) == len(pathData["idealRoutes"]): #Se pontos passados for igual número de pontos, estamos no fim da rota
                pathData["currentPoint"] = pathData["arrivalPoint"]
            
            if isPassed == False: #Se não se passou por esse ponto ainda
                lowerValue = value['edge_cost']
                pathData["currentPoint"] = value['dest_node']

        isPassed = False

    pathData["optRoute"].append(pathData["currentPoint"])
    
    pathData["lastPoints"].append(pathData["currentPoint"])

    if pathData["iterations"] >= len(pathData["idealRoutes"]) - 2:
        return pathData
    else:
        pathData["iterations"] += 1
        pathData = bestPath(pathData["currentPoint"], pathData)
        return pathData


def heuristic(routesI):
    pathData = {}
    pathData["idealRoutes"] = routesI
    pathData["arrivalPoint"] = 41
    pathData["iterations"] = 0
    pathData["optRoute"] = []
    pathData["lastPoints"] = [0]

    pathData = bestPath(0, pathData)
    
    return pathData

def coordsRoute(optRoute, routesI):
    coordsRoute = []
    currentNode = 0
    iterations = 0
    for idx, route in enumerate(optRoute):
        for edge in routesI:
            if edge['orig_node'] == currentNode:
                nextNode = optRoute[idx]
                for destNode in edge['dest']:
                    if destNode['dest_node'] == nextNode:
                        iterations += 1
                        for coords in destNode['route_points']:
                            coordsRoute.append([coords['lat'],coords['lng']])
                            currentNode = nextNode
                break
    return coordsRoute