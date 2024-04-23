import base64
import re
from flask import Response as r, json
from enum import Enum
from music21 import converter, midi
from os import path, getcwd, mkdir, system, remove

def Response(data: dict, status: int = 200):
    return r(json.dumps(data), status=status)


def decode_base64(data, altchars=b'+/'):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'='* (4 - missing_padding)
    return base64.b64decode(data, altchars)

class Status(Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


def musicxml_to_midi(job_id):
    print("Building midi file...")

    if not path.exists(path.join(getcwd(), 'out', "midi")):
        mkdir(path.join(getcwd(), 'out', "midi"))
   
    if not path.exists(path.join(getcwd(), 'out', "pdf")):
        mkdir(path.join(getcwd(), 'out', "pdf"))

    xml_file = path.join(getcwd(), "out", "musicxml", f"{job_id}.musicxml")
    score = converter.parse(xml_file)

    midi_file = path.join(getcwd(), "out", "midi", f"{job_id}.mid")
    score.write("midi", midi_file)

    pdf_file = path.join(getcwd(), "out", "pdf", f"{job_id}.pdf")

    try:
        score.write('musicxml.pdf', pdf_file)
        remove(path.join(getcwd(), "out", "pdf", f"{job_id}.musicxml"))
    except:
        print("Error rendering pdf.")

def midi_to_wav(job_id, soundfont):
    print("Building wav file...")

    if not path.exists(path.join(getcwd(), 'out', "wav")):
        mkdir(path.join(getcwd(), 'out', "wav"))

    midi_file = path.join(getcwd(), "out", "midi", f"{job_id}.mid")
    wav_file = path.join(getcwd(), "out", "wav", f"{job_id}.wav")

    try:
        system(f'fluidsynth -ni {soundfont} {midi_file} -F {wav_file} -r 44100 >> /dev/null')
    except:
        print("Error rendering to wav.")

    
    
