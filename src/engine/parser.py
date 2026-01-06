import os
import re
from typing import List
from .models import Requirement
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class RequirementParser:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # Check for API Key or use fallback mock logic if needed (handled in get_llm in agents.py ideally, 
        # but here we instantiate directly).
        if not api_key:
             api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
             print("WARNING: OPENAI_API_KEY not found. Parser might fail if not using fallback.")
             self.llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="sk-dummy")
        else:
             self.llm = ChatOpenAI(model="gpt-4-turbo", temperature=0, api_key=api_key)

    def parse(self, markdown_content: str) -> List[Requirement]:
        """Parses markdown content into structured Requirement objects using an LLM."""
        
        # Define the output parser
        parser = PydanticOutputParser(pydantic_object=Requirement)
        
        # We need a list of requirements, so we wrap the prompt to ask for a list
        # Note: PydanticOutputParser typically parses a single object. 
        # For a list, we can define a wrapper model or just ask for a list in JSON.
        # Simpler approach for this demo: Ask for a JSON list of objects matching the schema.
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Business Analyst. Extract all functional requirements and acceptance criteria from the provided markdown text. Return them as a JSON list where each item matches the following schema: {format_instructions}"),
            ("user", "Markdown Specification:\n{content}")
        ])
        
        # Wrapper model to parse a list
        from .models import RequirementList

        list_parser = PydanticOutputParser(pydantic_object=RequirementList)

        chain = prompt | self.llm | list_parser
        
        try:
            result = chain.invoke({
                "content": markdown_content,
                "format_instructions": list_parser.get_format_instructions()
            })
            return result.requirements
            
        except Exception as e:
            print(f"LLM Parsing failed: {e}. Falling back to Regex.")
            return self._regex_fallback(markdown_content)

    def _regex_fallback(self, markdown_content: str) -> List[Requirement]:
        """Fallback regex parser."""
        requirements = []
        pattern = re.compile(r'###\s+(AC-[\d\w]+):\s+(.*?)\n(.*?)(?=\n###|\Z)', re.DOTALL)
        matches = pattern.findall(markdown_content)
        for match in matches:
            req_id, title, body = match
            requirements.append(Requirement(
                id=req_id.strip(),
                title=title.strip(),
                description=body.strip()
            ))
        return requirements
