from abc import ABC, abstractmethod

class PromptAugmentation(ABC):

    def __init__(self):
        self.created_prompts = []

    @abstractmethod
    def augment_prompt(self):
        pass

    def remove_duplicate_prompts(self, prompts, prompt_file):
        unique_prompts = [prompt for prompt in prompts if prompt not in self.created_prompts]

        # Appending the truly unique prompts to self.created_prompts
        self.created_prompts.extend(unique_prompts)
        return unique_prompts
    


        




