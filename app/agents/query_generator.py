"""
Query Generator Component for SQL Agent

This module provides functionality to generate SQL queries based on natural language
questions and database schema information. It uses LangChain and LLMs to translate
natural language to SQL with appropriate prompting strategies.
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, List, Optional, Any
from app.llm.openai_manager import OpenAIManager
from app.prompts.llm_response_schema import LLMResponseSchemas
from app.prompts.sql_agent_prompt import Agentprompts
import re


class QueryGenerator:
    """
    A class for generating SQL queries from natural language questions
    """
    def __init__(self):
        """Initialize the QueryGenerator."""
        self.llm = OpenAIManager()
        self.prompts = Agentprompts()
        self._setup_prompts()

    def _setup_prompts(self) -> None:
        """set up the prompts for the query generation"""
        self.query_generation_prompt = ChatPromptTemplate.from_template(self.prompts.query_generation_prompt)
        self.few_shot_prompt = ChatPromptTemplate.from_template(self.prompts.few_shot_prompts)
        self.query_fixer_prompt = ChatPromptTemplate.from_template(self.prompts.query_fixer_prompt)    

    def _format_dialect_features(self, dialect_features: Dict[str, Any]) -> str:
        """
        Format dialect features for inclusion in the prompt.
        
        Args:
            dialect_features: Dictionary of dialect features
            
        Returns:
            Formatted dialect features as a string
        """
        formatted = f"Dialect: {dialect_features.get('name', 'unknown')}\n"
        
        formatted += "Supported Features:\n"
        formatted += f"- Window Functions: {dialect_features.get('supports_window_functions', False)}\n"
        formatted += f"- Common Table Expressions (CTEs): {dialect_features.get('supports_common_table_expressions', False)}\n"
        formatted += f"- JSON Support: {dialect_features.get('supports_json', False)}\n"
        formatted += f"- Array Support: {dialect_features.get('supports_arrays', False)}\n"
        
        if 'date_functions' in dialect_features and dialect_features['date_functions']:
            formatted += "Date Functions: " + ", ".join(dialect_features['date_functions']) + "\n"
        
        if 'string_functions' in dialect_features and dialect_features['string_functions']:
            formatted += "String Functions: " + ", ".join(dialect_features['string_functions']) + "\n"
        
        if 'aggregate_functions' in dialect_features and dialect_features['aggregate_functions']:
            formatted += "Aggregate Functions: " + ", ".join(dialect_features['aggregate_functions']) + "\n"
        
        return formatted
    

    def _get_example_queries(self, schema: str, dialect: str) -> Dict[str, str]:
        """
        Generate example queries for few-shot learning.
        
        Args:
            schema: Database schema information
            dialect: SQL dialect
            
        Returns:
            Dictionary of example questions and queries
        """
        # sophisticated way of generating or retrieving example queries
        
        # Extract table names from schema
        table_names = []
        for line in schema.split('\n'):
            if line.startswith('-- Table:'):
                table_name = line.replace('-- Table:', '').strip()
                table_names.append(table_name)
        
        # If no tables found, return generic examples
        if not table_names:
            return {
                "example_question_1": "Show me the top 5 customers by total order amount",
                "example_query_1": "SELECT c.customer_name, SUM(o.total_amount) as total_spent\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nGROUP BY c.customer_name\nORDER BY total_spent DESC\nLIMIT 5",
                
                "example_question_2": "How many orders were placed in each month of 2023?",
                "example_query_2": "SELECT EXTRACT(MONTH FROM order_date) as month, COUNT(*) as order_count\nFROM orders\nWHERE EXTRACT(YEAR FROM order_date) = 2023\nGROUP BY EXTRACT(MONTH FROM order_date)\nORDER BY month",
                
                "example_question_3": "Find all products that have never been ordered",
                "example_query_3": "SELECT p.product_name\nFROM products p\nLEFT JOIN order_items oi ON p.product_id = oi.product_id\nWHERE oi.order_id IS NULL"
            }
        
        # Use the actual table names to create more relevant examples
        examples = {}
        
        if len(table_names) >= 1:
            examples["example_question_1"] = f"Show me all records from the {table_names[0]} table"
            examples["example_query_1"] = f"SELECT *\nFROM {table_names[0]}\nLIMIT 10"
        else:
            examples["example_question_1"] = "Show me all records from the users table"
            examples["example_query_1"] = "SELECT *\nFROM users\nLIMIT 10"
        
        if len(table_names) >= 2:
            examples["example_question_2"] = f"Count the number of records in the {table_names[1]} table"
            examples["example_query_2"] = f"SELECT COUNT(*) as record_count\nFROM {table_names[1]}"
        else:
            examples["example_question_2"] = "Count the number of records in the orders table"
            examples["example_query_2"] = "SELECT COUNT(*) as record_count\nFROM orders"
        
        if len(table_names) >= 3:
            examples["example_question_3"] = f"Show me the relationship between {table_names[0]} and {table_names[2]}"
            examples["example_query_3"] = f"SELECT a.*, b.*\nFROM {table_names[0]} a\nJOIN {table_names[2]} b ON a.id = b.{table_names[0]}_id\nLIMIT 5"
        else:
            examples["example_question_3"] = "Show me the relationship between customers and orders"
            examples["example_query_3"] = "SELECT c.*, o.*\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nLIMIT 5"
        
        return examples
    
    def generate_query(self, question: str, schema: str, dialect: str, 
                      dialect_features: Optional[Dict[str, Any]] = None,
                      use_few_shot: bool = True) -> Dict[str, str]:
        """
        Generate a SQL query based on a natural language question.
        
        Args:
            question: Natural language question
            schema: Database schema information
            dialect: SQL dialect
            dialect_features: Optional dictionary of dialect-specific features
            use_few_shot: Whether to use few-shot learning
            
        Returns:
            Dictionary containing the generated query and explanation
        """
        if not dialect_features:
            dialect_features = {
                'name': dialect,
                'supports_window_functions': True,
                'supports_common_table_expressions': True,
                'supports_json': True,
                'supports_arrays': False,
                'date_functions': ['DATE', 'EXTRACT', 'CURRENT_DATE'],
                'string_functions': ['LOWER', 'UPPER', 'TRIM', 'SUBSTRING'],
                'aggregate_functions': ['SUM', 'AVG', 'MIN', 'MAX', 'COUNT']
            }
        
        formatted_dialect_features = self._format_dialect_features(dialect_features)
        
        if use_few_shot:
            examples = self._get_example_queries(schema, dialect)
            input_values = {
                'dialect': dialect,
                'schema': schema,
                'dialect_features': formatted_dialect_features,
                'question': question
            }
            input_values.update(examples)

            response = self.llm.run_chain(
                prompt_template=self.query_generation_prompt, 
                input_values=input_values
            )
        else:
            input_values = {
                'dialect': dialect,
                'schema': schema,
                'dialect_features': formatted_dialect_features,
                'question': question
            }

            response = self.llm.run_chain(
                prompt_template=self.query_generation_prompt, 
                input_values=input_values
            )
            # Extract the SQL query from the response
        response_text = response

        
        # Try to extract the SQL query using regex
        sql_pattern = r"```sql\n(.*?)```"
        sql_matches = re.findall(sql_pattern, response_text, re.DOTALL)
        
        if sql_matches:
            sql_query = sql_matches[0].strip()
        else:
            # If no SQL code block found, try to extract based on common patterns
            lines = response_text.split('\n')
            sql_lines = []
            capture = False
            
            for line in lines:
                if line.strip().upper().startswith("SELECT") or capture:
                    capture = True
                    sql_lines.append(line)
            
            if sql_lines:
                sql_query = '\n'.join(sql_lines)
            else:
                # If still no SQL found, use the entire response
                sql_query = response_text
        
        # Extract explanation
        explanation = response_text.replace(sql_query, "").strip()
        
        return {
            "query": sql_query,
            "explanation": explanation,
            "full_response": response_text
        }
    
    def query_fixer(self, question: str, schema: str, dialect: str,
                                previous_query: str, error: str,
                                dialect_features: Optional[Dict[str, Any]] = None,
                                use_few_shot: bool = False
                                ) -> Dict[str, Any]:
        """
        Generate a SQL query by fixing the error of previous_query.
        Args:
            question: Natural language question
            schema: Database schema information
            dialect: SQL dialect
            previous_query: Previously generated query
            error: Error of previously generated query
            dialect_features: Optional dictionary of dialect-specific features
            max_retries: Maximum number of retry attempts
        Returns:
            Dictionary containing the generated query, explanation, and retry information
        """
        if not dialect_features:
            dialect_features = {
                'name': dialect,
                'supports_window_functions': True,
                'supports_common_table_expressions': True,
                'supports_json': True,
                'supports_arrays': False,
                'date_functions': ['DATE', 'EXTRACT', 'CURRENT_DATE'],
                'string_functions': ['LOWER', 'UPPER', 'TRIM', 'SUBSTRING'],
                'aggregate_functions': ['SUM', 'AVG', 'MIN', 'MAX', 'COUNT']
            }
        
        formatted_dialect_features = self._format_dialect_features(dialect_features)
        
        if use_few_shot:
            examples = self._get_example_queries(schema, dialect)
            input_values = {
                'dialect': dialect,
                'schema': schema,
                'dialect_features': formatted_dialect_features,
                'question': question,
                'previous_query': previous_query,
                'error': error

            }
            input_values.update(examples)

            response = self.llm.run_chain(
                prompt_template=self.query_fixer_prompt, 
                input_values=input_values
            )
        else:
            input_values = {
                'dialect': dialect,
                'schema': schema,
                'dialect_features': formatted_dialect_features,
                'question': question
            }

            response = self.llm.run_chain(
                prompt_template=self.query_generation_prompt, 
                input_values=input_values
            )
            # Extract the SQL query from the response
        response_text = response

        
        # Try to extract the SQL query using regex
        sql_pattern = r"```sql\n(.*?)```"
        sql_matches = re.findall(sql_pattern, response_text, re.DOTALL)
        
        if sql_matches:
            sql_query = sql_matches[0].strip()
        else:
            # If no SQL code block found, try to extract based on common patterns
            lines = response_text.split('\n')
            sql_lines = []
            capture = False
            
            for line in lines:
                if line.strip().upper().startswith("SELECT") or capture:
                    capture = True
                    sql_lines.append(line)
            
            if sql_lines:
                sql_query = '\n'.join(sql_lines)
            else:
                # If still no SQL found, use the entire response
                sql_query = response_text
        
        # Extract explanation
        explanation = response_text.replace(sql_query, "").strip()
        
        return {
            "query": sql_query,
            "explanation": explanation,
            "full_response": response_text
        }

         
        
        