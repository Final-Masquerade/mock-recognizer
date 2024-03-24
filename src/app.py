from dotenv import load_dotenv
import os
from flask import Flask, request, send_file, jsonify, json
from multiprocessing import process
from threading import Thread
from util import Response, Status, decode_base64
from uuid import uuid4
from time import time
from mimetypes import guess_type, guess_extension
import base64
from typing import Final
from oemer.ete import extract_inline

load_dotenv()

cwd: Final[str] = os.getcwd()

failed_jobs = []
processing_queue = []

app = Flask(__name__)

@app.get("/")
def index():
    return "Stable."

@app.post("/api/recognize")
def recognize():
    body = request.get_json()
    if not ("file" in body):
        return Response({
            "message": "`file` field must be provided."
        }, status=400)

    data: str = body["file"]

    timestamp = round(time()*1000)
    job_id = f"{uuid4()}_{timestamp}"

    file_type = guess_type(data)[0]
    extension = guess_extension(file_type)

    if len(data.split(",")) > 1: data = data.split(",")[1]

    byte = base64.b64decode(f"{data}{'=' * (len(data) % 4)}")
    image_path = f"temp/{job_id}{extension}"

    if not os.path.exists(os.path.join(cwd, 'temp')):
        os.mkdir(os.path.join(cwd, 'temp'))
    
    if not os.path.exists(os.path.join(cwd, 'out')):
        os.mkdir(os.path.join(cwd, 'out'))

    with open(image_path, "wb") as file: 
        file.write(byte)

    def extract(input_path, output_path):
        i = input_path.split("/")[-1].split(".")[0]
        processing_queue.append(i)
        try: extract_inline(input_path, output_path)
        except:
            failed_jobs.append(i)
        finally: 
            os.remove(input_path)
            processing_queue.remove(i)

    recognition_thread = Thread(target=extract, args=(image_path, f"out/{job_id}.musicxml", ))
    recognition_thread.start()

    return Response({
        "file_type": file_type,
        "job_id": job_id,
        "status": Status.PROCESSING.value,
        "timestamp": timestamp,
    }, status=200)

@app.get("/api/queue")
def queue_info():
    return Response({
        "processing_queue": processing_queue,
        "failed_jobs": failed_jobs,
        "processing_queue_length": len(processing_queue),
        "failed_jobs_length": len(failed_jobs)
    })

@app.get("/api/tray/<jobId>")
def get_from_tray(jobId: str):
    return "The document."




if __name__ == "__main__":
    app.run(debug=True)
