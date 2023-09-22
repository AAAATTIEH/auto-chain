import os
import json
import shutil
from utils.helpers import remove_dir
def delete_from_cache(id):
    path = f'dataset/cache/{id}'
    ids = load_metadata()
    if(id in ids):
        #Remove
        ids.remove(id)
        save_metadata(ids)
        try:
            shutil.rmtree(path)
        except Exception as e:
            pass 
        print("Data Removed")
    else:
        print("ID does not exist")
    return ids
def add_to_cache(id):
    cache_size =int(os.environ["CACHE_SIZE"])
    ## Load Metadata
    ids = load_metadata()
    ## Append ID
    if(id in ids):
        delete_from_cache(id)
    if(len(ids)<cache_size):
        ids.insert(0,id)
    else:
        removed_id = ids.pop()
        delete_from_cache(removed_id)
        ids.insert(0,id)
    ## Save Metadata
    save_metadata(ids)
    ## Copy Directory
    source_directory = 'dataset/process'
    destination_directory = f'dataset/cache/{id}'
    try:
        shutil.copytree(source_directory, destination_directory)
        print(f"Directory '{source_directory}' copied to '{destination_directory}' successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    print("Data Added")

def load_from_cache(id):
    ## Load Metadata
    ids = load_metadata()
    ## Append ID
    if(id in ids):
        remove_dir('dataset/process')
        destination_directory = 'dataset/process'
        source_directory = f'dataset/cache/{id}'
        try:
            shutil.copytree(source_directory, destination_directory)
            print(f"Directory '{source_directory}' copied to '{destination_directory}' successfully.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        return True
    else:
        return False
def load_metadata():
    ids = json.loads(open(f'dataset/cache/metadata.json', 'r').read())
    return ids
def save_metadata(ids):
    with open('dataset/cache/metadata.json', "w") as json_file:
        json.dump(ids, json_file, indent=4) 
