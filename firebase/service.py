import firebase_admin
from firebase_admin import credentials,firestore,storage
import os
import json
from utils.callback import CustomHandler
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase/_keys.json")
    app =firebase_admin.initialize_app(cred,{
        'storageBucket':'auto-chain-c13a0.appspot.com'
    })
db = firestore.client()
bucket = storage.bucket()


def upload(id):
    folder_path = "dataset/process"

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            
            remote_file_path = os.path.join(id, local_file_path[len(folder_path) + 1:])
            local_file_path = local_file_path.replace('\\','/')
            remote_file_path = remote_file_path.replace('\\','/')
            blob = bucket.blob(remote_file_path)
            blob.upload_from_filename(local_file_path)
            
            # Print the URL of the uploaded file
            print(f"Uploaded {remote_file_path}: {blob.public_url}")


def delete_folder( folder_path):
    # List all the blobs (files and subdirectories) in the specified folder
    blobs = bucket.list_blobs(prefix=folder_path)

    # Delete each blob (file) and subdirectory
    for blob in blobs:
        blob.delete()

    print(f"Folder '{folder_path}' and its contents have been deleted.")




def download(id):
    directory_path = id
    # List all files in the directory
    blobs = bucket.list_blobs(prefix=directory_path)
    # Specify the local directory where you want to save the downloaded files
    local_directory_path = "dataset/process"
    # Iterate over each file in the directory and download it
    
    for blob in blobs:
        print(blob)
        # Create the local file path by removing the directory path prefix
        local_file_path = local_directory_path + blob.name[len(directory_path):]
        local_folder_path = os.path.dirname(local_file_path)
        # Download the file to the specified local path
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)
        blob.download_to_filename(local_file_path)

        print(f"Downloaded: {local_file_path}")


def load_all():
    doc_ref = db.collection('data')
    documents = doc_ref.get()
    names = []
    for doc in documents:
        dict = doc.to_dict() 
        names.append({
            "name":dict["name"],
            "id":doc.id,
            "df":dict["df"],
            "index":dict["index"],
            "conversation":dict["conversation"]
        })
    return names
def load(id):
    #doc_ref = db.collection('data').document(id)
    #documents = doc_ref.get()
    #data = []
    #for doc in documents:
    #    data = doc.to_dict() 
    download(id)
    #return data      
def save(id,name,df,chain):
    if(id == "NEW"):
        doc_ref = db.collection('data').document()
    else:
        doc_ref = db.collection('data').document(id)
    conversation = {}
    for i in chain:
        conversation[i] = {
            "messages":chain[i]["messages"]
        }

    doc_ref.set({
        'name':name,
        'df':df,
        'index':CustomHandler.index,
        'conversation':conversation
    })
    if(id != "NEW"):
        delete_folder(doc_ref.id)
    upload(doc_ref.id)

        
