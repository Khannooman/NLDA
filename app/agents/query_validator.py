"""
Query Validator Component for SQL Agent

This module provides functionality to validate SQL queries before execution.
It checks for syntax errors, common SQL mistakes, and suggests corrections
for invalid queries using LLMs.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional, Any, Tuple, Union
from app.llm.openai_manager import OpenAIManager
from app.prompts.llm_response_schema import LLMResponseSchemas
import re
import sqlparse

class QueryValidator:
    """
    A class for validating SQL queries before execution.
    """
    
    def __init__(self):
        """
        Initialize the QueryValidator.
    """
        self.llm = OpenAIManager()
        self._setup_prompts()
    
    def _setup_prompts(self) -> None:
        """Set up the prompts for query validation."""
        self.validation_prompt = ChatPromptTemplate.from_template("""
You are an expert SQL validator. Your task is to check a SQL query for errors and suggest corrections if needed.

Database Dialect: {dialect}

Schema Information:
{schema}

SQL Query to Validate:
{query}

Please analyze this query and check for the following issues:
1. Syntax errors
2. Missing or incorrect table or column names
3. Incorrect join conditions
4. Incorrect use of functions
5. Incorrect use of operators
6. Incorrect use of GROUP BY, ORDER BY, or HAVING clauses
7. Potential SQL injection vulnerabilities
8. Any other issues that would prevent the query from executing correctly
9. Return the SQL query wrapped in markdown code blocks like this.
```sql
    SELECT * FROM table
                                                                  

For each issue found, explain the problem and suggest a correction.
If the query is valid, state that it appears to be correct.

Validation Result:
""")
    
    def validate(self, query: str, schema: str, dialect: str) -> Dict[str, Any]:
        """
        Validate a SQL query.
        
        Args:
            query: SQL query to validate
            schema: Database schema information
            dialect: SQL dialect
            
        Returns:
            Dictionary containing validation results
        """
        
        # Use LLM for more comprehensive validation
        llm_validation = self._validate_with_llm(query, schema, dialect)
        
        # Determine overall validity
        is_valid = llm_validation.get("is_valid", False)
        
        # Combine all validation results
        return {
            "is_valid": is_valid,
            "llm_validation": llm_validation,
            "corrected_query": llm_validation.get("corrected_query") if not is_valid else query
        }
    
    def _validate_with_llm(self, query: str, schema: str, dialect: str) -> Dict[str, Any]:
        """
        Validate a SQL query using an LLM.
        
        Args:
            query: SQL query to validate
            schema: Database schema information
            dialect: SQL dialect
            
        Returns:
            Dictionary containing LLM validation results
        """
        input_values = {
            'dialect': dialect,
            'schema': schema,
            'query': query
        }
        
        response = self.llm.run_chain(
            prompt_template=self.validation_prompt,
            input_values=input_values,
            )
        response_text = response
        
        # Parse the response to determine if the query is valid
        is_valid = "appears to be correct" in response_text.lower() or "valid" in response_text.lower()
        
        # Extract corrected query if available
        corrected_query = None
        if not is_valid:
            # Try to extract corrected query using regex
            sql_pattern = r"```sql\n(.*?)```"
            sql_matches = re.findall(sql_pattern, response_text, re.DOTALL)
            
            if sql_matches:
                corrected_query = sql_matches[0].strip()
            else:
                # If no SQL code block found, try to extract based on common patterns
                correction_patterns = [
                    r"Corrected query:(.*?)(?:\n\n|$)",
                    r"Suggested correction:(.*?)(?:\n\n|$)",
                    r"Here's the corrected query:(.*?)(?:\n\n|$)"
                ]
                
                for pattern in correction_patterns:
                    matches = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
                    if matches:
                        corrected_query = matches.group(1).strip()
                        break
        
        # Extract issues from the response
        issues = []
        issue_pattern = r"\d+\.\s+(.*?)(?:\n\d+\.|\n\n|$)"
        issue_matches = re.findall(issue_pattern, response_text, re.DOTALL)
        
        if issue_matches:
            issues = [issue.strip() for issue in issue_matches]
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "corrected_query": corrected_query,
            "full_response": response_text
        }


