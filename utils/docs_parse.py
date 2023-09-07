
from .helpers import saveTemp
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.blob_loaders.file_system import FileSystemBlobLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders.parsers.audio import OpenAIWhisperParser
import os
from langchain.document_loaders import WebBaseLoader
from dotenv import load_dotenv
from langchain.document_loaders.image import UnstructuredImageLoader
from langchain.document_loaders import Docx2txtLoader
load_dotenv()

def parse_pdf(file):
    tmp_file = saveTemp(file)
    tmp_file_path = tmp_file["file"]
    loader = PyPDFLoader(tmp_file_path)
    chunks = loader.load_and_split()
    return chunks
def path_to_blob(file_path):
    with open(file_path, "rb") as file:
        blob = file.read()
    return blob
def parse_csv(file):
    tmp_file = saveTemp(file,"dataset/process/input/tables")
    tmp_file_path = tmp_file["file"]

    return tmp_file_path
def parse_pptx(file):
    tmp_file = saveTemp(file)
    tmp_file_path = tmp_file["file"]
    loader = UnstructuredPowerPointLoader(file_path=tmp_file_path)
    data = loader.load()
    return data
def parse_docx(file):
    tmp_file = saveTemp(file)
    tmp_file_path = tmp_file["file"]
    loader = Docx2txtLoader(file_path=tmp_file_path)
    data = loader.load_with_images(tmp_file["name"])
    
    
    return data
def parse_txt(file):
    tmp_file = saveTemp(file)
    tmp_file_path = tmp_file["file"]
    loader = TextLoader(file_path=tmp_file_path)
    data = loader.load()
    return data
def parse_image(file):
    tmp_file = saveTemp(file)
    tmp_file_path = tmp_file["file"]
    loader = UnstructuredImageLoader(file_path=tmp_file_path)
    data = loader.load()
    return data
    #metadata = ImageCaptionTool().run(tmp_file_path)
    #return tmp_file_path,metadata

def parse_audio(file):
    tmp_file = saveTemp(file)
    loader = GenericLoader(FileSystemBlobLoader(tmp_file),OpenAIWhisperParser(api_key=os.getenv("OPENAI_API_KEY")))
    data = loader.load()

    return data

def parse_links(file):
    loader = WebBaseLoader("https://www.brookings.edu/articles/how-artificial-intelligence-is-transforming-the-world/")
    data = loader.load()
    return data
