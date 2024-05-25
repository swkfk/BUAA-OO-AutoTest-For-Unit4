import json
import base64
from typing import Dict
from pathlib import Path

CONFIG_FILE = "config"

def write_config(config: Dict[str, str]):
    jsonify = json.dumps(config)
    base64ed = base64.b64encode(jsonify.encode('utf-8', errors='ignore'))
    Path(CONFIG_FILE).write_bytes(base64ed)


def read_config() -> Dict[str, str] | None:
    path = Path(CONFIG_FILE)
    if not path.exists:
        return None
    try:
        base64ed = path.read_bytes()
        jsonify = base64.b64decode(base64ed).decode('utf-8')
        return json.loads(jsonify)
    except Exception as e:
        print(repr(e))
        return None
