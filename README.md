# GA-based Prompt Optimization for Secure Code Generation

This is the repository containing the code implementing the discrete prompt optimization pipeline presented in the paper "Discrete Prompt Optimization for Secure Python Code Generation"

This repository contain 6 main folders:

* [data](https://github.com/tuhh-softsec/GAforSecCodeGen/tree/main/data): contains the dataset containing the reference tasks used in the optimization phase and the test tasks used for the evaluation.
* [query_preparation](https://github.com/tuhh-softsec/GAforSecCodeGen/tree/main/query_preparation): simple component that prepares the query to be sent to the LLM by combining a code generation prompt and a coding task.
* [code_generation](https://github.com/tuhh-softsec/GAforSecCodeGen/tree/main/code_generation): includes implementations for generating code using Codellama 7b, GPT-3.5, GPT-4, Gemini and DeepSeek-Coder, and to process the LLM responses.
* [SAST_integration](https://github.com/tuhh-softsec/GAforSecCodeGen/tree/main/SAST_integration): includes script to run Bandit on a given code file. The generated output is processed accordingly for further use.
* [prompt_scoring](https://github.com/tuhh-softsec/GAforSecCodeGen/tree/main/prompt_scoring): implements the scoring function that calculates the score for each prompt based on the response from Bandit.
* [prompt_mutation](https://github.com/tuhh-softsec/GAforSecCodeGen/tree/main/prompt_mutation): implements generic prompt mutation techniques (back translation, paraphrase and cloze) and security-specific prompt mutation techniques (self-guided and feedback-guided).

The main optimization algorithm is implmented in the [prompt_optimization.py](https://github.com/tuhh-softsec/GAforSecCodeGen/blob/main/prompt_optimization.py) script. 
Install the necessary dependencies in the requirements.txt file and run the optimization script using the following command:

    python3 prompt_optimization.py

Due to the computational demands of the pipeline—which involves multiple small and large models for prompt mutation and code generation, it is not recommended to run it on a standard laptop. For efficient execution, we recommend using a machine with a dedicated GPU or an HPC environment.







