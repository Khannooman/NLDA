import logging
import os
from typing import Dict, Union
from langchain_openai.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import PromptTemplate
from app.utils.utility_manager import UtilityManager
from app.enums.env_keys import EnvKeys
from langchain_community.callbacks import get_openai_callback
from langchain.schema.runnable import RunnableSequence

class OpenAIManager(UtilityManager):
    def __init__(self):
        super().__init__()
        
        self.OPENAI_KEY = self.get_env_variable(EnvKeys.OPENAI_KEY.value)
        self.TEMPERATURE = self.get_env_variable(EnvKeys.OPENAI_TEMPERATURE.value)
        self.MODEL = self.get_env_variable(EnvKeys.OPENAI_MODEL.value)
        self.VERBOSE = self.str_to_bool(self.get_env_variable(EnvKeys.OPENAI_VERBOSE.value))
        
        os.environ["OPENAI_API_KEY"] = self.OPENAI_KEY
        
    def run_chain(self, prompt_template: PromptTemplate, output_parser: StructuredOutputParser = None, input_values: Dict = {}, model: str = None) -> Union[dict, str]:
        try:
            llm_model = ChatOpenAI(
                    model_name=model or self.MODEL,
                    temperature=self.TEMPERATURE,
                    verbose=True,
                )
            chain = RunnableSequence(prompt_template | llm_model)

            with get_openai_callback() as cb:
                response = chain.invoke(input_values)
                text_response = response.content if hasattr(response, "content") else response

                logging.info("\nTokens Used: {} \nTotal Cost: {}".format(cb.total_tokens, cb.total_cost))
                logging.info("\nLLM-Response:\n {}".format(text_response))

                if output_parser:
                    try:
                        result = output_parser.parse(text_response)
                        result.update({
                            "total_tokens": cb.total_tokens,
                            "completion_tokens": cb.completion_tokens,
                            "total_cost": cb.total_cost if cb.total_cost else 0.0,
                            "prompt_tokens": cb.prompt_tokens
                        })
                        return result
                    except Exception as parse_error:
                        logging.error("Error parsing output")
                        raise parse_error

                return text_response
        except Exception as e:
            logging.error("Error in run_chain")
            raise e
    