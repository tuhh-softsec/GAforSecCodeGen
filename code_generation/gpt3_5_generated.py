import openai
from openai import OpenAI
import os
from time import sleep
import re
from config import config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class CodeGenerator():
    def __init__(self, model="gpt-3.5-turbo") -> None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_code(self, query, query_id):

        user_query = self.wrap_request("user", query)
        msgs = [user_query]
        success = False
        while not success:
            try:
                # sleep(20)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=msgs,
                    temperature=0.5,
                    top_p=0.1
                )
                success = True
                if "<span " in response:
                    print(f"Access error for prompt {
                          query_id}... Waiting....")
                    sleep(65)
                    print("...continue...")

            except openai.error.RateLimitError:
                print(f"RateLimitError for prompt {
                      query_id},... Waiting....")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except openai.error.APIError:
                print(f"API error for prompt {query_id},... Waiting....")
                sleep(180)  # wait for 1 min to reset ratelimit
                print("...continue")
            except openai.error.ServiceUnavailableError:
                print(f"Connection error for prompt {
                      query_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except openai.error.Timeout:
                print(f"Timeout for prompt {query_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")

        if response.choices:
            code = response.choices[0].message.content
            return code
        else:
            return None

    def wrap_request(self, type, msg):
        return {"role": type, "content": msg}

    def write_code_to_file(self, query_id, query, code):
        """ Writes a given code snippet and its associated prompt to a Python file. """
        print(f"Writing code for {query_id} to file")
        # output_dir = "output/code/evaluation/gps-1"
        output_dir = config.gen_code_output_dir
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
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
        code_blocks = re.findall(r'```python(.*?)```', code, re.DOTALL)
        # check if code_blocks is empty
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(code)

        filepath = os.path.join(output_dir, f"{query_id}-test.py")
        print(f"the code is written to: {filepath}")
        # filepath = f"{query_id}.py"
        print(filepath)
        try:
            f = open(filepath, "w+", encoding='utf-8')
            # f.write(f"#Prompt: {prompt}\n")
            for block in code_blocks:
                f.write(block.strip() + '\n\n')
            # f.write(f"{code}\n")  # Adding a newline to separate code snippets
            return filepath
        except Exception as e:
            print(f"Failed to write to file: {e}")
