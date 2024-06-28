import requests
import json
import os
from time import sleep
import re
from config import config


class CodeGenerator():
    def __init__(self, api_key="", model="codellama") -> None:
        self.api_key = api_key
        self.model = model
    

    def generate_code(self, task_prompt, task_prompt_id):
        
        url = 'http://localhost:11434/api/generate'
        success = False
        while not success:
            try:
                # sleep(20)
                payload = {
                    "model": "codellama",
                    "prompt": task_prompt,
                    "stream": False
                }
                response = requests.post(url, json=payload)
                response.raise_for_status()
                if response.status_code == 200:
                    success = True
                if "<span " in response:
                    print(f"Access error for prompt {task_prompt_id}... Waiting....")
                    sleep(65)
                    print("...continue...")

            except requests.exceptions.HTTPError:
                print(f"HTTPErros for prompt {task_prompt_id},... Waiting....")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except requests.exceptions.ConnectionError:
                print(f"Connection error for prompt {task_prompt_id},... Waiting....")
                sleep(180)  # wait for 1 min to reset ratelimit
                print("...continue")
            except requests.exceptions.RequestException:
                print(f"Request error for prompt {task_prompt_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except requests.exceptions.Timeout:
                print(f"Timeout for prompt {task_prompt_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            
        
        if response.json()["response"]:
            code = response.json()["response"]
            return code
        else:
            return None



    def wrap_request(self, type, msg):
        return {"role": type, "content": msg}
    

    def write_code_to_file(self, prompt_task_id, task_prompt, code):
        """ Writes a given code snippet and its associated prompt to a Python file. """
        print(f"Writing code for {prompt_task_id} to file")
        output_dir = config['filepaths']['gen_code_output_dir']
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
        # success = False
        # generation_attempts = 0
        # while not success and generation_attempts <= 2:

        #     code_blocks = re.findall(r'```python(.*?)```', code, re.DOTALL)
        #     # check if code_blocks is empty
        #     if all(not block.strip() for block in code_blocks):
        #         # regenerate the code for the prompt if the code_block is empty
        #         code = self.generate_code(task_prompt=task_prompt, task_prompt_id=prompt_task_id)
        #         generation_attempts +=1
        #     else:
        #         success = True
        code_blocks = []
        code_blocks = re.findall(r'```(.*?)```', code, re.DOTALL)
        # check if code_blocks is empty
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(code)


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
            

