import json
import logging
from functools import wraps
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.models.response_model import ResponseModel

class CatchAPIException:
    def __init__(self) -> None:
        logging.basicConfig(filename='logs/api-logs.log', level=logging.ERROR)    

    def catch_api_exceptions(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException as e:
                # Log the error with stack trace
                #logging.error(f"HTTPException: {str(e)}\n{traceback.format_exc()}")
                logging.error("Error in catch_api_exceptions wrapper class.")

                # Check if e.detail is already a dictionary
                if isinstance(e.detail, dict):
                    error_data = e.detail
                else:
                    # Try to parse the JSON object from the detail
                    try:
                        error_data = json.loads(e.detail)
                    except json.JSONDecodeError:
                        error_data = {"message": e.detail}

                response_model = ResponseModel(
                    message=error_data.get("message", ""),
                    error=json.dumps(e.detail),  # Convert error detail to string
                    status=ResponseModel.FAILED,
                    status_code=e.status_code,
                    data=[error_data]
                )
                return JSONResponse(content=response_model.model_dump(), status_code=e.status_code)

            except Exception as e:
                # Log the error with stack trace
                #logging.error(f"Exception: {str(e)}\n{traceback.format_exc()}")
                logging.error("Error in catch_api_exceptions wrapper class.")
                # For all other exceptions, return a 500 Internal Server Error
                error_message = str(e)
                response_model = ResponseModel(
                    message=error_message,
                    error=str(e),
                    status=ResponseModel.FAILED,
                    status_code=ResponseModel.INTERNAL_SERVER_ERROR_500
                )
                return JSONResponse(content=response_model.model_dump(), status_code=500)

        return wrapper