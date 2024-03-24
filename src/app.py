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
from processing import processing_queue, current_job, failed_jobs, process

load_dotenv()

cwd: Final[str] = os.getcwd()
app = Flask(__name__)

@app.get("/")
def index():
    timestamp = round(time()*1000)
    return Response({
        "status": "stable",
        "timestamp": timestamp
    })

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
    if extension == None: extension = ".png"

    if len(data.split(",")) > 1: data = data.split(",")[1]

    byte = base64.b64decode(f"{data}{'=' * (len(data) % 4)}")
    image_path = f"temp/{job_id}{extension}"

    if not os.path.exists(os.path.join(cwd, 'temp')):
        os.mkdir(os.path.join(cwd, 'temp'))

    with open(image_path, "wb") as file: 
        file.write(byte)

    processing_queue.put((job_id, image_path))

    return Response({
        "file_type": file_type,
        "job_id": job_id,
        "status": Status.PROCESSING.value,
        "timestamp": timestamp,
    }, status=200)

@app.get("/api/queue")
def queue_info():
    return Response({
        "current_job": current_job[0] if len(current_job) > 0 else None,
        "processing_queue": list(map(lambda item: item[0], list(processing_queue.queue))),
        "failed_jobs": failed_jobs,
        "processing_queue_length": processing_queue.qsize(),
        "failed_jobs_length": len(failed_jobs)
    })

@app.get("/api/tray/<jobId>")
def get_from_tray(jobId: str):
    return "The document."




if __name__ == "__main__":
    Thread(target=process).start()
    app.run(debug=True)
