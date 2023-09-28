from transformers import MarianMTModel, MarianTokenizer
from . abs_prompt_augmentation import AbstractPromptAugmentation
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

MAX_LENGTH = 150 # length of the prompts

class BackTranslation(AbstractPromptAugmentation):

    def __init__(self):
        self.languages = ['fr', 'de', 'es', 'it']
        super().__init__()

    def augment_prompt(self, prompt, source_lang='en', target_lang='fr'):
        # Translate English to Target Language
        model_name_fwd = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
        model_fwd = MarianMTModel.from_pretrained(model_name_fwd)
        tokenizer_fwd = MarianTokenizer.from_pretrained(model_name_fwd)
        
        tokenized_text = tokenizer_fwd.encode(prompt, return_tensors="pt")
        translation = model_fwd.generate(tokenized_text, max_length = MAX_LENGTH)
        translated_text = tokenizer_fwd.decode(translation[0], skip_special_tokens=True)
        
        # Translate Target Language back to English
        model_name_bwd = f'Helsinki-NLP/opus-mt-{target_lang}-{source_lang}'
        model_bwd = MarianMTModel.from_pretrained(model_name_bwd)
        tokenizer_bwd = MarianTokenizer.from_pretrained(model_name_bwd)
        
        tokenized_text = tokenizer_bwd.encode(translated_text, return_tensors="pt")
        back_translation = model_bwd.generate(tokenized_text, max_length = MAX_LENGTH)
        back_translated_text = tokenizer_bwd.decode(back_translation[0], skip_special_tokens=True)
        
        return back_translated_text


if __name__ == "__main__":
    translate = BackTranslation()
    
    prompt = "The quick brown fox jumps over the lazy dog."
    #languages = ['fr', 'de', 'es', 'it']
    back_translations = {}

    for lang in translate.languages:
        back_translations[lang] = translate.augment_prompt(prompt, target_lang=lang)
        print(f"Back translated using {lang}: {back_translations[lang]}")

