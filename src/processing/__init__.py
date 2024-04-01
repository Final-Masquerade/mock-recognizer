from os import getcwd, path, remove, mkdir, getenv
from queue import Queue
from oemer.ete import extract_inline
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


            # Success

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

            if save_on_process:
                if not path.exists(path.join(getcwd(), 'out')):
                    mkdir(path.join(getcwd(), 'out'))

                with open(path.join(getcwd(), "out", f"{job_id}.musicxml"), "wb") as file:
                    file.write(xml)

        except Exception as err:
            print(err)

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
            remove(image_path)
            current_job.remove(job_id)




