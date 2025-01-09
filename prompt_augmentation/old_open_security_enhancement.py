from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List
import torch
from .abs_prompt_augmentation import AbstractPromptAugmentation


class OpenSecurityEnhancement(AbstractPromptAugmentation):
    def __init__(self, model_name: str = "google/gemma-2-2b"):
        """Initialize with FLAN-T5-Small model."""
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()

    def augment_prompt(self, prompt: str, num_variations: int = 4) -> List[str]:
        """Generate security-enhanced variations of this code generation prompt to prevent security vulnerabilities."""
        instruction = """Generate security-enhanced variations of this code generation prompt to prevent security vulnerabilities.
        
        Original prompt: """

        input_text = instruction + prompt

        inputs = self.tokenizer(input_text,
                                return_tensors="pt",
                                max_length=512,
                                truncation=True).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                num_return_sequences=num_variations,
                num_beams=num_variations,
                temperature=0.7,
                do_sample=True,
                no_repeat_ngram_size=2
            )

        variations = self.tokenizer.batch_decode(outputs,
                                                 skip_special_tokens=True)
        unique_variations = self.remove_duplicate_prompts(
            variations[:num_variations])
        return unique_variations


def main():
    augmenter = SecurityPromptAugmenter()

    test_prompt = "Generate secure python code for the following task description: "
    variations = augmenter.augment_prompt(test_prompt)

    print("Original prompt:", test_prompt)
    print("\nSecurity-enhanced variations:")
    for i, variation in enumerate(variations, 1):
        print(f"\n{i}. {variation}")

    augmenter.prompts_to_file("security")


if __name__ == "__main__":
    main()
