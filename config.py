import yaml
from pathlib import Path


class Config:
    def __init__(self, config_path="config.yaml"):
        # Get the directory containing this script
        current_dir = Path(__file__).parent

        # Load the config file
        with open(current_dir / config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    @property
    def final_optimal_prompts_file(self):
        return self.config['filepaths']['final_optimal_prompts_file']

    @property
    def reference_set_file(self):
        return self.config['filepaths']['reference_set_file']

    @property
    def reproductive_group_file(self):
        return self.config['filepaths']['reproductive_group_file']

    @property
    def prompts_with_scores_file(self):
        return self.config['filepaths']['prompts_with_scores_file']

    @property
    def gen_code_output_dir(self):
        return self.config['filepaths']['gen_code_output_dir']

    @property
    def bandit_output_dir(self):
        return self.config['filepaths']['bandit_output_dir']

    @property
    def test_set_file(self):
        return self.config['filepaths']['test_set_file']

    @property
    def test_output_file(self):
        return self.config['filepaths']['test_output_file']

    @property
    def test_prompts_file(self):
        return self.config['filepaths']['test_prompts_file']

    @property
    def evaluation_results_file(self):
        return self.config['filepaths']['evaluation_results_file']

    @property
    def temp_output_dir(self):
        return self.config['filepaths']['temp_output_dir']

    @property
    def optimization_iterations(self):
        return self.config['hyperparameters']['iterations']

    @property
    def optimization_k(self):
        return self.config['hyperparameters']['K']

    @property
    def mutated_prompts_file(self):
        return self.config['filepaths']['mutated_prompts_file']



config = Config()
