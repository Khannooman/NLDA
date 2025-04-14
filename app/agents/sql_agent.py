from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, END, StateGraph
from app.database_wrapper.schema_parser import SchemaParser
from app.database_wrapper.database_handler import DatabaseHandler
from app.agents.query_generator import QueryGenerator
from app.agents.query_validator import QueryValidator
from app.models.agent_state_model import AgentState
from app.llm.openai_manager import OpenAIManager
from app.prompts.llm_response_schema import LLMResponseSchemas
from app.prompts.sql_agent_prompt import Agentprompts
import logging
class SQLAgents:
    "Node for SQL Agents"
    def __init__(self, db_handler: DatabaseHandler, session_id: str):
        self.db_handler = db_handler
        self.schema_parser = SchemaParser(db_handler=db_handler)
        self.query_generator = QueryGenerator()
        self.query_validator = QueryValidator()
        self.llm = OpenAIManager()
        self.prompts = Agentprompts()
        self.session_id = session_id


    def parse_schema(self, state: AgentState) -> AgentState:
        """Parse the database schema

        Args:
            state (AgentState): curent state of the agent

        Returns:
            AgentState: Update agent state
        """
        # Extract the last user message
        last_message = state.messages[-1]
        if not isinstance(last_message, HumanMessage):
            return state
        
        question = last_message.content
        try:
            # parse the schema
            logging.info("Parsing schema...")
            schema_info = self.schema_parser.parse_schema(question, session_id=self.session_id, top_k=5)
            #Update the schema 
            state.schema_info = schema_info
            # Add a message to indicates the success
            state.messages.append(
                AIMessage(content=f"I've analyzed the database schema. Found {len(schema_info['relevant_tables'])} relevant tables: {', '.join(schema_info['relevant_tables'])}")
            )

        except Exception as e:
            # Handle any errors 
            state.error = f"Error parsing schema: {str(e)}"
            state.messages.append(
                AIMessage(content=f"I encountered an error while analyzing the database schema: {str(e)}")
            )
        return state

    def generate_query(self, state: AgentState) -> AgentState:
        """
        Generate sql query based on the user question and schema information

        Args:generate_query
            state (AgentState): current state of the agent
        Returns:
            AgentState: Updated agent state
        """ 

        # check if we have schema or not

        if state.schema_info is None:
            state.error = "No schema information availabel. please the parse the schema first"
            state.messages.append(
                AIMessage(content="I need to analyze the database schema before I can generate a query")
            )
            return state
        
        # Extract the last user message
        last_message = state.messages[-1]
        if not isinstance(last_message, HumanMessage):
            last_user_message = None
            for message in reversed(state.messages):
                if isinstance(message, HumanMessage):
                    last_user_message = message
                    break
                
            if not last_user_message:
                state.error = "No user question found"
                state.messages.append(
                    AIMessage(content="I need a user question to generate a query")
                )
                return state
            
            question = last_user_message.content
            
        else:
            question = last_message.content

        try:
            #Generate the query
            logging.info("Generating query...")
            generated_query = self.query_generator.generate_query(
                question=question,
                schema=state.schema_info['formatted_schema'],
                dialect=state.schema_info['dialect'],
                dialect_features=self.db_handler.get_dialect_specific_features() if self.db_handler.dialect_name else None
            )

            # Update the state
            state.generated_query = generated_query
            
            # Add a message to indicate success
            state.messages.append(
                AIMessage(content=f"I've generated a SQL query to answer your question:\n\n```sql\n{generated_query['query']}\n```\n\nNow I'll validate this query to make sure it's correct.")
            )
        except Exception as e:
            # Handle errors
            state.error = f"Error generating query: {str(e)}"
            state.messages.append(
                AIMessage(content=f"I encountered an error while generating the SQL query: {str(e)}")
            )
        
        return state


    def validate_query(self, state: AgentState) -> AgentState:
        """
        Validate the generated SQL query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        # Check if we have a generated query
        if not state.generated_query:
            state.error = "No generated query available. Please generate a query first."
            state.messages.append(
                AIMessage(content="I need to generate a SQL query before I can validate it.")
            )
            return state
        
        # Check if we have schema information
        if not state.schema_info:
            state.error = "No schema information available. Please parse the schema first."
            state.messages.append(
                AIMessage(content="I need to analyze the database schema before I can validate the query.")
            )
            return state
        
         # Extract the last user message
        last_message = state.messages[-1]
        if not isinstance(last_message, HumanMessage):
            last_user_message = None
            for message in reversed(state.messages):
                if isinstance(message, HumanMessage):
                    last_user_message = message
                    break
                
            if not last_user_message:
                state.error = "No user question found"
                state.messages.append(
                    AIMessage(content="I need a user question to generate a query")
                )
                return state
            
            question = last_user_message.content
            
        else:
            question = last_message.content
        
        try:
            # Validate the query
            logging.info("Validating query...")
            validation_result = self.query_validator.validate(
                query=state.generated_query["query"],
                schema=state.schema_info["formatted_schema"],
                dialect=state.schema_info["dialect"]
            )
            # Update the state
            state.validation_result = validation_result
            
            # Add a message to indicate the validation result
            if validation_result["is_valid"]:
                state.messages.append(
                    AIMessage(content="The SQL query looks valid! Now I'll execute it to get the results.")
                )
            else:
                state.messages.append(
                    AIMessage(content=f"\n\nThere is some issue in query I'll correct these issues and generate a new query:\n\n```sql\n{validation_result['corrected_query']}\n```")
                )
                # Update the generated query with the corrected version
                state.generated_query["query"] = validation_result["corrected_query"]

        except Exception as e:
            # Handle errors
            state.error = f"Error validating query: {str(e)}"
            state.messages.append(
                AIMessage(content=f"I encountered an error while validating the SQL query: {str(e)}")
            )
        return state
    
    def fixed_query(self, state: AgentState) -> AgentState:
        """
        Execute the query fixer

        Args:
            state (AgentState): current agent state

        Returns:
            AgentState: Update agent state
        """

        # check if we have error
        if not state.error:
            state.messages.append(
                AIMessage(content="I need to execute a SQL query before I can fix it.")
            )
            return state
        
        if not state.generated_query:
            state.messages.append(
                AIMessage(content="I need to generate a SQL query before I can fix it")
            )
            return state
        
         # Extract the last user message
        last_message = state.messages[-1]
        if not isinstance(last_message, HumanMessage):
            last_user_message = None
            for message in reversed(state.messages):
                if isinstance(message, HumanMessage):
                    last_user_message = message
                    break
                
            if not last_user_message:
                state.error = "No user question found"
                state.messages.append(
                    AIMessage(content="I need a user question to generate a query")
                )
                return state
            
            question = last_user_message.content
            
        else:
            question = last_message.content

        try:
            logging.info("Fixing Error...")
            new_query = self.query_generator.query_fixer(
                question=question,
                schema=state.schema_info['schema'],
                dialect=state.schema_info['dialect'],
                previous_query=state.generated_query['query'],
                error=state.error
            )

            state.generated_query = new_query

            # Add a message to indicate success
            state.messages.append(
                AIMessage(content=f"I've generated a new SQL query to fix the error :\n\n```sql\n{new_query['query']}\n```\n\nNow I'll validate this query to make sure it's correct.")
            )
        except Exception as e:
            # Handle errors
            state.error = f"Error generating query: {str(e)}"
            state.messages.append(
                AIMessage(content=f"I encountered an error while generating the SQL query: {str(e)}")
            )
        
        return state


    def execute_query(self, state: AgentState) -> AgentState:
        """
        Execute the validated SQL query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        # Check if we have a generated query
        if not state.generated_query:
            state.error = "No generated query available. Please generate a query first."
            state.messages.append(
                AIMessage(content="I need to generate a SQL query before I can execute it.")
            )
            return state
        
        # Check if we have schema information
        if not state.schema_info:
            state.error = "No schema information available. Please parse the schema first."
            state.messages.append(
                AIMessage(content="I need to analyze the database schema before I can execute the query.")
            )
            return state
        
        try:
            print("Executing query...")
            counter = 0
            # Execute the query
            success, result = self.db_handler.execute_query(state.generated_query["query"])
            # Update the state
            state.execution_result = result
            # Add a message to indicate the execution result
            if success:
                if isinstance(result, list):
                    # Format the result for display
                    if len(result) > 0:
                        # Add a message with the result
                        state.messages.append(
                            AIMessage(content=f"I executed the SQL query and got {len(result)} results.")
                        )
                    else:
                        state.messages.append(
                            AIMessage(content="I executed the SQL query but got no results.")
                        )
                else:
                    state.messages.append(
                        AIMessage(content=f"I executed the SQL query successfully: {result}")
                    )
            else:
                state.messages.append(
                    AIMessage(content=f"I encountered an error while executing the SQL query: {result}")
                )
                
                # Try to generate a new query based on the error
                state.messages.append(
                    AIMessage(content="Let me try to fix the query and execute it again.")
                )
                # Regenerate the query
                if counter < 5:
                    counter += 1
                    return self.fixed_query(state)         
            
        except Exception as e:
            # Handle errors
            state.error = f"Error executing query: {str(e)}"
            state.messages.append(
                AIMessage(content=f"I encountered an error while executing the SQL query: {str(e)}")
            )
        
        return state


    def generate_final_answers(self, state: AgentState) -> AgentState:
        """
        Generate a final answer based on the query results.

        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        # Check if we have execution results
        if not state.execution_result:
            state.error = "No execution results available. Please execute the query first."
            state.messages.append(
                AIMessage(content="I need to execute the SQL query before I can provide a final answer.")
            )
            return state
        
        # Extract the last user message
        last_user_message = None
        for message in reversed(state.messages):
            if isinstance(message, HumanMessage):
                last_user_message = message
                break
        
        if not last_user_message:
            state.error = "No user question found."
            state.messages.append(
                AIMessage(content="I need a question to provide a final answer.")
            )
            return state
        
        question = last_user_message.content
        
        try:
            print("Generating final answer...")
            # Create a prompt for the LLM to generate a final answer
            prompt = ChatPromptTemplate.from_template(self.prompts.final_response_prompt)
            
            # Use the LLM to generate a final answer
            input_values = {
                "query": state.generated_query["query"],
                "response": state.execution_result,
                "user_input": question
            }
            response = self.llm.run_chain(
                prompt_template=prompt,
                output_parser=LLMResponseSchemas.common_output_parser,
                input_values=input_values)
            # print(response)
            # Update the state
            state.final_answer = response
            
            # Add a message with the final answer
            state.messages.append(
                AIMessage(content="Succfully generated final response")
            )
            
        except Exception as e:
            # Handle errors
            state.error = f"Error generating final answer: {str(e)}"
            state.messages.append(
                AIMessage(content=f"I encountered an error while generating the final answer: {str(e)}")
            )
        return state

    
def create_sql_agent(db_handler: DatabaseHandler, session_id: str) -> StateGraph:
    """LangGraph Agent for SQL
    Args:
        connection_url (URL): connection url
    Returns:
        StateGraph: return the compiled workflow
    """

    sqlagents = SQLAgents(db_handler=db_handler, session_id=session_id)

    # create the workflow
    workflow = StateGraph(AgentState)

    # add node
    workflow.add_node("parse_schema", sqlagents.parse_schema)
    workflow.add_node("generate_query", sqlagents.generate_query)
    workflow.add_node("validate_query", sqlagents.validate_query)
    workflow.add_node("execute_query", sqlagents.execute_query)
    workflow.add_node("generate_final_answer", sqlagents.generate_final_answers)
    
    # add edge node
    workflow.add_edge(START, "parse_schema")
    workflow.add_edge("parse_schema", "generate_query")
    workflow.add_edge("generate_query", "validate_query")
    workflow.add_edge("validate_query", "execute_query")
    workflow.add_edge("execute_query", "generate_final_answer")
    workflow.add_edge("generate_final_answer", END)

    app = workflow.compile()
    logging.info("Graph successfully compiled")
    return app



        




