from os import getcwd, path, remove, mkdir, getenv
from queue import Queue
from oemer.ete import extract_inline
from util import musicxml_to_midi, midi_to_wav
import requests

current_job = []
processing_queue = Queue(maxsize=-1)

def process(save_on_process=False):
    gateway_host = getenv("GATEWAY_HOST")
    secret = getenv("RECOGNIZER_SECRET")

    while True:
        job_id, image_path, user_id = processing_queue.get()

        try:
            current_job.append(job_id)
            xml = extract_inline(image_path)

            if save_on_process:
                if not path.exists(path.join(getcwd(), 'out')):
                    mkdir(path.join(getcwd(), 'out'))

                if not path.exists(path.join(getcwd(), 'out', "musicxml")):
                    mkdir(path.join(getcwd(), 'out', "musicxml"))


                with open(path.join(getcwd(), "out", "musicxml", f"{job_id}.musicxml"), "wb") as file:
                    file.write(xml)

                musicxml_to_midi(job_id)


                soundfont = path.join(getcwd(), "src", "assets", "yamaha-c3-grand.sf2")
                midi_to_wav(job_id, soundfont)

            else:
                body = {
                    "user_id": user_id,
                    "job_id": job_id,
                    "xml": xml.decode("utf-8"),
                    "status": "SUCCESS"
                }

                requests.put(
                    f"{gateway_host}/user/updateSheetStatus",
                    headers={ "Authorization": secret },
                    json=body)

        except Exception as err:
            if save_on_process: print(err)
            else:
                body = {
                    "user_id": user_id,
                    "job_id": job_id,
                    "xml": "",
                    "status": "FAILED"
                }

                requests.put(
                    f"{gateway_host}/user/updateSheetStatus",
                    headers={ "Authorization": secret },
                    json=body)

        finally:
            if not save_on_process: remove(image_path)
            current_job.remove(job_id)
