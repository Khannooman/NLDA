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

For each issue found, explain the problem and suggest a correction.
If the query is valid, state that it appears to be correct.

Validation Result:
""")
    
    def _check_syntax(self, query: str) -> Tuple[bool, str]:
        """
        Check the syntax of a SQL query using sqlparse.
        
        Args:
            query: SQL query to check
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Remove any comments
            query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
            
            # Parse the query
            parsed = sqlparse.parse(query)
            
            # Check if the query was parsed successfully
            if not parsed:
                return False, "Failed to parse the query."
            
            # Check for basic structure
            stmt = parsed[0]
            
            # Check if it's a SELECT statement
            if stmt.get_type() == 'SELECT':
                # Check for FROM clause
                from_seen = False
                for token in stmt.tokens:
                    if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == 'FROM':
                        from_seen = True
                        break
                
                if not from_seen:
                    return False, "SELECT statement is missing FROM clause."
            
            return True, "Syntax appears to be valid."
        except Exception as e:
            return False, f"Syntax error: {str(e)}"
    
    def _check_common_mistakes(self, query: str, dialect: str) -> List[str]:
        """
        Check for common SQL mistakes based on the dialect.
        
        Args:
            query: SQL query to check
            dialect: SQL dialect
            
        Returns:
            List of potential issues
        """
        issues = []
        
        # Check for missing semicolon at the end
        if not query.strip().endswith(';'):
            issues.append("Query is missing a semicolon at the end.")
        
        # Check for incorrect use of single quotes vs double quotes
        if dialect.lower() in ['postgresql', 'postgres']:
            if '"' in query and not re.search(r'"[^"]*"', query):
                issues.append("Potential issue with double quotes. In PostgreSQL, double quotes are used for identifiers, not strings.")
        
        # Check for LIMIT without ORDER BY
        if re.search(r'LIMIT\s+\d+', query, re.IGNORECASE) and not re.search(r'ORDER\s+BY', query, re.IGNORECASE):
            issues.append("LIMIT is used without ORDER BY, which may lead to inconsistent results.")
        
        # Check for GROUP BY without aggregation
        if re.search(r'GROUP\s+BY', query, re.IGNORECASE):
            agg_functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']
            has_agg = any(re.search(rf'{func}\s*\(', query, re.IGNORECASE) for func in agg_functions)
            if not has_agg:
                issues.append("GROUP BY is used without any aggregation functions.")
        
        # Check for potential SQL injection
        if re.search(r"'.*\s+OR\s+.*'", query, re.IGNORECASE) or re.search(r"'.*\s+AND\s+.*'", query, re.IGNORECASE):
            issues.append("Potential SQL injection vulnerability detected.")
        
        # Check for incorrect NULL comparisons
        if re.search(r'=\s*NULL', query, re.IGNORECASE) or re.search(r'NULL\s*=', query, re.IGNORECASE):
            issues.append("Incorrect NULL comparison. Use IS NULL or IS NOT NULL instead of = NULL.")
        
        # Check for incorrect use of DISTINCT
        if re.search(r'SELECT\s+DISTINCT\s+.*,', query, re.IGNORECASE):
            issues.append("DISTINCT applies to all columns in the SELECT list, not just the first one.")
        
        return issues
    
    def _check_against_schema(self, query: str, schema: str) -> List[str]:
        """
        Check the query against the provided schema.
        
        Args:
            query: SQL query to check
            schema: Database schema information
            
        Returns:
            List of potential issues
        """
        issues = []
        
        # Extract table names from schema
        table_names = []
        for line in schema.split('\n'):
            if line.startswith('-- Table:'):
                table_name = line.replace('-- Table:', '').strip()
                table_names.append(table_name.lower())
        
        # Extract column names from schema
        column_info = {}
        current_table = None
        
        for line in schema.split('\n'):
            if line.startswith('-- Table:'):
                current_table = line.replace('-- Table:', '').strip().lower()
                column_info[current_table] = []
            elif current_table and 'CREATE TABLE' not in line and '(' in line and ')' not in line:
                # This is a column definition
                column_match = re.search(r'^\s*"?([a-zA-Z0-9_]+)"?\s+', line)
                if column_match:
                    column_name = column_match.group(1).lower()
                    column_info[current_table].append(column_name)
        
        # Extract tables used in the query
        query_lower = query.lower()
        tables_in_query = []
        
        # Look for table names after FROM and JOIN
        from_clauses = re.findall(r'from\s+([a-zA-Z0-9_]+)', query_lower)
        join_clauses = re.findall(r'join\s+([a-zA-Z0-9_]+)', query_lower)
        
        tables_in_query.extend(from_clauses)
        tables_in_query.extend(join_clauses)
        
        # Check if all tables in the query exist in the schema
        for table in tables_in_query:
            if table not in table_names:
                issues.append(f"Table '{table}' is not found in the schema.")
        
        # Extract columns used in the query
        columns_in_query = []
        
        # Look for columns in SELECT, WHERE, GROUP BY, ORDER BY, etc.
        # This is a simplified approach and may not catch all cases
        select_pattern = r'select\s+(.*?)\s+from'
        select_match = re.search(select_pattern, query_lower, re.DOTALL)
        
        if select_match:
            select_clause = select_match.group(1)
            # Handle * case
            if '*' not in select_clause:
                # Split by commas, handle functions
                parts = select_clause.split(',')
                for part in parts:
                    # Extract column name, handling aliases and functions
                    col_match = re.search(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', part)
                    if col_match:
                        table_alias = col_match.group(1)
                        column_name = col_match.group(2)
                        columns_in_query.append((table_alias, column_name))
                    else:
                        col_match = re.search(r'([a-zA-Z0-9_]+)', part)
                        if col_match:
                            column_name = col_match.group(1)
                            columns_in_query.append((None, column_name))
        
        # This is a simplified check and may not catch all issues
        # A more comprehensive check would require a full SQL parser
        
        return issues
    
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
        # Perform basic syntax check
        syntax_valid, syntax_error = self._check_syntax(query)
        
        # Check for common mistakes
        common_issues = self._check_common_mistakes(query, dialect)
        
        # Check against schema
        schema_issues = self._check_against_schema(query, schema)
        
        # Combine all issues
        all_issues = []
        if not syntax_valid:
            all_issues.append(syntax_error)
        all_issues.extend(common_issues)
        all_issues.extend(schema_issues)
        
        # Use LLM for more comprehensive validation
        llm_validation = self._validate_with_llm(query, schema, dialect)
        
        # Determine overall validity
        is_valid = syntax_valid and not common_issues and not schema_issues and llm_validation.get("is_valid", False)
        
        # Combine all validation results
        return {
            "is_valid": is_valid,
            "syntax_valid": syntax_valid,
            "syntax_error": syntax_error if not syntax_valid else None,
            "common_issues": common_issues,
            "schema_issues": schema_issues,
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
        prompt = self.validation_prompt.format(
            dialect=dialect,
            schema=schema,
            query=query
        )
        
        response = self.llm.run_chain(
            prompt_template=prompt,
            output_parser=LLMResponseSchemas.common_output_parser,
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


