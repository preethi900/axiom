import sys
import os

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import langchain
# Enable verbose debug logging for LangChain
langchain.debug = True

from src.engine.parser import RequirementParser
from src.engine.architect import TestArchitect

def run_engine(spec_file_path: str, output_test_file: str, target_host: str, api_key: str = None):
    """
    Reads a spec file, generates a test suite, and writes it to disk.
    """
    print(f"Reading spec from {spec_file_path}...")
    with open(spec_file_path, "r") as f:
        content = f.read()

    parser = RequirementParser(api_key=api_key)
    requirements = parser.parse(content)
    print(f"Parsed {len(requirements)} requirements.")

    architect = TestArchitect(target_host=target_host, api_key=api_key)
    test_suite_code = architect.generate_test_suite(requirements)

    print(f"Writing test suite to {output_test_file}...")
    with open(output_test_file, "w") as f:
        f.write(test_suite_code)
    
    print("Done.")

if __name__ == "__main__":
    # For testing the engine independently
    # Usage: python src/engine/main.py <spec_path> <output_path> <host>
    if len(sys.argv) < 3:
        print("Usage: python main.py <spec_path> <output_path> [host]")
        sys.exit(1)
        
    spec = sys.argv[1]
    out = sys.argv[2]
    host = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"
    
    run_engine(spec, out, host)
