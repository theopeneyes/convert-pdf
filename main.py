from fastapi import FastAPI 
from google.cloud import storage 
from dotenv import load_dotenv
from typing import List, Dict 
from models import ConvertPDFOutputModel, ConvertPDFModel
from encoder import encode_image


import json 
import time 
import pdf2image as p2i
import os 


app = FastAPI(debug=True, title="project-astra")

load_dotenv(override=True) 

BUCKET_NAME: str = os.getenv("BUCKET_NAME")

gcs_client = storage.Client.from_service_account_json(".secrets/gcp_bucket.json")
bucket = gcs_client.bucket(BUCKET_NAME)

@app.post("/convert_pdf")
async def convert_pdf(pdf_file: ConvertPDFModel) -> ConvertPDFOutputModel: 
    """
    Input: {
        filename: name of the book 
        email_id: email id of the user used as a unique identified 
        uri: uri of the located file within uploaded_document
    }

    Function: 
    Disintegrates the pdf into a set of images to be stored within processed_image directory  
    """
    # accessing the file blob from the URI 
    start_time = time.time()
    pdf_blob = bucket.blob(pdf_file.uri)
    
    images: List[str] = p2i.convert_from_bytes(
        pdf_blob.open("rb").read(), 
        dpi=200, 
        fmt="jpg", 
    )

    # encoding the images and saving the encoded json to a directory  
    encoded_images: List[Dict[str, str]] = []
    for img in images: 
        encoded_image: str = encode_image(img) 
        image: Dict[str, str] = {
            "img_name": pdf_file.filename, 
            "img_b64": encoded_image, 
        }

        # formatting it as json 
        encoded_images.append(image)

    json_path: str = f"{pdf_file.email_id}/processed_image/{pdf_file.filename.split('.pdf')[0]}.json"
    json_blob = bucket.blob(json_path)
    
    with json_blob.open("w") as f: 
        f.write(
            json.dumps(encoded_images, ensure_ascii=True)
        )
    
    duration = time.time() - start_time

    return ConvertPDFOutputModel(
        filename=pdf_file.filename, 
        email_id=pdf_file.email_id, 
        uri=json_path, 
        time=duration,  
    ) 