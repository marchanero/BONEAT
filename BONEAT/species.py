import math
import random
import genome

class SpeciesList:

    def __init__(self,population,disjointWeight=1.0,excessWeight=1.0,weightsWeight=0.5,threshold=2.0):
        self.disjointC = disjointWeight
        self.excessC = excessWeight
        self.weightsC = weightsWeight
        self.threshold = threshold
        self.population = population

        self.max_pop_fitness = 0.0

        self.l_species = []

    def addToSpecies(self,genome):

        # loop through all species and check to which it belongs
        for s in self.l_species:
            if self.sameSpecies(s.root_genome,genome):
                s.l_genomes.append(genome)
                break

        # if it didn't belong to any make a new one
        else:
            s = species(genome)
            self.l_species.append(s)

    def sameSpecies(self,speciesGenome,newGenome):

        # get genome difference
        D,W = difference(speciesGenome,newGenome)

        # calculate delta
        delta = self.disjointC*D+self.weightsC*W

        # check if this is within threshold
        return delta <= self.threshold

    def getAllGenomes(self):
        agl = []
        for s in self.l_species:
            agl.extend(s.l_genomes)
        return agl

    def removeWeakPopulation(self):

        self.max_pop_fitness = self.getMaxFitness()
        surv = []

        for species in self.l_species:
            # remove stale species
            if species.checkStaleness(self.max_pop_fitness):
                continue
            # remove weak population
            else:
                species.removeWeak()
                surv.append(species)

        allAlive = False
        while not allAlive:
            allAlive = True

            new_s_list = []
            sum_avg_fitness = sum(s.avg_fitness for s in self.l_species)

            for species in surv:
                if sum_avg_fitness != 0.0:
                    breed = int(math.floor((species.avg_fitness/sum_avg_fitness)*self.population))
                else:
                    breed = 1

                if breed < 0:
                    allAlive = False
                    continue
                else:
                    species.breed = breed
                    new_s_list.append(species)

            surv = new_s_list

        self.l_species = surv

    def getMaxFitness(self):
        return max(s.max_fitness for s in self.l_species)

    def breedChildren(self,innovations):

        new_gen_children = []
        # breed all the children for each species
        for s in self.l_species:
            new_gen_children.extend(s.breedChildren(innovations))

        # fill the remainder with wild children
        remainder = self.population-len(new_gen_children)
        all_Gs = self.getAllGenomes()
        for i in range(remainder):
            child=genome.crossover(random.sample(all_Gs,2),innovations)
            child.mutate(innovations)
            new_gen_children.append(child)

        self.newGeneration(new_gen_children)

    def newGeneration(self,new_generation):
        self.killOldGeneration()
        self.loadNewGenertion(new_generation)
        self.killExtinctSpecies()

    def killExtinctSpecies(self):
        surv = []
        for s in self.l_species:
            if len(s.l_genomes) > 0:
                surv.append(s)
        self.l_species = surv

    def loadNewGenertion(self,new_population):
        for G in new_population:
            self.addToSpecies(G)

    def killOldGeneration(self):
        for s in self.l_species:
            s.l_genomes = []

class species:

    def __init__(self,genome):
        self.root_genome = genome
        self.l_genomes = [genome]
        self.staleness = 0
        self.avg_fitness = 0.0
        self.max_fitness = 0.0
        self.breed = 0

    def removeWeak(self):
        split = int(math.ceil(len(self.l_genomes)/2.0))
        self.l_genomes.sort(key=lambda g: g.fitness, reverse=True)
        surv =self.l_genomes[:split]
        self.l_genomes = surv
        self.calculateAverageFitness()

    def checkStaleness(self,max_pop_fitness):
        maxfit = self.getMaxFitness()
        if maxfit > self.max_fitness:
            self.max_fitness = maxfit
            self.staleness = 0
        else:
            self.staleness += 1

        # CONSTANT
        if self.staleness > 20:
            return True
        else:
            return False

    def getMaxFitness(self):
        return max(g.fitness for g in self.l_genomes)

    def calculateAverageFitness(self):
        self.avg_fitness = sum(g.fitness for g in self.l_genomes)/float(len(self.l_genomes))

    def breedChildren(self,innovations):
        # CONSTANT
        crossoverchance = 0.80

        # update root genome
        self.root_genome = random.choice(self.l_genomes)

        children = []

        # copy genome 0
        children.append(self.l_genomes[0])

        # loop through remaining breed
        for i in range(self.breed-1):
            if random.random() <= crossoverchance and len(self.l_genomes)>1:
                child=genome.crossover(random.sample(self.l_genomes,2),innovations)

            else:
                child = random.choice(self.l_genomes)

            child.mutate(innovations)
            children.append(child)

        return children

def difference(genome1,genome2):

    disjointcounter = 0.0
    weightsum = 0.0
    weightcounter = 0.0
    max_genes = max(len(genome1.l_link_genes),len(genome2.l_link_genes))
    max_innov = max(genome1.getMaxInnovNum(),genome2.getMaxInnovNum())

    il1 = [None]*(max_innov+1)
    il2 = [None]*(max_innov+1)

    for g in genome1.l_link_genes:
        il1[g.innovationNumber]=g.weight

    for g in genome2.l_link_genes:
        il2[g.innovationNumber]=g.weight

    for i in range(len(il1)):
        if il1[i] != il2[i]:
            if il1[i] == None or il2[i] == None:
                disjointcounter += 1.0
            if il1[i] != None and il2[i] != None:
                weightcounter += 1.0
                weightsum += abs(il1[i]-il2[i])

    djr = disjointcounter/max_genes
    if weightcounter > 0.0:
        aw = weightsum/weightcounter
    else:
        aw = 0.0

    return djr, aw


