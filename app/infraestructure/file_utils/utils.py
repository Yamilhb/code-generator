import os
import re
import json
import shutil
from dataclasses import asdict
from pathlib import Path
import subprocess

output_path = Path(__file__).resolve().parent.parent.parent / 'output'

def crea_archivo(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def crea_estructura(path, content):
    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    crea_archivo(path, content)

def extrae_json(text):

    # Define the regular expression pattern to match JSON blocks
    #pattern = r"\\\json(.*?)\\\"
    # pattern = r"json(.*?)\n"
    pattern = r"({[\s\S]*})"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    if matches:
        output = [json.loads(match.strip()) for match in matches]
    else:
        output = [json.loads(text)]
    try:
        return output
    except Exception:
        raise ValueError(f"Failed to parse: {text}")


def clean_output(file_path=output_path):
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
        os.makedirs(file_path)
    else:
        os.makedirs(file_path)

def save_code(estructura,output_path=output_path):
    # Si output_path existe y no está vacío, lo borra completamente
    if os.path.exists(output_path) and os.listdir(output_path):
        clean_output(output_path)
    elif not os.path.exists(output_path):
        os.makedirs(output_path)

    estructura = extrae_json(estructura)[0]
    for ruta, contenido in estructura.items():
        ruta = os.path.join(output_path,ruta.lstrip("/"))
        crea_estructura(ruta, contenido)

def linter_ruff(file_path=output_path):
    result = subprocess.run(['ruff', 'check', file_path], capture_output=True, text=True)
    return result.returncode, result.stdout


def snapshot_state(state):
    d = asdict(state)
    d.pop('history', None)
    return d.copy()  # Esto asegura que sea una copia independiente

def agent_history(history,file_path=output_path):
    with open(os.path.join(file_path,"history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
