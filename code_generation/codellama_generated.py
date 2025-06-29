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
    

    def generate_code(self, query, query_id):
        
        url = 'http://localhost:11434/api/generate'
        success = False
        while not success:
            try:
                # sleep(20)
                payload = {
                    "model": "codellama",
                    "prompt": query,
                    "stream": False
                }
                response = requests.post(url, json=payload)
                response.raise_for_status()
                if response.status_code == 200:
                    success = True
                if "<span " in response:
                    print(f"Access error for prompt {query_id}... Waiting....")
                    sleep(65)
                    print("...continue...")

            except requests.exceptions.HTTPError:
                print(f"HTTPErros for prompt {query_id},... Waiting....")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except requests.exceptions.ConnectionError:
                print(f"Connection error for prompt {query_id},... Waiting....")
                sleep(180)  # wait for 1 min to reset ratelimit
                print("...continue")
            except requests.exceptions.RequestException:
                print(f"Request error for prompt {query_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except requests.exceptions.Timeout:
                print(f"Timeout for prompt {query_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            
        
        if response.json()["response"]:
            code = response.json()["response"]
            return code
        else:
            return None



    def wrap_request(self, type, msg):
        return {"role": type, "content": msg}
    

    def write_code_to_file(self, query_id, query, code):
        """ Writes a given code snippet and its associated prompt to a Python file. """
        print(f"Writing code for {query_id} to file")
        output_dir = config.gen_code_output_dir
        valid_code = any(len(line.split()) > 2 for line in code.split(
            '\n')) and len(code.split('\n')) > 3
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
        # success = False
        # generation_attempts = 0
        # while not success and generation_attempts <= 2:

        #     code_blocks = re.findall(r'```python(.*?)```', code, re.DOTALL)
        #     # check if code_blocks is empty
        #     if all(not block.strip() for block in code_blocks):
        #         # regenerate the code for the prompt if the code_block is empty
        #         code = self.generate_code(query=query, query_id=query_id)
        #         generation_attempts +=1
        #     else:
        #         success = True
        code_blocks = []
        code_blocks = re.findall(r'```(.*?)```', code, re.DOTALL)
        # check if code_blocks is empty
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(code)


        filepath = os.path.join(output_dir, f"{query_id}.py")
        # filepath = f"{query_id}.py"
        print(filepath)
        try:
            f =  open(filepath, "w+", encoding='utf-8')
            # f.write(f"#Prompt: {prompt}\n")
            if valid_code:
                for block in code_blocks:
                    f.write(block.strip() + '\n\n')
                #f.write(f"{code}\n")  # Adding a newline to separate code snippets
            else:
                f.write("Invalid code")
            return filepath
        except Exception as e:
            print(f"Failed to write to file: {e}")
            

