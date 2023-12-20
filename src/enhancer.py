import json
import random
import re
import string

from src.utils import load_or_create_json


def make_id():
    chars = list(string.ascii_lowercase) + list(
        map(str, list(range(0, 9)) * 5))
    return "".join(random.sample(chars, 6))


class CVEnhancer:
    def __init__(
            self,
            model,
            tokenizer,
            model_name,
            system_prompt_path="prompts/system_prompt.txt",
            user_prompt_path="prompts/user_prompt.txt",
            report_path="evaluation/report.json",
            max_len=100000,
    ):
        self.ASSISTANT_MESSAGE_START = (
            "\nAssistant:Hello!"
            "As a career assiatant, I am glad to help you."
            "I will give you a detailed review of your CV"
            "and give some advice to help you improve it"
            "so that it will fit the job better."
        )
        self.RESPONSE_REGEXP = self.__get_response_regexp()
        self.TEMPLATE = (
            "<s>[INST] <<SYS>>"
            "{system_prompt} <</SYS>>"
            "{user_message} [/INST]{assistant_message}"
        )
        self.model = model
        self.tokenizer = tokenizer
        self.model_name = model_name
        with open(system_prompt_path) as f:
            self.system_prompt = f.read()
        with open(user_prompt_path) as f:
            self.user_prompt = f.read()
        self.report_path = report_path
        self.max_len = max_len

    def __get_response_regexp(self):
        assistant_message_start_regexp = self.ASSISTANT_MESSAGE_START.replace(
            "\n", ""
        ).replace(".", r"\.")
        text_regexp = r"[\S\s]*"
        return re.compile(
            f"(?<={assistant_message_start_regexp}){text_regexp}")

    def make_prompt(self, cv_path, job_path):
        with open(cv_path) as f:
            cv = f.read()
        with open(job_path) as f:
            job = f.read()
        user_prompt = self.user_prompt.format(cv=cv, job=job)
        return self.TEMPLATE.format(
            system_prompt=self.system_prompt,
            user_message=user_prompt,
            assistant_message=self.ASSISTANT_MESSAGE_START,
        )

    def generate_text(self, text, **generation_kwargs):
        input_ids = self.tokenizer(text, return_tensors="pt").input_ids.to(
            "cuda")
        output = self.tokenizer.decode(
            self.model.generate(
                input_ids,
                pad_token_id=self.tokenizer.eos_token_id,
                max_new_tokens=self.max_len,
                **generation_kwargs,
            )[0]
        )
        return output

    def process(self, llm_output):
        llm_output = llm_output.replace("</s>", "")
        return llm_output

    def extract(self, llm_output):
        llm_output = self.process(llm_output)
        matches = self.RESPONSE_REGEXP.findall(llm_output)
        if matches:
            return matches[0].lstrip()
        return ""

    def save_report(self, llm_output, cv_path, job_path, **generation_kwargs):
        reports = load_or_create_json(self.report_path)
        new_report = {
            "cv": cv_path,
            "job": job_path,
            "system_prompt": self.system_prompt,
            **generation_kwargs,
            "model": self.model_name,
            "output": llm_output,
        }
        report_id = make_id()
        reports.update({report_id: new_report})
        with open(self.report_path, "w") as jf:
            json.dump(reports, jf)

    def enhance(self, cv_path, job_path, save_report=True,
                **generation_kwargs):
        prompt = self.make_prompt(cv_path, job_path)
        llm_output = self.generate_text(prompt, **generation_kwargs)
        llm_output = self.extract(llm_output)
        if save_report:
            self.save_report(llm_output, cv_path, job_path,
                             **generation_kwargs)
        return llm_output
