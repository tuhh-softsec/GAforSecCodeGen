from abc import ABC, abstractmethod
import os
import time

class CodeGenerator(ABC):
    def __init__(self, model_name):
        self.model_name = model_name

    @abstractmethod
    def generate_code(self, prompt):
        pass

    def write_to_file(self, code, extension="txt"):
        timestamp = int(time.time())
        filename = f"{self.model_name}_{timestamp}.{extension}"

        with open(filename, "w") as file:
            file.write(code)

        print(f"Generated code written to {filename}")

    def is_executable(self, code):
        pass