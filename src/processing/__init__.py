from os import getcwd, path, remove, mkdir
from queue import Queue
from oemer.ete import extract_inline

current_job = []
processing_queue = Queue(maxsize=-1)
failed_jobs = []

def process():
    while True:
        job_id, image_path = processing_queue.get()

        try:
            current_job.append(job_id)
            xml = extract_inline(image_path)

            if not path.exists(path.join(getcwd(), 'out')):
                mkdir(path.join(getcwd(), 'out'))

            with open(path.join(getcwd(), "out", f"{job_id}.musicxml"), "wb") as file:
                file.write(xml)

        except Exception as err:
            print(err)
            failed_jobs.append(job_id)
        finally:
            remove(image_path)
            current_job.remove(job_id)




