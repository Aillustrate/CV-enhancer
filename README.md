# 📄🖊️🤖 CV Enhancement with the use of LLM

> A service where AI can give you some hints on how to improve your resume

A prototype of an assistant for people who actively searching for job. The service accepts a pair of vacancy and CV and answers how well the CV matches the job description, whether it contains main sections (work experience, education, hard 
and soft skills), what information can be added and what can be improved. If the CV and the job description do not match at all (e.g. the user do not have basic skills required for that job, or is not experienced enough), the seervice will 
honestly tell about that and suggest what the user might need.

**Table of Contents**
- [Experiments](#experiments)
  - [Dataset](#dataset)
  - [Models](#models)
  - [Metrics](#metrics)
  - [Results](#results)
- [Structure of repository](#structure)

<a name="experiments"></a>
## Experiments

<a name="dataset"></a>
### Dataset
For our experiments, we parsed data from a job aggregator platform [hh.ru](https://hh.ru). Code for parsing is avalible [here](https://github.com/abdullinilgiz/LLMmatch).

### Models

We conducted experiments with 2 models: [Llama-2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf) и [Mistral](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1). We decided to try these models because both of them are open 
source and do not require payment to use. In addition, both of these models perform well in other tasks.

### Metrics
Due to the fact that the result that the LLMs give as back is the plain text, the is no other way to evaluate the performance of the models other than human effort. So we decided to develop your own assessment methodology and give each 
resulting text a score from 0 to 5 according to the following criteria:

- **Adequacy**: The model adequately assesses the suitability of the CV for the job description. If the CV does not suit the vacancy at all, it says so directly.
- **Reliability**: The model does not operate on information that is not in the job description/CV.
- **Usefulness**: The answer is not made up of obvious things. The model gives really valuable advices on the topics that the user can study or how to reformulate the CV for better match with the jobs description.
- **Honesty**: The model does not request the user to lie about their skills. However, it can offer some topics to study.
- **Linguistic correctness**: The answer does not contain spelling, grammatical or punctuation errors.
- **Coherence**: The answer is logically connected.

<a name="results"></a>
### Results
We condacted the experiments with both models changing the following generation parameters: do_sample and temperature.
- **do_sample** is a parameter that determines the sampling strategy (selection of the next token) during the generation. If do_sample=True, then generation method will use Sample Decoding and it gives the opportunity to play with the temperature parameter. If do_sample=False, then generation method will use greedy decoding.
- **temperature** is one of the key parameters of generation. The more temperature is, the model will use more "creativity", and the less temperature instruct model to be "less creative", but following your prompt stronger.

The results of evaluation the performance of the models were as follows:

| model     |	do_sample | temperature	| adequacy | reliability | usefulness |	honesty |	linguistic correctness | coherence |
| --------- |	--------- | ----------	| -------- | ----------- | ---------- |	------- |	---------------------- | --------- |
|Llama-2-7b |	False     | 1.00      	| 4.75     | 4.25        | 4.50       |	5.00    |	5.00                   | 4.00      |
|Llama-2-7b |	True      | 1.25      	| 2.83     | 4.33        | 2.50       |	5.00    |	5.00                   | 4.83      |
|Mistral-7B |	False     | 1.00      	| 3.67     | 4.33        | 3.33       |	4.67    |	5.00                   | 4.00      |
|Mistral-7B |	True      | 1.00      	| 3.50     | 4.00        | 4.00       |	5.00    |	5.00                   | 5.00      |



<a name="structure"></a>
### Structure of repository
