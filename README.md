# Axiom: Agentic Spec-to-Test Pipeline

Axiom is an intelligent pipeline that transforms natural language **specifications (Markdown)** into executable **Pytest suites** using LangChain agents.

## Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit UI
    participant Engine as Axiom Engine
    participant LLM as OpenAI GPT-4
    participant FS as File System
    participant TestRunner as Pytest Container
    participant Service as Mock Service API

    Note over User, UI: Phase 1: Specification & Generation
    User->>UI: Inputs Markdown Spec (ACs)
    User->>UI: Clicks "Generate Test Suite"
    UI->>Engine: Run Pipeline (Spec File)
    
    rect rgb(240, 248, 255)
        Note right of Engine: Agentic Orchestration
        Engine->>Engine: Parse Markdown -> [Requirements]
        
        loop For Each Requirement
            Engine->>LLM: RequirementsAnalyst: Analyze & Create Scenario
            LLM-->>Engine: JSON Test Scenario (Given/When/Then)
            
            Engine->>LLM: SoftwareTester: Write Pytest Code
            LLM-->>Engine: Python Code Block (httpx)
        end
        
        Engine->>LLM: SuiteComposer: Assemble File
        LLM-->>Engine: Complete test_suite.py
    end
    
    Engine->>FS: Write tests/generated_suite_test.py
    Engine-->>UI: Generation Complete
    
    Note over User, UI: Phase 2: Verification
    User->>UI: Clicks "Run Verification"
    UI->>TestRunner: Execute Pytest
    
    rect rgb(255, 240, 240)
        Note right of TestRunner: Test Execution
        TestRunner->>Service: GET /profile (Valid Token)
        Service-->>TestRunner: 200 OK (PASS)
        
        TestRunner->>Service: PUT /profile (Invalid Email)
        Service-->>TestRunner: 200 OK (FAIL! Expected 422)
        Note right of TestRunner: Bug Detected!
    end
    
    TestRunner-->>UI: Return Test Report
    UI->>User: Display Results (Passed/Failed)
```

## Codeflow
1.  **Specification**: Users write requirements in `docs/project_sample.md` (User Stories, ACs).
2.  **Parsing**: The **Engine** parses these into structured data.
3.  **Analysis (Agent 1)**: The `RequirementsAnalyst` breaks down ACs into logical **Test Scenarios** (Given/When/Then).
4.  **Test Generation (Agent 2)**: The `SoftwareTester` converts Scenarios into executable **Pytest** code.
5.  **Verification**: The generated suite runs against the **Target Service** (Mock Service).

## Directory Structure
- `docs/`: Specifications.
- `src/engine/`: The core logic (Agents, Parser, Orchestrator).
- `src/mock_service/`: A sample FastAPI app with an intentional bug.
- `tests/`: Output directory for generated tests.
- `main.py`: Streamlit UI for interactive usage.

## Setup & Running via Makefile

### Prerequisites
- Python 3.10+
- Docker (optional)
- OpenAI API Key

### Quick Start
1.  **Install Dependencies**:
    ```bash
    make install
    ```
2.  **Run All (Mock Service + Engine + Tests)**:
    ```bash
    make verify
    ```

### Docker Compose (Recommended)
This approach runs the Service, UI, and Tests in isolated containers on a shared network.

1.  **Start App**:
    ```bash
    docker-compose up -d axiom-ui
    ```
    Access UI at `http://localhost:8501`.

2.  **Run Tests in Container**:
    ```bash
    docker-compose run --rm axiom-tests
    ```

### Manual Running
- **UI**: `streamlit run main.py`
- **Engine**: `python src/engine/main.py docs/project_sample.md tests/generated_suite_test.py http://localhost:8000`

## Showcase
![Axiom Proof of Concept](poc.png)

Created with ❤️ with Gemini!