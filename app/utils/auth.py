import os
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.utils.utility_manager import UtilityManager
from app.enums.env_keys import EnvKeys

## Make Instance of enviroment variable
utility_manager = UtilityManager()

#API KEY HEADER
API_KEY_NAME = utility_manager.get_env_variable(EnvKeys.API_KEY_NAME.value)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
# Validate api key
async def verify_api_key(api_key: str = Depends(api_key_header)):
    valid_api_key = [utility_manager.get_env_variable(EnvKeys.SECURITY_API_KEY.value)]
    if api_key not in valid_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key

    
