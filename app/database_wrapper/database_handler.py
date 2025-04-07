"""
Database Handler Component for SQL Agent

This module provides functionality to handle different database types and their
specific SQL dialects. It manages database connections, adapts queries to specific
SQL dialects, and provides a unified interface for database operations.
"""

import sqlalchemy
from sqlalchemy import create_engine, text, inspect, MetaData, Engine, URL
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple, Any, Union
from abc import ABC, abstractmethod
import re

class DatabaseHandler:
    """
    A class for handling different database types and their specific SQL dialects.
    """
    
    # Mapping of common database types to their SQLAlchemy dialects
    DIALECT_MAPPING = {
        'mysql': 'mysql',
        'postgresql': 'postgresql',
        'postgres': 'postgresql',
        'sqlite': 'sqlite',
        'oracle': 'oracle',
        'mssql': 'mssql',
        'sqlserver': 'mssql',
        'db2': 'db2',
        'redshift': 'redshift',
        'snowflake': 'snowflake',
        'bigquery': 'bigquery',
        'databricks': 'databricks'
    }
    
    def __init__(self, connection_url: URL):
        """Initialize the DatabaseHandler."""
        self.connection_url = connection_url
        self.engine = None
        self.connection = None
        self.dialect = None
        self.dialect_name = None
        self.inspector = None
        self.metadata = None
    
    
    def connect(self) -> bool:
        """
        Connect to a database.
        
        Args:
            connection_string: SQLAlchemy connection string
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.connection and not self.connection.closed:
            return True

        try:
            self.engine = create_engine(self.connection_url)
            self.connection = self.engine.connect()
            self.dialect = self.engine.dialect
            self.dialect_name = self.dialect.name
            self.inspector = sqlalchemy.inspect(self.engine)
            self.metadata = sqlalchemy.MetaData()
            self.metadata.reflect(bind=self.engine)
            return True
        except SQLAlchemyError as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.connection = None
        self.engine = None
        self.dialect = None
        self.dialect_name = None
        self.inspector = None
        self.metadata = None
    
    def get_dialect(self) -> str:
        """
        Get the SQL dialect of the connected database.
        
        Returns:
            str: SQL dialect name
        """
        if not self.dialect_name:
            raise ValueError("Not connected to a database. Call connect() first.")
        return self.dialect_name
    
    def normalize_dialect(self, dialect_name: str) -> str:
        """
        Normalize a dialect name to a standard form.
        
        Args:
            dialect_name: Name of the dialect
            
        Returns:
            str: Normalized dialect name
        """
        dialect_lower = dialect_name.lower()
        return self.DIALECT_MAPPING.get(dialect_lower, dialect_lower)
    
    def adapt_query(self, query: str, target_dialect: Optional[str] = None) -> str:
        """
        Adapt a SQL query to a specific SQL dialect.
        
        Args:
            query: SQL query to adapt
            target_dialect: Target SQL dialect (if None, uses the connected database's dialect)
            
        Returns:
            str: Adapted SQL query
        """
        if not target_dialect:
            if not self.dialect_name:
                raise ValueError("Not connected to a database and no target dialect specified.")
            target_dialect = self.dialect_name
        
        normalized_dialect = self.normalize_dialect(target_dialect)

        # Apply dialect-specific transformations
        if normalized_dialect == 'postgresql':
            return self._adapt_to_postgresql(query)
        elif normalized_dialect == 'mysql':
            return self._adapt_to_mysql(query)
        elif normalized_dialect == 'sqlite':
            return self._adapt_to_sqlite(query)
        elif normalized_dialect == 'mssql':
            return self._adapt_to_mssql(query)
        elif normalized_dialect == 'oracle':
            return self._adapt_to_oracle(query)
        else:
            # For other dialects, return the query as is
            return query
    
    def _adapt_to_postgresql(self, query: str) -> str:
        """
        # Adapt a SQL query to PostgreSQL dialect.
        
        # Args:
        #     query: SQL query to adapt
            
        # Returns:
        #     str: Adapted SQL query
        # """
        # # Replace LIMIT x OFFSET y with LIMIT x OFFSET y
        # query = re.sub(r'LIMIT\s+(\d+)\s+OFFSET\s+(\d+)', r'LIMIT \1 OFFSET \2', query, flags=re.IGNORECASE)
        # print(query)

        # # Replace ISNULL with IS NULL
        # query = re.sub(r'ISNULL\(([^,]+)\)', r'\1 IS NULL', query, flags=re.IGNORECASE)
        
        # # Replace TOP with LIMIT
        # query = re.sub(r'SELECT\s+TOP\s+(\d+)', r'SELECT', query, flags=re.IGNORECASE)
        # query = re.sub(r'FROM(.*?)ORDER BY', r'FROM\1ORDER BY', query, flags=re.IGNORECASE)
        # query = re.sub(r'ORDER BY(.*?)$', r'ORDER BY\1 LIMIT \2', query, flags=re.IGNORECASE)
        
        return query
    
    def _adapt_to_mysql(self, query: str) -> str:
        """
        Adapt a SQL query to MySQL dialect.
        
        Args:
            query: SQL query to adapt
            
        Returns:
            str: Adapted SQL query
        """
        # Replace OFFSET x ROWS with OFFSET x
        query = re.sub(r'OFFSET\s+(\d+)\s+ROWS', r'OFFSET \1', query, flags=re.IGNORECASE)
        
        # Replace || with CONCAT
        query = re.sub(r'([^\|])\s*\|\|\s*([^\|])', r'\1 CONCAT \2', query, flags=re.IGNORECASE)
        
        # Replace REGEXP_LIKE with REGEXP
        query = re.sub(r'REGEXP_LIKE\(([^,]+),\s*([^)]+)\)', r'\1 REGEXP \2', query, flags=re.IGNORECASE)
        
        return query
    
    def _adapt_to_sqlite(self, query: str) -> str:
        """
        Adapt a SQL query to SQLite dialect.
        
        Args:
            query: SQL query to adapt
            
        Returns:
            str: Adapted SQL query
        """
        # Replace OFFSET x ROWS with OFFSET x
        query = re.sub(r'OFFSET\s+(\d+)\s+ROWS', r'OFFSET \1', query, flags=re.IGNORECASE)
        
        # Replace ISNULL with IFNULL
        query = re.sub(r'ISNULL\(([^,]+),\s*([^)]+)\)', r'IFNULL(\1, \2)', query, flags=re.IGNORECASE)
        
        # Replace TOP with LIMIT
        query = re.sub(r'SELECT\s+TOP\s+(\d+)', r'SELECT', query, flags=re.IGNORECASE)
        query = re.sub(r'FROM(.*?)ORDER BY', r'FROM\1ORDER BY', query, flags=re.IGNORECASE)
        query = re.sub(r'ORDER BY(.*?)$', r'ORDER BY\1 LIMIT \2', query, flags=re.IGNORECASE)
        
        return query
    
    def _adapt_to_mssql(self, query: str) -> str:
        """
        Adapt a SQL query to Microsoft SQL Server dialect.
        
        Args:
            query: SQL query to adapt
            
        Returns:
            str: Adapted SQL query
        """
        # Replace LIMIT with TOP
        limit_match = re.search(r'LIMIT\s+(\d+)', query, flags=re.IGNORECASE)
        if limit_match:
            limit_value = limit_match.group(1)
            query = re.sub(r'SELECT', f'SELECT TOP {limit_value}', query, count=1, flags=re.IGNORECASE)
            query = re.sub(r'LIMIT\s+\d+', '', query, flags=re.IGNORECASE)
        
        # Replace CONCAT with +
        query = re.sub(r'CONCAT\(([^,]+),\s*([^)]+)\)', r'\1 + \2', query, flags=re.IGNORECASE)
        
        # Replace REGEXP_LIKE with LIKE (simplified)
        query = re.sub(r'REGEXP_LIKE\(([^,]+),\s*([^)]+)\)', r'\1 LIKE \2', query, flags=re.IGNORECASE)
        
        return query
    
    def _adapt_to_oracle(self, query: str) -> str:
        """
        Adapt a SQL query to Oracle dialect.
        
        Args:
            query: SQL query to adapt
            
        Returns:
            str: Adapted SQL query
        """
        # Replace LIMIT with ROWNUM
        limit_match = re.search(r'LIMIT\s+(\d+)', query, flags=re.IGNORECASE)
        if limit_match:
            limit_value = limit_match.group(1)
            query = re.sub(r'LIMIT\s+\d+', '', query, flags=re.IGNORECASE)
            query = f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit_value}"
        
        # Replace ISNULL with NVL
        query = re.sub(r'ISNULL\(([^,]+),\s*([^)]+)\)', r'NVL(\1, \2)', query, flags=re.IGNORECASE)
        
        return query
    
    def execute_query(self, query: str) -> Tuple[bool, Union[List[Dict], str]]:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            tuple: (success, results_or_error_message)
        """
        if not self.connection:
            return False, "Not connected to a database. Call connect() first."
        
        try:
            # Adapt the query to the current dialect
            adapted_query = self.adapt_query(query)
            print(adapted_query)
            # Execute the query
            result = self.connection.execute(text(adapted_query))
            column_names = result.keys()
            # Fetch results if it's a SELECT query
            if result.returns_rows:
                rows = [dict(zip(column_names, row)) for row in result]
                return True, rows
            else:
                return True, f"Query executed successfully. Rows affected: {result.rowcount}"
        except SQLAlchemyError as e:
            return False, f"Error executing query: {str(e)}"
    
    def get_table_names(self) -> List[str]:
        """
        Get all table names from the database.
        
        Returns:
            List of table names
        """
        if not self.engine:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        inspector = sqlalchemy.inspect(self.engine)
        return inspector.get_table_names()
    
    def get_dialect_specific_features(self) -> Dict[str, Any]:
        """
        Get dialect-specific features and limitations.
        
        Returns:
            Dictionary of dialect-specific features
        """
        if not self.dialect_name:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        normalized_dialect = self.normalize_dialect(self.dialect_name)
        
        features = {
            'name': normalized_dialect,
            'supports_window_functions': True,
            'supports_common_table_expressions': True,
            'supports_json': True,
            'supports_arrays': False,
            'date_functions': [],
            'string_functions': [],
            'aggregate_functions': []
        }
        
        if normalized_dialect == 'postgresql':
            features.update({
                'supports_arrays': True,
                'date_functions': ['DATE_TRUNC', 'EXTRACT', 'TO_CHAR'],
                'string_functions': ['LOWER', 'UPPER', 'TRIM', 'SUBSTRING', 'REGEXP_REPLACE'],
                'aggregate_functions': ['SUM', 'AVG', 'MIN', 'MAX', 'COUNT', 'ARRAY_AGG', 'STRING_AGG']
            })
        elif normalized_dialect == 'mysql':
            features.update({
                'date_functions': ['DATE_FORMAT', 'EXTRACT', 'DATE_ADD', 'DATE_SUB'],
                'string_functions': ['LOWER', 'UPPER', 'TRIM', 'SUBSTRING', 'REGEXP_REPLACE'],
                'aggregate_functions': ['SUM', 'AVG', 'MIN', 'MAX', 'COUNT', 'GROUP_CONCAT']
            })
        elif normalized_dialect == 'sqlite':
            features.update({
                'supports_window_functions': False,
                'supports_common_table_expressions': False,
                'supports_json': False,
                'date_functions': ['STRFTIME', 'DATE', 'TIME', 'DATETIME'],
                'string_functions': ['LOWER', 'UPPER', 'TRIM', 'SUBSTR', 'REPLACE'],
                'aggregate_functions': ['SUM', 'AVG', 'MIN', 'MAX', 'COUNT', 'GROUP_CONCAT']
            })
        elif normalized_dialect == 'mssql':
            features.update({
                'date_functions': ['DATEPART', 'DATEADD', 'DATEDIFF', 'FORMAT'],
                'string_functions': ['LOWER', 'UPPER', 'TRIM', 'SUBSTRING', 'REPLACE'],
                'aggregate_functions': ['SUM', 'AVG', 'MIN', 'MAX', 'COUNT', 'STRING_AGG']
            })
        elif normalized_dialect == 'oracle':
            features.update({
                'date_functions': ['TO_CHAR', 'EXTRACT', 'ADD_MONTHS', 'MONTHS_BETWEEN'],
                'string_functions': ['LOWER', 'UPPER', 'TRIM', 'SUBSTR', 'REPLACE', 'REGEXP_REPLACE'],
                'aggregate_functions': ['SUM', 'AVG', 'MIN', 'MAX', 'COUNT', 'LISTAGG']
            })
        
        return features


 