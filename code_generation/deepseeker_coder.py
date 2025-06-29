from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
from time import sleep
import re

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class CodeGenerator():
    def __init__(self, model_name="deepseek-ai/deepseek-coder-33b-instruct") -> None:
        self.model_name = model_name
        # Initialize tokenizer and model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
            )
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise

    def generate_response(self, query, query_id):
        success = False
        while not success:
            try:
                # Prepare the input
                messages = [
                    {"role": "user", "content": query}
                ]
                inputs = self.tokenizer.apply_chat_template(
                    messages, add_generation_prompt=True, return_tensors="pt", padding=True).to(self.model.device)
                # tokenizer.eos_token_id is the id of <|EOT|> token
                outputs = self.model.generate(inputs, do_sample=True, temperature=0.2, top_k=50,
                                              top_p=0.95, num_return_sequences=1, eos_token_id=self.tokenizer.eos_token_id)
                response = self.tokenizer.decode(
                    outputs[0][len(inputs[0]):], skip_special_tokens=True)

                success = True
                return response

            except torch.cuda.OutOfMemoryError:
                print(f"GPU OOM for prompt {
                      query_id}... Clearing cache...")
                torch.cuda.empty_cache()
                sleep(5)
            except Exception as e:
                print(f"Error for prompt {query_id}: {e}... Waiting...")
                sleep(65)
                print("...continue")

        return None

    def wrap_request(self, type, msg):
        return {"role": type, "content": msg}

    def write_code_to_file(self, query_id, query, code):
        """ Writes a given code snippet and its associated prompt to a Python file. """
        print(f"Writing code for {query_id} to file")
        output_dir = "output/deep-seek"
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Extract code blocks
        code_blocks = []
        code_blocks = re.findall(r'```python(.*?)```', code, re.DOTALL)
        # If no code blocks found, use the entire response
        if all(not block.strip() for block in code_blocks):
            code_blocks.append(code)

        filename = f"{query_id}"
        filepath = os.path.join(output_dir, f"{filename}.py")
        print(filepath)

        try:
            with open(filepath, "w+", encoding='utf-8') as f:
                for block in code_blocks:
                    f.write(block.strip() + '\n\n')
            return filepath
        except Exception as e:
            print(f"Failed to write to file: {e}")
