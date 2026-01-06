from typing import List
from .models import Requirement, TestCase
from .agents import RequirementsAnalyst, SoftwareTester, SuiteComposer

class TestArchitect:
    """
    Orchestrator that pipelines the Requirement -> Scenario -> Code flow.
    """
    def __init__(self, target_host: str = "http://localhost:8000", api_key: str = None):
        self.target_host = target_host
        self.analyst = RequirementsAnalyst(api_key=api_key)
        self.tester = SoftwareTester(target_host=target_host, api_key=api_key)
        self.composer = SuiteComposer(target_host=target_host, api_key=api_key)

    def generate_test_suite(self, requirements: List[Requirement]) -> str:
        """Generates a full pytest file content from requirements."""
        
        test_codes = []

        for req in requirements:
            # Step 1: Analyze (Req -> Scenario)
            scenario = self.analyst.analyze(req)
            
            # Step 2: Test (Scenario -> Code)
            test_case = self.tester.write_test(scenario)
            
            test_codes.append(test_case.code)

        # Step 3: Compose (Code Blocks -> Full File)
        # LLM assembles the file with imports
        full_suite_code = self.composer.compose_suite(test_codes)

        return full_suite_code