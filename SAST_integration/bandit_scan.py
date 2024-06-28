import subprocess
import json
import os
from config import config


class BanditScan():
    """ class to scan code files one at a time, process the results and write to a file. """

    def __init__(self):
        self.bandit_output_dict = {}

   
    def run_bandit(self, filepath, prompt_task_id):
        """ run bandit on a python code file and save the results to a json object """
        output_dir = config['filepaths']['bandit_output_dir']
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exist
        bandit_output_filepath = os.path.join(output_dir, f"{prompt_task_id}-test.json")
        print(f"Bandit scanning in progress for file {filepath}......")
        cmd = f"bandit -r -f json {filepath} -o {bandit_output_filepath}"
            
        try:
            result = subprocess.run(
                cmd, shell=True, text=True, capture_output=True) # need to add check=True as well to the arugment. But later
            with open(bandit_output_filepath, 'r') as file:
                return json.load(file)
            # return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Bandit scan failed: {e.stderr}")
            return None
        
        
    def process_scan_output(self, prompt_id, prompt, bandit_output):
        """ add the prompt and the processed bandit json output to self.bandit_output_dict """
        # Convert string representation of JSON to Python dictionary (if necessary)
        if isinstance(bandit_output, str):
            bandit_output = json.loads(bandit_output)

        # Extract and count the issues
        issue_count = len(bandit_output["results"])     
        # Create a list to store the issues

        if issue_count == 0:
            issues = []
        else: 
            issues = [
                {
                    "severity": issue["issue_severity"],
                    "confidence": issue["issue_confidence"],
                    "issue_cwe": issue["issue_cwe"]["id"],
                    "issue_text": issue["issue_text"]
                }
                for issue in bandit_output["results"]
            ]

        # Create the final JSON object
        final_output = {
            "prompt": prompt,
            "issue_count": issue_count,
            "issues": issues
        }
        return final_output
       
        

