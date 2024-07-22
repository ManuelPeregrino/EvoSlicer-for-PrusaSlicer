import configparser
import random
import numpy as np

# Function to read specific parameters from the .ini file
def read_specific_parameters(file_path):
    config = configparser.RawConfigParser()
    config.read(file_path)
    
    parameters = {
        'fill_density': None,
        'first_layer_speed': None,
        'first_layer_height': None,
        'layer_height': None,
        'perimeter_speed': None,
        'retract_speed': None,
        'retract_length': None
    }

    for param in parameters.keys():
        if config.has_option('DEFAULT', param):
            parameters[param] = config.get('DEFAULT', param)
        else:
            for section in config.sections():
                if config.has_option(section, param):
                    parameters[param] = config.get(section, param)
                    break
    
    return parameters

# Constraints and parameter ranges
FILL_DENSITY_RANGE = (0.1, 0.2)
FIRST_LAYER_SPEED_RANGE = (20, 50)
LAYER_HEIGHT_RANGE = (0.12, 0.32)
PERIMETER_SPEED_RANGE = (30, 100)
SOLID_INFILL_SPEED_RANGE = (30, 100)
RETRACT_SPEED_RANGE = (30, 100)
RETRACT_LENGTH_RANGE = (1, 5)
LAYER_HEIGHT_STEP = 0.04

# Generate initial population
def generate_initial_population(pop_size):
    population = []
    for _ in range(pop_size):
        chromosome = {
            'fill_density': round(random.uniform(*FILL_DENSITY_RANGE)),
            'first_layer_speed': round(random.uniform(*FIRST_LAYER_SPEED_RANGE)),
            'layer_height': round(random.uniform(*LAYER_HEIGHT_RANGE) / LAYER_HEIGHT_STEP) * LAYER_HEIGHT_STEP,
            'perimeter_speed': round(random.uniform(*PERIMETER_SPEED_RANGE)),
            'solid_infill_speed': round(random.uniform(*SOLID_INFILL_SPEED_RANGE)),
            'retract_speed': round(random.uniform(*RETRACT_SPEED_RANGE)),
            'retract_length': random.uniform(*RETRACT_LENGTH_RANGE)
        }
        population.append(chromosome)
    return population

# Fitness function
def fitness_function(chromosome):
    fill_density = chromosome['fill_density']
    first_layer_speed = chromosome['first_layer_speed']
    layer_height = chromosome['layer_height']
    perimeter_speed = chromosome['perimeter_speed']
    solid_infill_speed = chromosome['solid_infill_speed']
    retract_speed = chromosome['retract_speed']
    retract_length = chromosome['retract_length']
    
    # Simplified print time estimation (higher values for speed decrease the print time)
    print_time = (100 / fill_density) + (100 / (first_layer_speed + 1)) + (100 / layer_height) + \
                 (100 / (perimeter_speed + 1)) + (100 / (solid_infill_speed + 1)) + (100 / (retract_speed + 1)) + \
                 (100 / retract_length)
    
    # Add rewards for higher speeds and layer height
    speed_reward = (perimeter_speed + solid_infill_speed + retract_speed + first_layer_speed)
    height_reward = layer_height * 10
    
    # Add penalties for constraint violations
    if not (10 <= fill_density <= 30):
        print_time += 1000
    if not (0 <= first_layer_speed <= 40):
        print_time += 1000
    if not (0.12 <= layer_height <= 0.32) or (layer_height % 0.04 != 0):
        print_time += 1000
    if not (0 <= perimeter_speed <= 100):
        print_time += 1000
    if not (0 <= solid_infill_speed <= 100):
        print_time += 1000
    if not (0 <= retract_speed <= 100):
        print_time += 1000
    if not (1 <= retract_length <= 5):
        print_time += 1000

    return -print_time + speed_reward + height_reward  # We want to minimize print time, maximize speed, and maximize layer height

# Selection
def selection(population, fitnesses, num_parents):
    parents = np.random.choice(population, size=num_parents, replace=True, p=fitnesses/fitnesses.sum())
    return parents

# Crossover
def crossover(parent1, parent2):
    child = parent1.copy()
    for key in parent2:
        if random.random() < 0.5:
            child[key] = parent2[key]
    return child

# Mutation
def mutate(chromosome):
    key = random.choice(list(chromosome.keys()))
    if key == 'fill_density':
        chromosome[key] = round(random.uniform(*FILL_DENSITY_RANGE))
    elif key == 'first_layer_speed':
        chromosome[key] = round(random.uniform(*FIRST_LAYER_SPEED_RANGE))
    elif key == 'layer_height':
        chromosome[key] = round(random.uniform(*LAYER_HEIGHT_RANGE) / LAYER_HEIGHT_STEP) * LAYER_HEIGHT_STEP
    elif key == 'perimeter_speed':
        chromosome[key] = round(random.uniform(*PERIMETER_SPEED_RANGE))
    elif key == 'solid_infill_speed':
        chromosome[key] = round(random.uniform(*SOLID_INFILL_SPEED_RANGE))
    elif key == 'retract_speed':
        chromosome[key] = round(random.uniform(*RETRACT_SPEED_RANGE))
    elif key == 'retract_length':
        chromosome[key] = random.uniform(*RETRACT_LENGTH_RANGE)
    return chromosome

# Genetic Algorithm
def genetic_algorithm(pop_size, num_generations, num_parents):
    population = generate_initial_population(pop_size)
    
    for generation in range(num_generations):
        fitnesses = np.array([fitness_function(chromosome) for chromosome in population])
        
        print(f"Generation {generation} - Best Fitness: {fitnesses.max()}")
        
        parents = selection(population, fitnesses, num_parents)
        
        next_population = []
        for _ in range(pop_size):
            parent1, parent2 = random.sample(list(parents), 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_population.append(child)
        
        population = next_population

    fitnesses = np.array([fitness_function(chromosome) for chromosome in population])
    best_chromosome = population[np.argmax(fitnesses)]
    
    return best_chromosome

# Example usage
file_path = 'path_to_your_config_file.ini'
parameters = read_specific_parameters(file_path)

print(f'Initial Parameters:')
print(f'fill_density = {parameters["fill_density"]}')
print(f'first_layer_speed = {parameters["first_layer_speed"]}')
print(f'first_layer_height = {parameters["first_layer_height"]}')
print(f'layer_height = {parameters["layer_height"]}')
print(f'perimeter_speed = {parameters["perimeter_speed"]}')
print(f'retract_speed = {parameters["retract_speed"]}')
print(f'retract_length = {parameters["retract_length"]}')

best_parameters = genetic_algorithm(pop_size=50, num_generations=1000, num_parents=10)
print("Best Parameters:", best_parameters)
