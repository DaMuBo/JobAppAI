import spacy
import json
from spacy import displacy
import re
import os


PROJECT_ROOT_DIR = "."
visu_path = os.path.join(PROJECT_ROOT_DIR, "visu")
models_path = os.path.join(PROJECT_ROOT_DIR, "models")
os.makedirs(visu_path, exist_ok=True)

skill_ner_model_path = os.path.join(models_path, "skill_ner_model")


def load_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


file_content = load_data(
    r"data\labeling_job_1_output\labeling_job_1_output_0.json"
)
test = file_content.get("source")


def clean_text(text):
    cleaned = re.sub(r"[\(\[].*?[\)\]]", "", text)
    return cleaned


test = clean_text(test)

nlp = spacy.load(skill_ner_model_path)
doc = nlp(test)

html = displacy.render(doc, style="ent")
html_path = os.path.join(visu_path, "found_entities.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
