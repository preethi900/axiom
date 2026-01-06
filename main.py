import streamlit as st
import os
import sys
import subprocess
import time
import requests
from src.engine.main import run_engine

# Configuration
SPEC_FILE = "docs/project_sample.md"
TEST_FILE = "tests/generated_suite_test.py"

st.set_page_config(page_title="Axiom | Agentic Spec-to-Test", layout="wide")

st.title("Axiom: Agentic Spec-to-Test Pipeline")
st.markdown("Transform natural language requirements into executable Pytest suites.")

# Sidebar - Service Control
st.sidebar.header("Environment")

# API Key Configuration
api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key here.")

# Target Host Configuration
target_host = st.sidebar.text_input("Target Service URL", value="http://localhost:8000")

if st.sidebar.button("Start Mock Service (Local)"):
    try:
        # Start uvicorn in a subprocess
        # We use sys.executable to ensure we use the same python environment
        cmd = [sys.executable, "-m", "uvicorn", "src.mock_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
        subprocess.Popen(cmd, cwd=os.getcwd())
        st.sidebar.success("Service started on port 8000")
        time.sleep(2) 
    except Exception as e:
        st.sidebar.error(f"Failed to start service: {e}")

if st.sidebar.button("Stop Mock Service"):
    subprocess.run(["pkill", "-f", "uvicorn"])
    st.sidebar.warning("Service stopped.")

# Main Area
col1, col2 = st.columns(2)

with col1:
    st.header("1. Specification")
    
    # Load Spec
    if os.path.exists(SPEC_FILE):
        with open(SPEC_FILE, "r") as f:
            spec_content = f.read()
    else:
        spec_content = "# New Spec"
        
    edited_spec = st.text_area("Edit Requirements (Markdown)", spec_content, height=500, key="spec_editor")
    
    if st.button("Save Specification"):
        with open(SPEC_FILE, "w") as f:
            f.write(edited_spec)
        st.success("Specification saved.")

with col2:
    st.header("2. Orchestration")
    
    st.markdown("### Individual Steps")
    
    # Step 2: Generate
    if st.button("Generate Test Suite"):
        with st.spinner("Parsing requirements & generating code..."):
            try:
                # Save latest spec
                with open(SPEC_FILE, "w") as f:
                    f.write(edited_spec)
                
                run_engine(SPEC_FILE, TEST_FILE, target_host, api_key=api_key)
                st.success("Test suite generated successfully!")
                
                # Show generated code snippet
                if os.path.exists(TEST_FILE):
                    with open(TEST_FILE, "r") as f:
                        code = f.read()
                    st.code(code, language="python")
                    
            except Exception as e:
                st.error(f"Engine failed: {e}")

    # Step 3: Run
    if st.button("Run Pytest"):
        if not os.path.exists(TEST_FILE):
            st.warning("No test file found. Generate it first.")
        else:
            with st.spinner("Running tests..."):
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", TEST_FILE, "-v"], 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    st.success("All tests PASSED")
                else:
                    st.error("Tests FAILED (Check Output)")
                
                st.subheader("Console Output")
                st.text(result.stdout)
                if result.stderr:
                    st.text(result.stderr)

    st.markdown("---")
    st.markdown("### Automate functionality")
    
    if st.button("RUN FULL VERIFICATION"):
        st.info("Starting Full Verification Pipeline...")
        progress_bar = st.progress(0)
        
        # 1. Start Service
        try:
            # Check if service is responsive
            try:
                requests.get(target_host + "/docs", timeout=1)
                st.write("✅ Service is already running.")
            except:
                st.write("🔄 Starting Mock Service...")
                cmd = [sys.executable, "-m", "uvicorn", "src.mock_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
                subprocess.Popen(cmd, cwd=os.getcwd())
                time.sleep(3)
                st.write("✅ Service started.")
        except Exception as e:
            st.error(f"Service Error: {e}")
        
        progress_bar.progress(33)
        
        # 2. Generate
        try:
            st.write("🔄 Generating Tests...")
            with open(SPEC_FILE, "w") as f:
                f.write(edited_spec)
            run_engine(SPEC_FILE, TEST_FILE, target_host, api_key=api_key)
            st.write("✅ Tests generated.")
        except Exception as e:
            st.error(f"Generation Error: {e}")
            st.stop()
            
        progress_bar.progress(66)
            
        # 3. Run
        try:
            st.write("🔄 Running Pytest...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", TEST_FILE, "-v"], 
                capture_output=True, 
                text=True
            )
            st.write("✅ Execution complete.")
            
            st.code(result.stdout)
            
            if result.returncode != 0:
                 st.warning("⚠️ Tests Failed (Expected for Intentional Bug)")
            else:
                 st.success("Tests Passed!")
                 
        except Exception as e:
            st.error(f"Execution Error: {e}")
            
        progress_bar.progress(100)
