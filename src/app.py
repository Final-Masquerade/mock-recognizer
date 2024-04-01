import os
import base64
import argparse
from dotenv import load_dotenv
from flask import Flask, request, send_file, jsonify, json
from threading import Thread
from util import Response, Status, decode_base64
from uuid import uuid4
from time import time
from mimetypes import guess_type, guess_extension
from typing import Final
from processing import processing_queue, current_job, process

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
    
    if not ("user_id" in body):
        return Response({
            "message": "`user_id` field must be provided."
        }, status=400)

    data: str = body["file"]
    user_id: str = body["user_id"]

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

    processing_queue.put((job_id, image_path, user_id))

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
        "processing_queue_length": processing_queue.qsize(),
    })



if __name__ == "__main__":
    parser = argparse.ArgumentParser("recognizer")
    parser.add_argument(
        "--save-on-process", 
        help="Saves the output as musicxml in the /out folder.", 
        action="store_true", 
        default=False
    )
    
    args = parser.parse_args()

    Thread(target=lambda: process(args.save_on_process)).start()
    app.run(debug=True)
