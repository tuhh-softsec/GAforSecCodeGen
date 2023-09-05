class CodingTaskTemplate:
    def __init__(self):
        self.pre_prompt = ""
        self.input_strings = []
        self.post_prompt = ""
    
    def read_input(self, input_file):
        # Read input coding tasks from file and return a list of inputs
        with open (input_file, 'r') as f:
            input_list = f.readlines()
            return input_list

    def pre_post_template(self, input_strings):
        # Generates a template combining pre_prompt and post_prompt.

        pre_post_input_prompts = []
        for string in input_strings:
            template_input_string = self.pre_prompt + " " + string + " " + self.post_prompt
            pre_post_input_prompts.append(template_input_string)
        return pre_post_input_prompts

    def pre_template(self, input_strings):
        # Generates a template using only the pre_prompt.
        pre_input_prompts = []
        for string in input_strings:
            template_input_string = self.pre_prompt + " " + string
            pre_input_prompts.append(template_input_string)
        return pre_input_prompts

