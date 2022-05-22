import json
import os
import random
import re
import subprocess
import sys

import boto3
import spacy
from spacy.training import Example

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT_DIR = "."
data_path = os.path.join(PROJECT_ROOT_DIR, "data")
models_path = os.path.join(PROJECT_ROOT_DIR, "models")
os.makedirs(data_path, exist_ok=True)
os.makedirs(models_path, exist_ok=True)

skill_ner_model_path = os.path.join(models_path, "skill_ner_model")


def load_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def train_spacy(data, iterations):

    TRAIN_DATA = data
    nlp = spacy.blank("de")
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()

        for itn in range(iterations):
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:

                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)

                nlp.update([example], drop=0.2, sgd=optimizer, losses=losses)

            print(losses)
    return nlp


train_data_path = os.path.join(data_path, "skill_label_train_data.json")
TRAIN_DATA = load_data(train_data_path)

nlp = train_spacy(TRAIN_DATA, 30)
nlp.to_disk(skill_ner_model_path)


subprocess.run(
    [
        "aws",
        "s3",
        "cp",
        "--recursive",
        r"models\skill_ner_model",
        "s3://job-app-data-bucket/models/skill_ner_model/",
    ]
)


# Tests
file_content = load_data(
    r"data\labeling_job_1_output\labeling_job_1_output_0.json"
)
test = file_content.get("source")
print(test)


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
for ent in doc.ents:
    print(ent.text, ent.label_)
