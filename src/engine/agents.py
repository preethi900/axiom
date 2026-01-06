import os
import sys
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from .models import Requirement, TestScenario, TestCase

# Helper to get LLM (mock or real)
def get_llm(api_key: str = None):
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        # Fallback
        print("WARNING: OPENAI_API_KEY not found. Using dummy LLM.")
        return ChatOpenAI(model="gpt-3.5-turbo", api_key="sk-dummy") 
    return ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=api_key)

class RequirementsAnalyst:
    """
    Agent responsible for breaking down Requirements into logical Test Scenarios using an LLM.
    """
    def __init__(self, api_key: str = None):
        self.llm = get_llm(api_key)
        self.parser = PydanticOutputParser(pydantic_object=TestScenario)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert QA Analyst. Your job is to analyze requirements and break them down into detailed, logical test scenarios (Given/When/Then). You must anticipate edge cases and security vectors. Output must be valid JSON conforming to the schema."),
            ("user", "Requirement: {requirement}\n\n{format_instructions}")
        ])

    def analyze(self, req: Requirement) -> TestScenario:
        chain = self.prompt | self.llm | self.parser
        
        try:
            return chain.invoke({
                "requirement": req.json(),
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            # Fallback for demo stability if LLM fails (e.g. no auth)
            import traceback
            traceback.print_exc()
            print(f"LLM Call failed: {e}. Returning fallback scenario.", file=sys.stderr)
            return TestScenario(
                requirement_id=req.id,
                scenario_id=f"SCN-FALLBACK-{req.id}",
                description=f"Fallback scenario for {req.title}",
                steps=["Check logs", "Verify failure"],
                expected_result="Error",
                test_data={}
            )

class SoftwareTester:
    """
    Agent responsible for converting Test Scenarios into executable Pytest code using an LLM.
    """
    def __init__(self, target_host: str, api_key: str = None):
        self.target_host = target_host
        self.llm = get_llm(api_key)
        # For code generation, we just want the text, but let's structured output the whole TestCase object
        self.parser = PydanticOutputParser(pydantic_object=TestCase)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a Senior SDET. Write a high-quality, robust Pytest function for the following test scenario. The base URL is defined as `BASE_URL = '{target_host}'`. Use `httpx` for requests. Include assertion messages. \n\nIMPORTANT: When using f-strings for assertions, ensure you handle quotes correctly. If you access a dictionary with quotes inside an f-string (e.g., {{{{data['key']}}}}), you MUST use a different quote type for the outer string. Example: assert x == y, \"Error: {{{{data['key']}}}}\" (Double quotes outside). Output valid JSON."),
            ("user", "Scenario: {scenario}\n\n{format_instructions}")
        ])

    def write_test(self, scenario: TestScenario) -> TestCase:
        chain = self.prompt | self.llm | self.parser
        
        try:
            return chain.invoke({
                "scenario": scenario.json(),
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"LLM Call failed: {e}. Returning fallback test.", file=sys.stderr)
            return TestCase(
                requirement_id=scenario.requirement_id,
                scenario_id=scenario.scenario_id,
                test_function_name=f"test_{scenario.requirement_id.lower().replace('-', '_')}_fallback",
                code=f"def test_{scenario.requirement_id.lower().replace('-', '_')}_fallback():\n    import pytest\n    # Error: {str(e).replace(chr(39), '').replace(chr(34), '')}\n    pytest.skip('LLM generation failed check comments for details')",
                description="Fallback test due to LLM failure"
            )

class SuiteComposer:
    """
    Agent responsible for assembling the final test suite file using an LLM.
    """
    def __init__(self, target_host: str, api_key: str = None):
        self.target_host = target_host
        self.llm = get_llm(api_key)

    def compose_suite(self, test_codes: List[str]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a Senior Release Engineer. Assemble the following Python test functions into a complete, valid `pytest` file. Add all necessary imports (pytest, httpx, etc.). \n\nIMPORTANT: Do NOT define `BASE_URL`. It will be injected dynamically. Use `BASE_URL` in your code assuming it exists. Return ONLY the Python code. Do not include any conversational text."),
            ("user", "Test Functions:\n{functions}")
        ])
        
        chain = prompt | self.llm
        
        try:
            from langchain_core.output_parsers import StrOutputParser
            result = (chain | StrOutputParser()).invoke({
                "functions": "\n\n".join(test_codes)
            })
            
            # Robust extraction of code block
            cleaned_code = ""
            if "```python" in result:
                cleaned_code = result.split("```python")[1].split("```")[0].strip()
            elif "```" in result:
                cleaned_code = result.split("```")[1].split("```")[0].strip()
            else:
                 # Heuristic logic as before
                 lines = result.split("\n")
                 filtered_lines = []
                 started_code = False
                 for line in lines:
                    if line.strip().startswith("import ") or line.strip().startswith("from ") or line.strip().startswith("def "):
                        started_code = True
                    if started_code:
                        filtered_lines.append(line)
                 if filtered_lines:
                     cleaned_code = "\n".join(filtered_lines)

            # Prepend the dynamic BASE_URL logic
            # We use os.getenv to allow Docker override, defaulting to the host used during generation
            header = f"# Generated by Axiom Engine\nimport os\nimport pytest\nimport httpx\n\n# Dynamic Host Configuration\nBASE_URL = os.getenv('AXIOM_TARGET_HOST', '{self.target_host}')\n\n"
            
            # Remove any existing manual imports or BASE_URL definitions from the LLM output to avoid duplicates
            # (Simple string replacement might be risky, but let's assume LLM follows instructions)
            # Actually, the LLM was told to add imports. We should probably let it, or strip them. 
            # Safer: Let LLM do imports, but we FORCE the BASE_URL definition at the top.
            # We will ask LLM to NOT define BASE_URL constant in the new prompt, OR we just overwrite it? 
            # Easiest: The LLM output usually puts imports at top. 
            
            return header + cleaned_code
        except Exception as e:
            print(f"Suite Composition failed: {e}. Returning simple concatenation.")
            # Fallback
            header = f"# Generated by Axiom Engine (Fallback)\nimport pytest\nimport httpx\nimport os\nBASE_URL = os.getenv('AXIOM_TARGET_HOST', '{self.target_host}')\n"
            return header + "\n\n".join(test_codes)
