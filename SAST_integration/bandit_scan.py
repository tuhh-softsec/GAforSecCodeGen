import subprocess
import json


class BanditScan():
    """ class to scan code files one at a time, process the results and write to a file. """

    def __init__(self):
        self.bandit_output_dict = {}

   
    def run_bandit(self, filepath):
        """ run bandit on a python code file and save the results to a json object """
        cmd = f"bandit -r -f json {filepath}"
        try:
            result = subprocess.run(
                cmd, shell=True, text=True, capture_output=True) # need to add check=True as well to the arugment. But later
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            return e.stderr
        
        
    def process_scan_output(self, prompt_id, prompt, bandit_output):
        """ add the prompt and the processed bandit json output to self.bandit_output_dict """
        # Convert string representation of JSON to Python dictionary (if necessary)
        if isinstance(bandit_output, str):
            bandit_output = json.loads(bandit_output)

        # Extract and count the issues
        issue_count = len(bandit_output["results"])     
        # Create a list to store the issues
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

        self.bandit_output_dict[prompt_id] = final_output




if __name__ == "__main__":
    # Replace with the path to the code file or directory you want to scan
    code_file = "test-file.py"
    scan = BanditScan()
    output = scan.run_bandit(code_file)
    prompt = "adsgfhdghs"
    prompt_id = "1_3"
    scan.process_scan_output(prompt_id, prompt, output)
    print(scan.bandit_output_dict)
    # if isinstance(output, dict):
    #     print(json.dumps(output, indent=4))
    # else:
    #     print(output)
