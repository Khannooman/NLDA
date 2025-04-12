from langchain.output_parsers import StructuredOutputParser
from langchain_core.output_parsers import JsonOutputParser

class LLMResponseSchemas:
    common_response_schemas = []
    common_output_parser = StructuredOutputParser.from_response_schemas(
        common_response_schemas)
    common_format_instructions = common_output_parser.get_format_instructions()
    # json_output_parser = JsonOutputParser()