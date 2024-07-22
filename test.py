import configparser

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

# Example usage
file_path = './defaultConfig/config.ini'
parameters = read_specific_parameters(file_path)

print(f'fill_density = {parameters["fill_density"]}')
print(f'first_layer_speed = {parameters["first_layer_speed"]}')
print(f'first_layer_height = {parameters["first_layer_height"]}')
print(f'layer_height = {parameters["layer_height"]}')
print(f'perimeter_speed = {parameters["perimeter_speed"]}')
print(f'retract_speed = {parameters["retract_speed"]}')
print(f'retract_length = {parameters["retract_length"]}')
