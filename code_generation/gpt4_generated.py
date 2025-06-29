from openai import OpenAI
import os
from time import sleep
import re
from config import config
from dotenv import load_dotenv

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class CodeGenerator():
    def __init__(self, model="gpt-4-1106-preview") -> None:
        self.model = model
        api_key = os.getenv('OPENAI_API_Key')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)

    def generate_code(self, query, query_id):
        user_query = self.wrap_request("user", query)
        msgs = [user_query]
        success = False
        while not success:
            try:
                response = self.client.chat.completions.create(  # Updated API call
                    model=self.model,
                    messages=msgs,
                    temperature=0.5,
                    top_p=0.1
                )
                success = True
                if "<span " in response:
                    print(f"Access error for prompt {query_id}... Waiting....")
                    sleep(65)
                    print("...continue...")

            except RateLimitError:
                print(f"RateLimitError for prompt {query_id},... Waiting....")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            except APIError:
                print(f"API error for prompt {query_id},... Waiting....")
                sleep(180)  # wait for 1 min to reset ratelimit
                print("...continue")
            except InternalServerError:
                print(f"Serveroverloaded for prompt {query_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            # except client.Timeout:
            #     print(f"Timeout for prompt {query_id}... waiting...")
            #     sleep(65)  # wait for 1 min to reset ratelimit
            #     print("...continue")
            except APIConnectionError:
                print(f"API connection error for prompt {query_id}... waiting...")
                sleep(65)  # wait for 1 min to reset ratelimit
                print("...continue")
            
        if response.choices:
            response_content = response.choices[0].message.content
            return response_content
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
        code_blocks = []
        code_blocks = re.findall(r'```python(.*?)```', code, re.DOTALL)
        # check if code_blocks is empty
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(code)

        #filename = f"{file_prefix}_{query_id}"
        filepath = os.path.join(output_dir, f"{query_id}.py")
        # filepath = f"{query_id}.py"
        print(filepath)
        try:
            f =  open(filepath, "w+", encoding='utf-8')
            # f.write(f"#Prompt: {prompt}\n")
            if valid_code and len(code) != 0:
                for block in code_blocks:
                    f.write(block.strip() + '\n\n')
                #f.write(f"{code}\n")  # Adding a newline to separate code snippets
            else:
                f.write("Invalid code")
            return filepath
        except Exception as e:
            print(f"Failed to write to file: {e}")
            
