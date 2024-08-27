import ujson as json
from ic_translate import *


def get_device_data():
    try:
        with open(device_save_file, 'r') as f:
            data = json.load(f)

        is_dirty = False
        if device_io_pw_name not in data:
            is_dirty = True
            data[device_io_pw_name] = default_device_pw

        if device_io_device_name not in data:
            is_dirty = True
            data[device_io_device_name] = default_device_name

        if is_dirty:
            save_device_data(data)

        return data
    except:
        print("Init save data...")
        # Initialize JSON
        data = {device_io_pw_name: default_device_pw,
                device_io_device_name: default_device_name}
        save_device_data(data)
        return data


def save_device_data(data):
    try:
        with open(device_save_file, 'w') as f:
            json.dump(data, f)
    except:
        print("Could not save data...")
