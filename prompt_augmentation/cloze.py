from transformers import BertTokenizer, BertForMaskedLM
from abs_prompt_augmentation import AbstractPromptAugmentation
import torch
import random

class Cloze(AbstractPromptAugmentation):

    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForMaskedLM.from_pretrained(model_name)
        self.model.eval()
        self.mask_token = self.tokenizer.mask_token  # [MASK] token for BERT

    def augment_prompt(self, prompt):
        
        words = prompt.split()
        num_words_to_mask = random.randint(1, 3)
        
        for _ in range(num_words_to_mask):
            word_to_mask = random.choice(words)
            prompt = prompt.replace(word_to_mask, self.mask_token, 1)
        
        # print("masked prompt: " + prompt)
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
        mask_positions = torch.where(input_ids == self.tokenizer.mask_token_id)[1]

        with torch.no_grad():
            outputs = self.model(input_ids).logits
        
        for mask_position in mask_positions:
            predicted_token = torch.argmax(outputs[0, mask_position]).item()
            predicted_word = self.tokenizer.decode([predicted_token])
            prompt = prompt.replace(self.mask_token, predicted_word, 1)

        return prompt

if __name__ == "__main__":
    
    cloze = Cloze()
    original_prompt = "The quick brown fox jumps over the lazy dog."
    augmented_prompt = cloze.augment_prompt(original_prompt)
    print(f"Original Prompt: {original_prompt}")
    print(f"Augmented Prompt: {augmented_prompt}")
