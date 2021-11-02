import json
import random
import maps
import heuristic
import requests as r
import os

#FUNÇÕES ENVOLVENDO ALGORITIMO GENÉTICO

#Mutação de um conjunto de genes
def mutation(genes, mutationRate):
  for gene in genes:
    #Sorteia um número e valida se menor que a taxa de mutação
    if random.random() < mutationRate:
      indexA = random.randint(0, len(genes) - 1)
      indexB = indexA
      while indexB == indexA:
        indexB = random.randint(0, len(genes) - 1) #Sorteia um segundo indice
      if indexA > indexB: #Faz indice A ser sempre menor que B
        auxB = indexB
        indexB = indexA
        indexA = auxB
      x = indexA
      y = indexB
      while x < y: #Inverte o caminho entre Indice A e B
        aux = genes[x]
        genes[x] = genes[y]
        genes[y] = aux 
        x += 1
        y -= 1
      break
  return genes


#Cria geração 1
def startGeneration(route, popSize, mutationRate):
  generation = []
  for x in range(1, popSize): #Cria "filhos" da rota pai iguais o tamanho da população
    sample = mutation(route.copy(), mutationRate)
    generation.append(sample.copy())
  return generation


#Define a fitness/eficiencia de cada membro da população
def normalizeFitness(genes):
    genFitness = []
    totalFitness = 0
    for gene in genes:
      population = {}
      population['genes'] = gene

      #Fitness = 1/Custo (quanto menor o custo, mais eficiente a rota é)
      fitness = 1 / maps.CostRoute(idealRoutes, gene)["totalCost"] 
      population['fitness'] = fitness 
      genFitness.append(population)
      totalFitness += fitness
    
    for population in genFitness:
      #Verifica quanto da eficiencia total o membro da população possuí
      population['Normfitness'] = population['fitness'] / totalFitness

    return genFitness


#Crossover/Cruzamento entre duas rotas
def crossOver(orderA, orderB):
  #Determina um segmento a ser copiado do pai
  #Filho vai possuir este segmento igual o pai e os demais pontos igual a mãe
  start = random.randint(0, len(orderA) - 1) 
  end = random.randint(start, len(orderA) - 1)
  if start > end:
    auxStart = start
    start = end
    end = auxStart

  sliced = []
  if start == end: #Recorta o segmento
    sliced.append(orderA[start])
  else:
    sliced = orderA[start:(end+1)].copy() 

  offspring = []
  x = 0
  #Cria o filho
  while len(offspring) < len(orderB):
    if len(offspring) >= start and len(offspring) <= end: #Se esta no trecho a ser copiado do pai
      for y in range(start, end + 1):
        offspring.append(orderA[y]) #Copiando segmento do pai
    else: #Senão copia da mãe
      try:
        if not orderB[x] in sliced:
          offspring.append(orderB[x]) #Copiando segmento da mãe
        x += 1
      except:
        break
  return offspring


#Determina os pesos de decisão para pais (quanto mais eficiente, mais chance de ser escolhido)
def fitWeights(generation):
  weights = []
  for population in generation:
    weights.append(population['Normfitness'])
  return weights

#Escolher pais
def chooseParents(generation):
  bestGenes = {}
  bestGenes["father"] = generation[0]["genes"]
  fatherFit = generation[0]["fitness"]
  bestGenes["mother"] = generation[1]["genes"]
  motherFit = generation[0]["fitness"]
  for sample in generation: #Loop pela geração inteira
    if sample["fitness"] > fatherFit: #Valida se fitness maior que o pai
      bestGenes["father"] = sample["genes"]
      fatherFit = sample["fitness"]
    else: #Senão valida se é maior que a da mãe
      if sample["fitness"] > motherFit:
        bestGenes["mother"] = sample["genes"]
        motherFit = sample["fitness"]
  return bestGenes #Retorna sempre os dois melhores cromosomos

#Cria uma nova geração
def nextGeneration(generation):
  newGeneration = []
  newGenes = []
  bestGenes = chooseParents(generation.copy()) #Escolhe os pais dentro da geração atual
  for population in generation: #Nova geração terá o mesmo tamanho da anterior
    crossGen = crossOver(bestGenes["father"], bestGenes["mother"]) #Cruza pai/mãe
    newSample = []
    newSample = mutation(crossGen.copy(), 0.3) #Realiza mutações
    newGenes.append(newSample.copy())
  newGeneration = normalizeFitness(newGenes) #Determina eficiencia da geração
  return newGeneration

#Treina a IA
def train(pathData, numGen, mutRate):
  global idealRoutes
  idealRoutes = pathData["idealRoutes"]
 
  #Determina os custos iniciais (geração 0) e envia para o cliente
  initCosts = maps.CostRoute(idealRoutes, pathData["optRoute"].copy())
  initData={"distance":initCosts["totalDis"], "time":initCosts["totalTime"]}
  r.post('http://localhost:5000/initRoute', json=json.dumps(initData) )

  costs = maps.CostRoute(idealRoutes, pathData["optRoute"].copy())
  initTime = costs["totalTime"] #Tempo inicial
  initDis = costs["totalDis"] #Distancia inicial

  generation = startGeneration(pathData["optRoute"].copy(), 100, mutRate) #Cria geração 1
  generation = normalizeFitness(generation.copy()) #Determina eficiencia
  bestSample = normalizeFitness([pathData["optRoute"].copy()])[0] #salva na variavel bestSample
  bestFit = bestSample["fitness"]
  fitChanged = False

  coords = heuristic.coordsRoute(bestSample["genes"], idealRoutes) #Cria o mapa com a rota 1
  m = maps.CreateMap(coords, idealRoutes)
  m.save("map.html") 
  r.post('http://localhost:5000/updMap', json=json.dumps(''))

  for a in range(1, numGen): #Numero de iteraçoes = parâmetro
    generation = nextGeneration(generation.copy()) #Cria a próxima geração baseada na anterior
    for sample in generation:
      if sample["fitness"] > bestFit: #Verifica se foi encontrado um filho melhor que o melhor atual
        bestFit = sample["fitness"]
        fitChanged = True
        bestSample = sample
        coords = heuristic.coordsRoute(bestSample["genes"], idealRoutes)
        m = maps.CreateMap(coords, idealRoutes)
        m.save("map.html") #Se encontrar salva ele e cria um mapa

        #Tratando dados que serão enviados ao cliente
        genData = {}
        genData["currentGen"] = a
        costs = maps.CostRoute(idealRoutes, bestSample["genes"].copy())
        percentTime = (costs["totalTime"] * 100) / initTime
        percentDis = (costs["totalDis"] * 100) / initDis 
        genData["timeGain"] = 100 - percentTime
        genData["disGain"] = 100 - percentDis
        genData["distance"] = costs["totalDis"]
        genData["time"] = costs["totalTime"]

    if fitChanged: #Se melhor rota mudou, notifica cliente
      r.post('http://localhost:5000/updMap', json=json.dumps(genData))
      fitChanged = False

  #Notifica conclusão do processo
  r.post('http://localhost:5000/finish', data={"endGen":numGen})
  return bestSample