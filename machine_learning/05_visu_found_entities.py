import json
import os
import re

import spacy
from spacy import displacy

PROJECT_ROOT_DIR = "."
visu_path = os.path.join(PROJECT_ROOT_DIR, "visu")
models_path = os.path.join(PROJECT_ROOT_DIR, "models")
data_path = os.path.join(PROJECT_ROOT_DIR, "data")
os.makedirs(visu_path, exist_ok=True)

skill_ner_model_path = os.path.join(models_path, "skill_ner_model")

json_folder = "labeling_job_1_output"
json_folder_path = os.path.join(data_path, json_folder)
dateien = os.listdir(json_folder_path)[:4]


def load_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


for file in dateien:

    filepath = os.path.join(json_folder_path, file)

    file_content = load_data(filepath)
    test = file_content.get("source")

    def clean_text(text):
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

    test = clean_text(test)

    nlp = spacy.load(skill_ner_model_path)
    doc = nlp(test)

    html = displacy.render(doc, style="ent")
    html_path = os.path.join(
        visu_path, file.replace(".json", "") + "_found_entities.html"
    )
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
