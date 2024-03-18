import os
from dotenv import load_dotenv
from flask import Flask, request, send_file



load_dotenv() # os.getenv("SECRET_KEY")

app = Flask(__name__)

@app.get("/")
def index():
    return "Stable."

@app.post("/api/recognize")
def recognize():
    data = request.get_json()

    return "Recognized."
    # return send_file('/temp/0000-0000-0000-0000.musicxml')

@app.post("/api/harmonize")
def harmonize():
    data = request.get_json()

    return "Harmonized."