from abc import ABC, abstractmethod

class AbstractPromptAugmentation(ABC):

    created_prompts = []

    @abstractmethod
    def augment_prompt(self):
        pass

    def remove_duplicate_prompts(self, prompts):
        # finding unique prompts that has not been created yet
        unique_prompts = [prompt for prompt in prompts if prompt not in self.created_prompts]
        self.created_prompts.extend(unique_prompts)
        return unique_prompts
    
    def prompts_to_file(self, augmentation_technique):
        # write all the newly created prompts to a file
        filepath = "../output/" + augmentation_technique + "_prompts.txt"
        with open(filepath, 'w') as f:
            for prompt in self.created_prompts:
                f.write(prompt)
            
    


        




