import openai
from . abs_code_generation import AbstractCodeGenerator
import os

class CodeGenerator(AbstractCodeGenerator):
    def __init__(self, api_key, model="gpt-3.5-turbo-instruct"):
        self.api_key = api_key
        self.model = model

    def generate_code(self, prompt, max_tokens=100, temperature=0.7):
        openai.api_key = self.api_key

        response = openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=None
        )

        if response.choices:
            return response.choices[0].text
        else:
            return None
    

    def write_code_to_file(self, prompt_task_id, prompt, code):
        """ Writes a given code snippet and its associated prompt to a Python file. """
        print(f"Writing code for {prompt_task_id} to file")
        output_dir = "../output"
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
        
        filepath = os.path.join(output_dir, f"{prompt_task_id}.py")
        try:
            with open(filepath, "a", encoding='utf-8') as f:
                f.write(f"#Prompt: {prompt}\n")
                f.write(f"{code}\n")  # Adding a newline to separate code snippets
            return filepath
        except Exception as e:
            print(f"Failed to write to file: {e}")
            


if __name__ == "__main__":
    api_key = ""  # Replace with your OpenAI API key
    code_generator = CodeGenerator(api_key)

    prompt = """
    Create a Python function that calculates the factorial of a given number.
    The function should take one argument, 'n', and return the factorial.
    """

    generated_code = code_generator.generate_code(prompt)
    print("Generated Python code:")
    print(generated_code)

    model_name = code_generator.model
    code_generator.write_to_file(generated_code, model_name)
