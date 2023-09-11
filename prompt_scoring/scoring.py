import os
import sys
import json

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SAST_DIRECTORY = os.path.join(CURRENT_DIRECTORY, '..', 'SAST_integration')
sys.path.insert(0, SAST_DIRECTORY)

from bandit_scan import BanditScan

SEVERITY_SCORES = {'LOW': 2, 'MEDIUM': 4, 'HIGH': 6}
CONFIDENCE_MULTIPLIERS = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}

class PromptScoring:
    """Class to calculate the score of prompts based on the evaluation criteria."""
    
    def __init__(self):
        self.score = 0

    def bandit_score(self, prompt_id, bandit_scan):
        """Calculate the score of a given prompt based on the output from the bandit scan."""
        if not isinstance(bandit_scan, BanditScan):
            raise TypeError("Expected an object of type BanditScan")

        prompt_metrics = bandit_scan.bandit_output_dict.get(prompt_id, {})
        issues = prompt_metrics.get('issues', [])

        for issue in issues:
            temp_score = 0
            severity = issue.get('severity')
            confidence = issue.get('confidence')

            temp_score += SEVERITY_SCORES.get(severity, 0)
            temp_score *= CONFIDENCE_MULTIPLIERS.get(confidence, 1)
            self.score += temp_score

        return self.score
    
    def write_score_to_file(self, prompt_id, bandit_scan, score):
        """ write the scores of a given prompt variation to a file for future reference """
        if not isinstance(bandit_scan, BanditScan):
            raise TypeError("Expected an object of type BanditScan")
        
        # Retrieve the prompt data
        prompt_data = bandit_scan.bandit_output_dict.get(prompt_id, {})
        prompt_text = prompt_data.get("prompt")

        json_object = {
        "prompt_id": prompt_id,
        "prompt": prompt_text,
        "score": score
        }
        
        output_path = "../output/prompt_scores.json"
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(json_object)

        # Write the updated data back to the file
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)



if __name__ == "__main__":
    code_file = "../SAST_integration/test-file.py"
    scan = BanditScan()
    
    output = scan.run_bandit(code_file)
    prompt = "adsgfhdghs"
    prompt_id = '1_3'
    scan.process_scan_output(prompt_id, prompt, output)
    #print(scan.bandit_output_dict)
    
    scoring = PromptScoring()
    score = scoring.bandit_score(prompt_id, scan)
    print(score)
    scoring.write_score_to_file(prompt_id, scan, score)
