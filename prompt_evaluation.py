from dataclasses import dataclass
from typing import List, Optional
import logging
from pathlib import Path

from SAST_integration.bandit_scan import BanditScan
from prompt_scoring.bandit_score import PromptScoring
from query_preparation.preparation import CodingTaskTemplate
from code_generation.gemini_generated import CodeGenerator
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    prompt_id: int
    prompt: str
    score: int
    code_error: bool
    error_count: int


class PromptEvaluator:
    def __init__(self):
        self.bandit_scan = BanditScan()
        self.scoring = PromptScoring()
        self.code_generator = CodeGenerator()
        self.template = CodingTaskTemplate()

    def evaluate_single_task(self, prompt_id: int, task_template: str, template_number: int) -> Optional[int]:
        """Evaluate a single task template and return its score."""
        query_id = f"manual_{prompt_id}_{template_number}"

        # Generate code
        code = self.code_generator.generate_code(task_template, query_id)
        if not code:
            logger.warning(f"Code generation failed for {prompt_task_id}")
            return None

        # Write code to file
        code_file_path = self.code_generator.write_code_to_file(
            query_id, task_template, code)
        if not code_file_path:
            logger.warning("Invalid code file path")
            return None

        # Perform security scan
        scan_output = self.bandit_scan.run_sast(
            filepath=code_file_path, query_id=query_id)
        if not scan_output:
            logger.warning(f"Invalid scan output for file {code_file_path}")
            return None

        # Calculate score
        if len(scan_output["errors"]) != 0:
            return True, 10

        processed_output = self.bandit_scan.process_scan_output(
            query_id=prompt_id,
            prompt=task_template,
            bandit_output=scan_output
        )
        return False, self.scoring.bandit_score(prompt_id, processed_output)

    def calculate_score(self, prompt_id: int, prompt: str, test_set: List[str]) -> EvaluationResult:
        """Calculate the aggregate score for a prompt based on tasks in the test set."""
        prompt_score = 0
        code_error = True
        code_error_count = 0

        # Generate task templates
        test_task_queries = self.template.pre_template(prompt, test_set)

        # Evaluate each template
        for query_number, task_query in enumerate(test_task_queries, 1):
            code_error_status, score = self.evaluate_single_task(
                prompt_id, task_query, query_number)

            if score is not None:
                if isinstance(score, int):
                    prompt_score += score
                    if code_error_status == True:
                        code_error_count += 1
                    else:
                        code_error = False
                else:
                    logger.warning(
                        f"Prompt score is invalid for prompt: {prompt_id}")

        # Apply penalties
        if code_error_count >= 62:  # More than half contain errors
            prompt_score += 100
        if code_error:  # All tasks had syntactic errors
            prompt_score += 200

        return EvaluationResult(
            prompt_id=prompt_id,
            prompt=prompt,
            score=prompt_score,
            code_error=code_error,
            error_count=code_error_count
        )


def main():
    """Main execution function."""
    evaluator = PromptEvaluator()

    # Read test tasks
    try:
        with open(config.test_set_file, "r") as f:
            test_tasks = f.readlines()
    except FileNotFoundError:
        logger.error(f"Test set file not found: {config.test_set_file}")
        return

    # Read prompts to evaluate
    try:
        with open(config.test_prompts_file, "r") as f:
            prompts_to_evaluate = f.readlines()
    except FileNotFoundError:
        logger.error(f"Test prompts file not found: {
                     config.test_prompts_file}")
        return

    # Ensure output directory exists
    Path(config.evaluation_results_file).parent.mkdir(
        parents=True, exist_ok=True)

    # Evaluate prompts and write results
    with open(config.evaluation_results_file, "a+") as f:
        for idx, prompt in enumerate(prompts_to_evaluate, 1):
            result = evaluator.calculate_score(idx, prompt, test_tasks)
            f.write(f"Prompt: {result.prompt}, Score: {result.score} \n")
            logger.info(f"Evaluated prompt {idx}/{len(prompts_to_evaluate)}")


if __name__ == "__main__":
    main()
