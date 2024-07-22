import configparser
import random
import numpy as np

# Function to read specific parameters from the .ini file
def read_specific_parameters(file_path):
    config = configparser.RawConfigParser()
    config.read(file_path)
    
    parameters = {
        'fill_density': float(config.get('DEFAULT', 'fill_density', fallback='20%').strip('%')) / 100,
        'first_layer_speed': config.getfloat('DEFAULT', 'first_layer_speed', fallback=30.0),
        'first_layer_height': config.getfloat('DEFAULT', 'first_layer_height', fallback=0.32),
        'layer_height': config.getfloat('DEFAULT', 'layer_height', fallback=0.28),
        'perimeter_speed': config.getfloat('DEFAULT', 'perimeter_speed', fallback=60.0),
        'solid_infill_speed': config.getfloat('DEFAULT', 'solid_infill_speed', fallback=60.0),
        'retract_speed': config.getfloat('DEFAULT', 'retract_speed', fallback=40.0),
        'retract_length': config.getfloat('DEFAULT', 'retract_length', fallback=2.0)
    }
    
    return parameters

# Function to write the optimized parameters to a new config file
def write_optimized_parameters(original_file_path, optimized_parameters):
    config = configparser.RawConfigParser()
    config.read(original_file_path)
    
    for param, value in optimized_parameters.items():
        if config.has_option('DEFAULT', param):
            config.set('DEFAULT', param, str(value))
        else:
            for section in config.sections():
                if config.has_option(section, param):
                    config.set(section, param, str(value))
                    break
    
    with open('optimized_config.ini', 'w') as configfile:
        config.write(configfile)
    
    # Remove the [DEFAULT] header from the optimized config file
    with open('optimized_config.ini', 'r') as file:
        lines = file.readlines()
    
    with open('optimized_config.ini', 'w') as file:
        for line in lines:
            if '[DEFAULT]' not in line:
                file.write(line)

# Custom function to read parameters from optimized_config.ini without section headers
def read_parameters_without_header(file_path):
    parameters = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.split('=')
                try:
                    parameters[key.strip()] = float(value.strip())
                except ValueError:
                    parameters[key.strip()] = value.strip()
    return parameters

# Ensure all necessary parameters are present in the optimized config
def ensure_parameters(optimized_parameters, initial_parameters):
    for key in initial_parameters:
        if key not in optimized_parameters:
            optimized_parameters[key] = initial_parameters[key]
    return optimized_parameters

# Constraints and parameter ranges
FILL_DENSITY_RANGE = (0.1, 0.3)
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
            'fill_density': round(random.uniform(*FILL_DENSITY_RANGE), 2),
            'first_layer_speed': round(random.uniform(*FIRST_LAYER_SPEED_RANGE)),
            'first_layer_height': round(random.uniform(*LAYER_HEIGHT_RANGE) / LAYER_HEIGHT_STEP) * LAYER_HEIGHT_STEP,
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
    first_layer_height = chromosome['first_layer_height']
    layer_height = chromosome['layer_height']
    perimeter_speed = chromosome['perimeter_speed']
    solid_infill_speed = chromosome['solid_infill_speed']
    retract_speed = chromosome['retract_speed']
    retract_length = chromosome['retract_length']
    
    # Simplified print time estimation (higher values for speed decrease the print time)
    print_time = (100 / max(fill_density, 1e-6)) + (100 / (first_layer_speed + 1)) + (100 / first_layer_height) + \
                 (100 / layer_height) + (100 / (perimeter_speed + 1)) + (100 / (solid_infill_speed + 1)) + \
                 (100 / (retract_speed + 1)) + (100 / retract_length)
    
    # Add rewards for higher speeds and layer height
    speed_reward = ((perimeter_speed + solid_infill_speed + retract_speed + first_layer_speed) / 4) * 2
    height_reward = (layer_height / 0.32) * 50  # Higher reward for higher layer height
    
    # Add penalties for constraint violations
    if not (0.1 <= fill_density <= 0.3):
        print_time += 1000
    if not (20 <= first_layer_speed <= 50):
        print_time += 1000
    if not (0.12 <= first_layer_height <= 0.32) or (first_layer_height % 0.04 != 0):
        print_time += 1000
    if not (0.12 <= layer_height <= 0.32) or (layer_height % 0.04 != 0):
        print_time += 1000
    if not (30 <= perimeter_speed <= 100):
        print_time += 1000
    if not (30 <= solid_infill_speed <= 100):
        print_time += 1000
    if not (30 <= retract_speed <= 100):
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
        chromosome[key] = round(random.uniform(*FILL_DENSITY_RANGE), 2)
    elif key == 'first_layer_speed':
        chromosome[key] = round(random.uniform(*FIRST_LAYER_SPEED_RANGE))
    elif key == 'first_layer_height' or key == 'layer_height':
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
def genetic_algorithm(pop_size, num_generations, num_parents, initial_fitness):
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
    
    best_fitness = fitness_function(best_chromosome)
    
    # If the new parameters are worse than the initial parameters, run the GA again
    if best_fitness < initial_fitness:
        print("Optimized parameters are worse than the initial parameters. Running the genetic algorithm again...")
        return genetic_algorithm(pop_size, num_generations, num_parents, initial_fitness)
    
    return best_chromosome

# Example usage
file_path = './defaultConfig/config.ini'

parameters = read_specific_parameters(file_path)

print(f'Initial Parameters:')
print(f'fill_density = {parameters["fill_density"] * 100}%')
print(f'first_layer_speed = {parameters["first_layer_speed"]}')
print(f'first_layer_height = {parameters["first_layer_height"]}')
print(f'layer_height = {parameters["layer_height"]}')
print(f'perimeter_speed = {parameters["perimeter_speed"]}')
print(f'solid_infill_speed = {parameters["solid_infill_speed"]}')
print(f'retract_speed = {parameters["retract_speed"]}')
print(f'retract_length = {parameters["retract_length"]}')

# Calculate the initial fitness
initial_fitness = fitness_function(parameters)

# Run the genetic algorithm
best_parameters = genetic_algorithm(pop_size=50, num_generations=100, num_parents=10, initial_fitness=initial_fitness)
print("Best Parameters:", best_parameters)

# Write the optimized parameters to a new config file
write_optimized_parameters(file_path, best_parameters)

# Read the optimized parameters without section headers
optimized_parameters = read_parameters_without_header('optimized_config.ini')
optimized_parameters = ensure_parameters(optimized_parameters, parameters)  # Ensure all parameters are present
optimized_fitness = fitness_function(optimized_parameters)

print(f'Optimized Parameters:')
print(f'fill_density = {optimized_parameters["fill_density"] * 100}%')
print(f'first_layer_speed = {optimized_parameters["first_layer_speed"]}')
print(f'first_layer_height = {optimized_parameters["first_layer_height"]}')
print(f'layer_height = {optimized_parameters["layer_height"]}')
print(f'perimeter_speed = {optimized_parameters["perimeter_speed"]}')
print(f'solid_infill_speed = {optimized_parameters["solid_infill_speed"]}')
print(f'retract_speed = {optimized_parameters["retract_speed"]}')
print(f'retract_length = {optimized_parameters["retract_length"]}')

print(f'Initial Fitness: {initial_fitness}')
print(f'Optimized Fitness: {optimized_fitness}')

# Ensure the optimized parameters are not worse than the initial parameters
if optimized_fitness < initial_fitness:
    print("Optimized parameters are worse than the initial parameters. Re-running the genetic algorithm.")
    best_parameters = genetic_algorithm(pop_size=50, num_generations=100, num_parents=10, initial_fitness=initial_fitness)
    write_optimized_parameters(file_path, best_parameters)
else:
    print("Optimized parameters are better than or equal to the initial parameters.")
