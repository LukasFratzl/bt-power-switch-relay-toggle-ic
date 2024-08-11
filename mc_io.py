import ujson as json
from mc_translate import *

def get_device_data():
    try:
        with open(device_save_file, 'r') as f:
            return json.load(f)
    except:
        print("Init save data...")
        data = {device_pw_name: default_device_pw} # Initialize JSON
        save_device_data(data)
        return data

def save_device_data(data):
    try:
        with open(device_save_file, 'w') as f:
            json.dump(data, f)
    except:
        print("Could not save data...")
