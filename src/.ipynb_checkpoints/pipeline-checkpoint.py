import gc
import sys
import torch
from tqdm.notebook import tqdm

sys.path.append('src')
from utils import cleanup

def experiment(enhancer, jobs, temperatures=(1.0, 1.25, 1.5, 1.75, 2.0)):
    generation_kwargs_combinations = [{'do_sample':False, 'temperature':1.0}]
    for t in temperatures:
        generation_kwargs_combinations.append({'do_sample':True, 'temperature':t})
    
    with tqdm(total=len(generation_kwargs_combinations)*len(jobs)) as pbar:
        for generation_kwargs in generation_kwargs_combinations:
            for job in jobs:
                cv_path = os.path.join('data', 'CVs', f'{job}.txt')
                vacancy_dir = os.path.join('data', 'Vacancies', job)
                for vacancy in (f for f in  os.listdir(vacancy_dir) if f.endswith('.txt')):
                    vacancy_path = os.path.join(vacancy_dir, vacancy)
                    pbar.set_description(f'{vacancy_path} {generation_kwargs}')
                    enhancer.enhance(cv_path, vacancy_path, save_report=True, **generation_kwargs)
                    cleanup()
                pbar.update(1)