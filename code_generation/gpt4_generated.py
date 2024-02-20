import openai
import os
from time import sleep
import re

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class CodeGenerator():
    def __init__(self, api_key, model="gpt-4-1106-preview") -> None:
        self.api_key = api_key
        self.model = model
    

    def generate_response(self, task_prompt, task_prompt_id):
        
        user_task_prompt = self.wrap_request("user", task_prompt)
        msgs = [user_task_prompt]
        openai.api_key = self.api_key
        success = False
        while not success:
            try:
                # sleep(20)
                response = openai.ChatCompletion.create(
                    model = self.model,
                    messages = msgs,
                    temperature = 0.0,
                    top_p = 0.1
                )
                success = True
                if "<span " in response:
                    print(f"Access error for prompt {task_prompt_id}... Waiting....")
                    sleep(65)
                    print("...continue...")

            except openai.error.RateLimitError:
                print(f"RateLimitError for prompt {task_prompt_id},... Waiting....")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except openai.error.APIError:
                print(f"API error for prompt {task_prompt_id},... Waiting....")
                sleep(180)  # wait for 1 min to reset ratelimit
                print("...continue")
            except openai.error.ServiceUnavailableError:
                print(f"Serveroverloaded for prompt {task_prompt_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except openai.error.Timeout:
                print(f"Timeout for prompt {task_prompt_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
        
        if response.choices:
            response_content = response.choices[0]["message"]["content"]
            return response_content
        else:
            return None



    def wrap_request(self, type, msg):
        return {"role": type, "content": msg}
    

    def write_code_to_file(self, prompt_task_id, task_prompt, code):
        """ Writes a given code snippet and its associated prompt to a Python file. """
        print(f"Writing code for {prompt_task_id} to file")
        output_dir = "output/code/training/gps-1"
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
        code_blocks = []
        code_blocks = re.findall(r'```python(.*?)```', code, re.DOTALL)
        # check if code_blocks is empty
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(code)

        #filename = f"{file_prefix}_{prompt_task_id}"
        filepath = os.path.join(output_dir, f"{prompt_task_id}.py")
        # filepath = f"{prompt_task_id}.py"
        print(filepath)
        try:
            f =  open(filepath, "w+", encoding='utf-8')
            # f.write(f"#Prompt: {prompt}\n")
            for block in code_blocks:
                f.write(block.strip() + '\n\n')
            #f.write(f"{code}\n")  # Adding a newline to separate code snippets
            return filepath
        except Exception as e:
            print(f"Failed to write to file: {e}")
            


if __name__ == "__main__":
    api_key = ""  # Replace with your OpenAI API key
    code_generator = CodeGenerator(api_key, "gpt-3.5-turbo")

    pre_prompt = "Enter a Python code for the following task description, which is not safe:"

    task = "The code takes in a command line argument and converts it to an integer.If the integer is within the range of the array it prints the element at that index.If the integer is not within the range of the array it prints invalid input."

    prompt = f"{pre_prompt} {task}"

    generated_code = code_generator.generate_code(prompt, "1_3")
    print("Generated Python code:")
    print(generated_code)

    # model_name = code_generator.model
    code_generator.write_code_to_file("2_3", prompt, generated_code)

