import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

json_folders = [
    "labeling_job_1_output",
    "labeling_job_1_intermediate_output",
    "labeling_job_2_intermediate_output",
]

PROJECT_ROOT_DIR = "."
data_path = os.path.join(PROJECT_ROOT_DIR, "data")
os.makedirs(data_path, exist_ok=True)
skills_path = os.path.join(data_path, "skills.json")


def load_data(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def clean_skill(text):
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
    )
    cleaned.strip()
    return cleaned


def get_skills_from_json(file):
    data = load_data(file)

    text = data.get("source")
    labels = data.get("job-app-labeling").get("annotations").get("entities")

    for label in labels:
        skill = text[label.get("startOffset") : label.get("endOffset")]
        skill = clean_skill(skill)
        skills.append(skill)


skills = []
for folder in json_folders:
    json_folder_path = os.path.join(data_path, folder)
    for file in os.listdir(json_folder_path):
        try:  # nur wenn Skills da sind
            get_skills_from_json(os.path.join(json_folder_path, file))
        except Exception as e:
            pass
skills = list(set(skills))
skills.sort()

save_data(skills_path, skills)
