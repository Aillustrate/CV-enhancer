import gc
import json
import os
import re

import torch


def parse_matches(path):
    SEP = "*****"
    VACANCY_SEP = "***** vacansy"
    guidelines_RE = re.compile(r"Оценка \d/\d+:.*")
    URL_RE = re.compile(r"\(https://.*\)")
    with open(path) as f:
        lines = f.readlines()
    cv = []
    i = 0
    while not lines[i].startswith(SEP):
        cv.append(lines[i])
        i += 1
        if i == len(lines):
            break
    cv = "".join(cv)

    vacancies = []
    guidelines = []
    urls = []
    for line in lines[i:]:
        if line.startswith(VACANCY_SEP):
            vacancies.append([])
            url = URL_RE.findall(line)
            url.append("")
            urls.append(url[0])

        elif line.startswith(SEP):
            guidelines.append(guidelines_RE.findall(line))
        else:
            vacancies[-1].append(line)
    vacancies = ["".join(vacancy) for vacancy in vacancies]
    guidelines = [" ".join(guideline) for guideline in guidelines]
    assert len(vacancies) == len(guidelines)
    return cv, vacancies, guidelines, urls


def load_or_create_json(json_path):
    d = {}
    if os.path.exists(json_path):
        with open(json_path) as jf:
            d = json.load(jf)
    return d


def save_matches(
    job,
    matches_dir="../LLMmatch/data/matches",
    guidelines_path="../evaluation/guidelines.json",
    urls_path="../evaluation/urls.json",
):
    guideline_dict = load_or_create_json(guidelines_path)
    urls_dict = load_or_create_json(urls_path)
    matches_path = os.path.join(matches_dir, f"{job}.txt")
    cv, vacancies, guidelines, urls = parse_matches(matches_path)
    cv_path = os.path.join("..", "data", "CVs", f"{job}.txt")
    vacancy_dir = os.path.join("data", "Vacancies", job)
    os.makedirs(vacancy_dir, exist_ok=True)
    with open(cv_path, "w") as f:
        f.write(cv)
    for i, (vacancy, guideline, url) in enumerate(
            list(zip(vacancies, guidelines, urls)), start=1
    ):
        vacancy_path = os.path.join(vacancy_dir, f"{i}.txt")
        with open(vacancy_path, "w") as f:
            f.write(vacancy)
        guideline_dict.update({f"{cv_path} & {vacancy_path}": guideline})
        if url:
            urls_dict.update({vacancy_path: url})
    with open(guidelines_path, "w") as jf:
        json.dump(guideline_dict, jf, ensure_ascii=False)
    with open(urls_path, "w") as jf:
        json.dump(urls_dict, jf, ensure_ascii=False)


def cleanup():
    torch.cuda.empty_cache()
    gc.collect()
