"""
Query Generator Component for SQL Agent

This module provides functionality to generate SQL queries based on natural language
questions and database schema information. It uses LangChain and LLMs to translate
natural language to SQL with appropriate prompting strategies.
"""

from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional, Any, Union
from app.llm.openai_manager import OpenAIManager
from app.prompts.llm_response_schema import LLMResponseSchemas
import re
import json


class QueryGenerator:
    """
    A class for generating SQL queries from natural language questions
    """

    def __init__(self):
        """Initialize the QueryGenerator."""
        self.llm = OpenAIManager()
        self._setup_prompts()

    def _setup_prompts(self) -> None:
        """set up the prompts for the query generation"""
        self.query_generation_prompt = ChatPromptTemplate.from_template("""
You are an expert SQL query generator. Your task is to convert natural language questions into correct SQL queries.

Database Dialect: {dialect}

Schema Information:
{schema}

Dialect-Specific Features:
{dialect_features}

User Question: {question}

Generate a SQL query that answers the user's question. Follow these guidelines:
1. Use only tables and columns that exist in the schema
2. Use appropriate joins based on the foreign key relationships
3. Use appropriate SQL syntax for the specified dialect
4. Include appropriate filtering, grouping, and sorting as needed
5. Use appropriate functions for the specified dialect
6. Do not use any tables or columns that are not in the schema
7. Do not use any functions that are not supported by the dialect
8. Ensure the query is syntactically correct
9. Explain your reasoning step by step
10. Return the SQL query wrapped in markdown code blocks like this.
```sql
    SELECT * FROM table

SQL Query:
""")

        self.few_shot_prompt = ChatPromptTemplate.from_template("""
You are an expert SQL query generator. Your task is to convert natural language questions into correct SQL quries.
Database Dialect: {dialect}

Schema Information:
{schema}

Dialect-Specific Features:
{dialect_features}

Here are some examples of natural language questions and their corresponding SQL queries:
Example 1:
Question: {example_question_1}
SQL Query: {example_query_1}

Example 2:
Question: {example_question_2}
SQL Query: {example_query_2}

Example 3:
Question: {example_question_3}
SQL Query: {example_query_3}

Now, generate a SQL query for the following question:
User Question: {question}

Generate a SQL query that answers the user's question. Follow these guidelines:
1. Use only tables and columns that exist in the schema
2. Use appropriate joins based on the foreign key relationships
3. Use appropriate SQL syntax for the specified dialect
4. Include appropriate filtering, grouping, and sorting as needed
5. Use appropriate functions for the specified dialect
6. Do not use any tables or columns that are not in the schema
7. Do not use any functions that are not supported by the dialect
8. Ensure the query is syntactically correct
9. Explain your reasoning step by step
10. Return the SQL query wrapped in markdown code blocks like this.
```sql
    SELECT * FROM table                                                               
                                                                                                                             

SQL Query:                                                                
""")
        

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

    def generate_query_with_retry(self, question: str, schema: str, dialect: str,
                                 dialect_features: Optional[Dict[str, Any]] = None,
                                 max_retries: int = 3) -> Dict[str, Any]:
        """
        Generate a SQL query with retry logic for handling errors.
        
        Args:
            question: Natural language question
            schema: Database schema information
            dialect: SQL dialect
            dialect_features: Optional dictionary of dialect-specific features
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing the generated query, explanation, and retry information
        """

        result = self.generate_query(question, schema, dialect, dialect_features, use_few_shot=True)
        retries = 0
        retry_history = [result]
        
        while retries < max_retries:
            # Check if the query contains any obvious errors
            query = result["query"]
            has_error = False
            
            # Check for common SQL syntax errors
            if "ERROR" in query.upper() or "SYNTAX ERROR" in query.upper():
                has_error = True
            
            # Check for incomplete queries
            if not query.strip().endswith(";") and ";" not in query:
                if not re.search(r"SELECT.*FROM", query, re.IGNORECASE | re.DOTALL):
                    has_error = True
            
            if not has_error:
                break
            
            # Retry with more specific instructions
            retry_prompt = f"""
I need to fix the following SQL query that has errors:

{query}

The query should answer this question: {question}

For the following database schema:
{schema}

Using the {dialect} SQL dialect.

Please provide a corrected SQL query that:
1. Uses proper syntax for {dialect}
2. Only uses tables and columns from the schema
3. Properly handles any joins needed
4. Is complete and executable

Corrected SQL query:
"""
            
            response = self.llm.run_chain(retry_prompt, output_parser=LLMResponseSchemas.common_output_parser)
            response_text = response
            
            # Extract the SQL query from the response
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
            
            result = {
                "query": sql_query,
                "explanation": response_text.replace(sql_query, "").strip(),
                "full_response": response_text
            }
            
            retry_history.append(result)
            retries += 1
        
        return {
            "query": result["query"],
            "explanation": result["explanation"],
            "full_response": result["full_response"],
            "retries": retries,
            "retry_history": retry_history
        }