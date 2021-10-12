import random
import maps
import heuristic
import requests as r


def mutation(genes, mutationRate):
  for gene in genes:
    if random.random() < mutationRate:
      indexA = random.randint(0, len(genes) - 1)
      indexB = indexA
      while indexB == indexA:
        indexB = random.randint(0, len(genes) - 1)
      if indexA > indexB:
        auxB = indexB
        indexB = indexA
        indexA = auxB
      x = indexA
      y = indexB
      while x < y:
        aux = genes[x]
        genes[x] = genes[y]
        genes[y] = aux 
        x += 1
        y -= 1
      break
  return genes


def startGeneration(route, popSize, mutationRate):
  generation = []
  for x in range(1, popSize):
    sample = mutation(route.copy(), mutationRate)
    generation.append(sample.copy())
  return generation


def normalizeFitness(genes):
    genFitness = []
    totalFitness = 0
    for gene in genes:
      population = {}
      population['genes'] = gene
      fitness = 1 / maps.CostRoute(idealRoutes, gene)
      population['fitness'] = fitness
      genFitness.append(population)
      totalFitness += fitness
    
    for population in genFitness:
      population['Normfitness'] = population['fitness'] / totalFitness

    return genFitness


def crossOver(orderA, orderB):
  start = random.randint(0, len(orderA) - 1)
  end = random.randint(start, len(orderA) - 1)
  if start > end:
    auxStart = start
    start = end
    end = auxStart

  sliced = []
  if start == end:
    sliced.append(orderA[start])
  else:
    sliced = orderA[start:(end+1)].copy()
  offspring = []
  x = 0
  while len(offspring) < len(orderB):
    if len(offspring) >= start and len(offspring) <= end:
      for y in range(start, end + 1):
        offspring.append(orderA[y])
    else:
      try:
        if not orderB[x] in sliced:
          offspring.append(orderB[x])
        x += 1
      except:
        break
  return offspring


def fitWeights(generation):
  weights = []
  for population in generation:
    weights.append(population['Normfitness'])
  return weights

def chooseParents(generation):
  bestGenes = {}
  bestGenes["father"] = generation[0]["genes"]
  fatherFit = generation[0]["fitness"]
  bestGenes["mother"] = generation[1]["genes"]
  motherFit = generation[0]["fitness"]
  for sample in generation:
    if sample["fitness"] > fatherFit:
      bestGenes["father"] = sample["genes"]
      fatherFit = sample["fitness"]
    else:
      if sample["fitness"] > motherFit:
        bestGenes["mother"] = sample["genes"]
        motherFit = sample["fitness"]
  return bestGenes

def nextGeneration(generation):
  newGeneration = []
  newGenes = []
  bestGenes = chooseParents(generation.copy())
  for population in generation:
    crossGen = crossOver(bestGenes["father"], bestGenes["mother"])
    newSample = []
    newSample = mutation(crossGen.copy(), 0.3)
    newGenes.append(newSample.copy())
  newGeneration = normalizeFitness(newGenes)
  return newGeneration

def train(pathData, numGen, mutRate):
  print('Mutation rate' + str(mutRate))
  global idealRoutes
  idealRoutes = pathData["idealRoutes"]
  generation = startGeneration(pathData["optRoute"].copy(), 100, mutRate)
  generation = normalizeFitness(generation.copy())
  bestFit = 0
  bestSample = []
  for a in range(1, numGen):
    
    generation = nextGeneration(generation.copy())
    for sample in generation:
      if sample["fitness"] > bestFit:
        bestFit = sample["fitness"]
        bestSample = sample
        coords = heuristic.coordsRoute(bestSample["genes"], idealRoutes)
        m = maps.CreateMap(coords, idealRoutes)
        m.save("map.html") 
        r.post('http://localhost:5000/updMap', data={"valor":"1"})
  return bestSample