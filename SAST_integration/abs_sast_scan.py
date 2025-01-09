from abc import ABC, abstractmethod
import os
import time


class AbstractSastScan(ABC):

    @abstractmethod
    def run_sast(self, filepath, prompt_task_id):
        pass

    @abstractmethod
    def process_scan_output(self, query_id, prompt, bandit_output):
        pass
