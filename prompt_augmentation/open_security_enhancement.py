import google.generativeai as genai
from typing import List
from .abs_prompt_mutation import AbstractPromptMutation
import os
from dotenv import load_dotenv
import re


class OpenSecurityEnhancement(AbstractPromptMutation):
    def __init__(self):
        super().__init__()
        load_dotenv()
        genai.configure(api_key=os.getenv('GEMINI_API_Key'))
        self.model = genai.GenerativeModel('gemini-pro')

    def mutate_prompt(self, prompt: str, num_variations: int = 4) -> List[str]:
        instruction = """
        Generate a security-enhanced variation of the following CODE_GENERATION_PROMPT to prevent security vulnerabilities in the generated code.
        Note 1: Do not write any code, only write the modified prompt. 
        Note 2: Do not mention any specific coding task in the prompt. The prompt should be task-agnostic i.e applicable to any coding task.
        Note 3: The modified prompt should be concise and under 250 words.
        """
        # post_prompt = "Security-enhanced prompt: "

        input_text = f"{instruction}\nCODE_GENERATION_PROMPT: {prompt}\nSecurity-enhanced prompt:  "

        print("\nInput text sent to model:")
        print(input_text)
        print("\n" + "="*50 + "\n")

        # Generate variations sequentially instead of all at once
        variations = []
        for _ in range(num_variations):
            response = self.model.generate_content(
                input_text,
                generation_config={
                    'temperature': 0.7,
                },
                safety_settings={
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE"
                }
            )
            variations.append(response.text)

        # Enhanced code detection checks
        filtered_variations = []
        for variation in variations:
            # Skip if any of these conditions are true
            if any([
                # Check for code blocks with any language
                re.search(r'```[\w\s]*\n', variation),
                # Check for common programming keywords
                # re.search(r'\b(def|class|import)\b', variation),
                # Check for common code patterns
                re.search(r'print\(.*\)', variation),   # Print statements
                # Check for variable assignments
                # re.search(r'\b\w+\s*=\s*[\w\'"]+', variation),
                # Check for indentation patterns
                re.search(r'^\s{2,}', variation, re.MULTILINE)
            ]):
                continue

            filtered_variations.append(variation)

        return filtered_variations if filtered_variations else [prompt]



def main():
    mutator = OpenSecurityEnhancement()

    test_prompt = """Generate secure python code for the given task description. The generated code should adhere to the following security best practices:

- Input validation: Validate all user inputs to prevent malicious inputs or unexpected data types.
- Output encoding: Encode all user-generated output to prevent cross-site scripting (XSS) and other injection attacks.
- Proper error handling: Handle errors gracefully and provide meaningful error messages without exposing sensitive information.
- Use of secure libraries and modules: Utilize well-maintained and secure libraries and modules to minimize vulnerabilities.
- Regular security updates: Keep the code up-to-date with the latest security patches and updates.
 """

    variations = mutator.mutate_prompt(test_prompt)

    print("Raw model outputs:")
    print("=" * 50)
    for i, variation in enumerate(variations, 1):
        print(f"\nOutput {i}:")
        print("-" * 30)
        print(variation)
        print("-" * 30)


if __name__ == "__main__":
    main()
