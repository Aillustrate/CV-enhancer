import os
import uuid

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.enhancer import CVEnhancer
from src.YandexIAMClient import YandexIAMClient, YandexTranslateClient

MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf" or 'mistralai/Mistral-7B-Instruct-v0.1'
YAOAUTH = ""
FOLDER_ID = ""

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, torch_dtype=torch.float16, low_cpu_mem_usage=True
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model.to("cuda")
enhancer = CVEnhancer(model, tokenizer, MODEL_NAME, max_len=1000)
YAIAMCLI = YandexIAMClient(YAOAUTH)
YATRANSLATE = YandexTranslateClient(FOLDER_ID, "ru")


def write_text_to_tmp_directory(text):
    unique_filename = str(uuid.uuid4()) + ".txt"
    file_path = os.path.join("/tmp", unique_filename)

    try:
        with open(file_path, "w") as file:
            file.write(text)
        return file_path

    except Exception as e:
        return f"Ошибка при записи файла: {e}"


def enh(
    CV: str,
    job: str,
):
    CV_path = write_text_to_tmp_directory(CV)
    job_path = write_text_to_tmp_directory(job)
    result = enhancer.enhance(cv_path=CV_path, job_path=job_path, save_report=False)
    result = YATRANSLATE.translate_text(result, YAIAMCLI.get_key())
    return result


demo = gr.Interface(
    fn=enh,
    inputs=[
        gr.Textbox(type="text", label="Резюме (скопируйте сырой текст)"),
        gr.Textbox(type="text", label="Описание вакансии (скопируйте сырой текст)"),
    ],
    outputs="text",
    title="CV-Job Match Demo",
    description="Введите резюме и описание вакансии для анализа.",
)

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0")
