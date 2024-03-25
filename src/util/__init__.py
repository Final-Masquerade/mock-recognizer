import base64
import re
from flask import Response as r, json
from enum import Enum

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