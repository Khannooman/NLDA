"""
Schema Parser Component for SQL Agent

This module provides functionality to parse and understand database schemas
for use in SQL query generation. It extracts table names, column names,
data types, and relationships from a database and formats this information
for consumption by an LLM.
"""

import sqlalchemy
from sqlalchemy import inspect, MetaData, URL
from typing import List, Dict, Any, Optional
from app.database_wrapper.database_handler import DatabaseHandler
import re

class SchemaParser(DatabaseHandler):
    """
    A class for parsing database schemas and extracting relevant information
    for SQL query generation.
    """
    
    def __init__(self, connection_url: URL):
        """Initialize the SchemaParser."""

        super().__init__(connection_url=connection_url)
    
    def get_all_tables(self) -> List[str]:
        """
        Get all table names from the database.
        
        Returns:
            List of table names
        """
        if not self.inspector:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        return self.inspector.get_table_names()
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary containing table schema information
        """
        if not self.inspector:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        columns = self.inspector.get_columns(table_name)
        primary_keys = self.inspector.get_pk_constraint(table_name)['constrained_columns']
        foreign_keys = self.inspector.get_foreign_keys(table_name)
        indexes = self.inspector.get_indexes(table_name)
        
        # Format column information
        formatted_columns = []
        for col in columns:
            col_info = {
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col.get('nullable', True),
                'default': col.get('default', None),
                'is_primary_key': col['name'] in primary_keys
            }
            formatted_columns.append(col_info)
        
        # Format foreign key information
        formatted_foreign_keys = []
        for fk in foreign_keys:
            fk_info = {
                'constrained_columns': fk['constrained_columns'],
                'referred_table': fk['referred_table'],
                'referred_columns': fk['referred_columns']
            }
            formatted_foreign_keys.append(fk_info)
        
        return {
            'name': table_name,
            'columns': formatted_columns,
            'primary_keys': primary_keys,
            'foreign_keys': formatted_foreign_keys,
            'indexes': indexes
        }
    
    def get_create_table_statement(self, table_name: str) -> str:
        """
        Get the CREATE TABLE statement for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            CREATE TABLE statement as a string
        """
        if not self.inspector:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        # This is a simplified approach - actual implementation would depend on the dialect
        table = self.metadata.tables.get(table_name)
        if table is not None:
            create_stmt = str(sqlalchemy.schema.CreateTable(table).compile(dialect=self.dialect))
            return create_stmt
        else:
            raise ValueError(f"Table {table_name} not found in metadata.")
    
    def get_sample_rows(self, table_name: str, limit: int = 3) -> List[Dict]:
        """
        Get sample rows from a table.
        
        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return
            
        Returns:
            List of dictionaries representing rows
        """
        if not self.metadata:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        table = self.metadata.tables.get(table_name)
        if table is not None:
            try:
                result = self.connection.execute(statement=table.select().limit(limit))
                column_names = result.keys()
                rows = [dict(zip(column_names, row)) for row in result]
                return rows
            except Exception as e:
                print(f"Error getting sample rows: {e}")
                return []
        else:
            raise ValueError(f"Table {table_name} not found in metadata.")
    
    def get_relevant_tables(self, question: str, tables: List[str]) -> List[str]:
        """
        Determine which tables are relevant to a natural language question.
        This is a simple implementation that looks for table names in the question.
        A more sophisticated approach would use an LLM.
        
        Args:
            question: Natural language question
            tables: List of available table names
            
        Returns:
            List of relevant table names
        """
        relevant_tables = []
        
        # Convert question to lowercase for case-insensitive matching
        question_lower = question.lower()
        
        for table in tables:
            # Check for exact table name
            if table.lower() in question_lower:
                relevant_tables.append(table)
                continue
            
            # Check for plural form of table name
            if table.lower() + 's' in question_lower:
                relevant_tables.append(table)
                continue
            
            # Check for singular form of table name (if it ends with 's')
            if table.lower().endswith('s') and table.lower()[:-1] in question_lower:
                relevant_tables.append(table)
                continue
        
        return relevant_tables
    
    def format_schema_for_llm(self, tables: List[str]) -> str:
        """
        Format schema information for consumption by an LLM.
        
        Args:
            tables: List of table names to include
            
        Returns:
            Formatted schema information as a string
        """
        if not self.inspector:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        schema_info = []
        
        for table_name in tables:
            create_stmt = self.get_create_table_statement(table_name)
            sample_rows = self.get_sample_rows(table_name)
            schema_info.append(f"-- Table: {table_name}")
            schema_info.append(create_stmt)
            
            if sample_rows:
                schema_info.append(f"\n-- Sample rows from {table_name} table:")
                for i, row in enumerate(sample_rows, 1):
                    schema_info.append(f"-- Row {i}: {row}")
            
            schema_info.append("\n")
        
        return "\n".join(schema_info)
    
    def parse_schema(self, question: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse the database schema and return relevant information.
        
        Args:
            connection_string: SQLAlchemy connection string
            question: Optional natural language question to filter relevant tables
            
        Returns:
            Dictionary containing schema information
        """

        if not self.connection:
            raise ValueError("Not connected to a database. Call connect() first.")
        
        # Get all tables
        all_tables = self.get_all_tables()
        # Determine relevant tables if a question is provided
        if question:
            relevant_tables = self.get_relevant_tables(question, all_tables)
            # If no relevant tables found, include all tables
            if not relevant_tables:
                relevant_tables = all_tables
        else:
            relevant_tables = all_tables
        
        # Get schema information for relevant tables
        tables_info = {}
        for table_name in relevant_tables:
            tables_info[table_name] = self.get_table_schema(table_name)
        
        # Format schema for LLM
        formatted_schema = self.format_schema_for_llm(relevant_tables)

        return {
            "dialect": self.dialect_name,
            "all_tables": all_tables,
            "relevant_tables": relevant_tables,
            "tables_info": tables_info,
            "formatted_schema": formatted_schema
        }