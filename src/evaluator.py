import json
import os
import random

from IPython.display import clear_output

from src.utils import load_or_create_json


class Evaluator:
    def __init__(
            self,
            report_path="../evaluation/report.json",
            eval_dir="../evaluation/results",
            guidelines_path="../evaluation/guidelines.json",
            urls_path="../evaluation/urls.json",
            shuffle=True,
    ):
        self.annotator = input("Enter your name")
        self.report_path = report_path
        self.eval_path = os.path.join(eval_dir, f"{self.annotator}_eval.json")
        self.reports = load_or_create_json(self.report_path)
        self.evaluated = load_or_create_json(self.eval_path)
        self.CRITERIA = {
            "adequacy": (0, 5),
            "reliability": (0, 5),
            "usefulness": (0, 5),
            "honesty": (0, 5),
            "linguistic correctness": (0, 5),
            "coherence": (0, 5),
        }
        with open(guidelines_path) as jf:
            self.guidelines = json.load(jf)
        with open(urls_path) as jf:
            self.urls = json.load(jf)
        self.shuffle = shuffle

    def evaluate_report(self, report_id):
        report = self.reports[report_id]
        clear_output()

        print(f"CV: {report['cv']}\nVacancy:{report['job']}\n")

        guideline = self.guidelines.get(f"{report['cv']} & {report['job']}",
                                        "")
        cv_url = self.urls.get(report["cv"])
        vacancy_url = self.urls.get(report["job"])
        if cv_url:
            print(f"CV URL: {cv_url}")
        if vacancy_url:
            print(f"VACANCY URL: {vacancy_url}")

        if guideline:
            print(f"guidelines: {guideline}\n")

        print(report["output"])

        scores = {}
        for criterion, (min_score, max_score) in self.CRITERIA.items():
            score = int(input(f"{criterion} ({min_score}-{max_score})"))
            scores.update({criterion: score})
        self.evaluated.update({report_id: {**report, **scores}})
        with open(self.eval_path, "w") as jf:
            json.dump(self.evaluated, jf)

    def run(self):
        report_ids = list(self.reports.keys())
        if self.shuffle:
            random.shuffle(report_ids)
        for report_id in report_ids:
            if report_id not in self.evaluated:
                self.evaluate_report(report_id)
        print("All texts were evaluated. Thank you!")
