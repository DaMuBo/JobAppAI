"""
# TODO:
# was ist mit englischen Texten?
# Hab im moment nur deutsches NLP. Ist das eig ein Problem?
"""
import json
import os
import re
import sys

import spacy
from spacy.lang.de import German

sys.stdout.reconfigure(encoding="utf-8")

json_folders = [
    "labeling_job_1_output",
    "labeling_job_1_intermediate_output",
    "labeling_job_2_intermediate_output",
]

PROJECT_ROOT_DIR = "."
data_path = os.path.join(PROJECT_ROOT_DIR, "data")
models_path = os.path.join(PROJECT_ROOT_DIR, "models")
os.makedirs(data_path, exist_ok=True)
os.makedirs(models_path, exist_ok=True)


def load_data(file):
    """
    Daten in den speicher laden und zurückgeben
    """
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_data(file, data):
    """
    Daten speichern
    """
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def create_patterns(file, type):
    """
    Patterns erzeugen
    """
    data = load_data(file)
    patterns = []
    for item in data:
        pattern = {"label": type, "pattern": item}
        patterns.append(pattern)
    return patterns


def generate_ruler(patterns):
    """
    erzeuge regeln auf basis der regeln
    """
    nlp = German()
    entity_ruler = nlp.add_pipe("entity_ruler")
    entity_ruler.initialize(
        lambda: [], nlp=nlp, patterns=patterns
    )  # patterns entsprechen dann den Regeln
    ruler_path = os.path.join(models_path, "skill_ner")
    nlp.to_disk(ruler_path)


def get_all_json_files():
    """
    alle JSON files iteriren in dem ordner
    """
    all_json_files = []
    for folder in json_folders:
        json_folder_path = os.path.join(data_path, folder)
        for file in os.listdir(json_folder_path):
            filepath = os.path.join(json_folder_path, file)
            all_json_files.append(filepath)
    return all_json_files


def create_train_data_line(model, text):
    """
    beispieltext
    """
    doc = nlp(text)
    results = []
    entities = []
    for ent in doc.ents:
        entities.append((ent.start_char, ent.end_char, ent.label_))
    if len(entities) > 0:
        results = [str(text), {"entities": entities}]
    return results


def clean_text(text):
    """
    beispieltext
    """
    cleaned = re.sub(r"[\(\[].*?[\)\]]", " ", text)
    cleaned = re.sub(
        r"^\s+", "", cleaned, flags=re.UNICODE
    )  # Whitespace Begin
    cleaned = re.sub(
        r"\s+$", "", cleaned, flags=re.UNICODE
    )  # Whitespace Ending
    cleaned = (
        cleaned.replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(",", "")
        .replace("-", " ")
        .replace("/", " ")
        .replace("\n", " ")
    )
    cleaned.strip()
    return cleaned


patterns = create_patterns(r"data\skills.json", "SKILL")
print(patterns)
generate_ruler(patterns)

ruler_path = os.path.join(models_path, "skill_ner")
nlp = spacy.load(ruler_path)

TRAIN_DATA = []
files = get_all_json_files()

for file in files:
    file_content = load_data(file)
    text = file_content.get("source")
    text = text.replace("\t", "\n\n")
    segments = text.split("\n\n")
    hits = []
    for segment in segments:
        segment = clean_text(segment)
        results = create_train_data_line(nlp, segment)
        if results != []:
            TRAIN_DATA.append(results)

skill_label_train_data_path = os.path.join(
    data_path, "skill_label_train_data.json"
)
save_data(skill_label_train_data_path, TRAIN_DATA)
print(len(TRAIN_DATA))
