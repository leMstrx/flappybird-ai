import random
import copy

def crossover(nn1, nn2):   
    '''
    Perform crossover between two neural networks (parents)
    Return a new natural network (child)
    '''
    child = copy.deepcopy(nn1)
    # let's do a simple 50/50 from each parent
    for i in range(len(nn1.W1)):
        for j in range(len(nn1.W1[0])):
            if random.random() < 0.5:
                child.W1[i][j] = nn2.W1[i][j]

    for i in range(len(nn1.b1)):
        if random.random() < 0.5:
            child.b1[i] = nn2.b1[i]

    for i in range(len(nn1.W2)):
        for j in range(len(nn1.W2[0])):
            if random.random() < 0.5:
                child.W2[i][j] = nn2.W2[i][j]

    for i in range(len(nn1.b2)):
        if random.random() < 0.5:
            child.b2[i] = nn2.b2[i]


    return child

def mutate(nn, mutation_rate = 0.1, mutation_strength = 0.5):
    '''
    Mutate the weights of a neural network with given probability and strength
    '''
    for i in range(len(nn.W1)):
        for j in range(len(nn.W1[0])):
            if random.random() < mutation_rate:
                nn.W1[i][j] += random.uniform(-mutation_strength, mutation_strength)

    for i in range(len(nn.b1)):
        if random.random() < mutation_rate:
            nn.b1[i] += random.uniform(-mutation_strength, mutation_strength)

    for i in range(len(nn.W2)):
        for j in range(len(nn.W2[0])):
            if random.random() < mutation_rate:
                nn.W2[i][j] += random.uniform(-mutation_strength, mutation_strength)

    for i in range(len(nn.b2)):
        if random.random() < mutation_rate:
            nn.b2[i] += random.uniform(-mutation_strength, mutation_strength)

def next_generation(population, fitnesses, elite_size=5):
    '''
    Given the current pipultation and their fitnesses, produce the next generation of AI Bots
    population: list of neural networks
    fitnesses: list of fitness values
    elite_size: number of top performing networks to keep for the next generation
    '''
    #Sort by fitness descending
    sorted_pop = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
    #Keep top networks as elites
    new_population = [copy.deepcopy(ind[0]) for ind in sorted_pop[:elite_size]]

    #Fill the rest of the population
    while len(new_population) < len(population):
        #Select parents
        parent1, _ = random.choice(sorted_pop[:len(population)//2])
        parent2, _ = random.choice(sorted_pop[:len(population)//2])
        child = crossover(parent1, parent2)
        mutate(child)
        new_population.append(child)

    return new_population



