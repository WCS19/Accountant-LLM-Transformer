config_ini_location = '/Users/willemseethaler/config.ini' # Change filepath to wherever you have config.ini file stored

import configparser

config = configparser.ConfigParser()
config.read(config_ini_location)
openai_api_key = config['OpenAI']['API_KEY']