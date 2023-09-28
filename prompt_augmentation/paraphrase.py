from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from . abs_prompt_augmentation import AbstractPromptAugmentation
import logging
from transformers import logging as transformers_logging
from transformers import GenerationMixin
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Disable logging
logging.basicConfig(level=logging.ERROR)
transformers_logging.set_verbosity_error()

class Paraphraser(AbstractPromptAugmentation):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("Vamsi/T5_Paraphrase_Paws")
        super().__init__()

    def augment_prompt(self, prompt, num_return_sequences=5, num_beams=5):
    # tokenize the text to be form of a list of token IDs
        inputs = self.tokenizer([prompt], truncation=True, padding="longest", return_tensors="pt")
        # generate the paraphrased sentences
        outputs = self.model.generate(
            **inputs,
            num_beams=num_beams,
            num_return_sequences=num_return_sequences,
        )
        # decode the generated sentences using the tokenizer to get them back to text
        
        return self.tokenizer.batch_decode(outputs, skip_special_tokens=True)


if __name__ == "__main__": 
    
    paraphrase = Paraphraser()
    prompt = "The quick brown fox jumps over the lazy dog."
    augmented_prompts = paraphrase.augment_prompt(prompt, num_beams=5, num_return_sequences=5)
    print(augmented_prompts)
    