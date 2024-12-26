import google.generativeai as genai
from typing import List
from .abs_prompt_augmentation import AbstractPromptAugmentation
import os
from dotenv import load_dotenv


class SecurityPromptAugmenter(AbstractPromptAugmentation):
    def __init__(self):
        super().__init__()
        load_dotenv()
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    def augment_prompt(self, prompt: str, num_variations: int = 4) -> List[str]:
        instruction = """
        Input: Generate secure python code for the following task. 
        Output: Generate a secure python implementation of the given task description considering secure coding practices in mind.

        Input: Generate python code for the given task description that prevents security vulnerabilities.
        Output: Write secure python code for the given task description by eliminating the top 25 CWEs to make the generated code more secure.
        Like the above examples, generate security-enhanced variations of this code generation prompt to prevent security vulnerabilities.
        Input: """
        post_prompt = "Output: "

        input_text = f"{instruction} {prompt}\n{post_prompt} "

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
                }
            )
            variations.append(response.text)

        return variations


def main():
    augmenter = SecurityPromptAugmenter()

    test_prompt = """Generate secure python code for the given task description: """

    variations = augmenter.augment_prompt(test_prompt)

    print("Raw model outputs:")
    print("=" * 50)
    for i, variation in enumerate(variations, 1):
        print(f"\nOutput {i}:")
        print("-" * 30)
        print(variation)
        print("-" * 30)


if __name__ == "__main__":
    main()
