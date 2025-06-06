from typing import List
from fastapi import UploadFile,File, HTTPException
import shutil
import os
from app.enums.env_keys import EnvKeys
from app.utils.get_current_timestamp import get_current_timestamp_str
from app.utils.env_manager import EnvManager
from app.utils.file_system import FileSystem
from app.models.response_model import ResponseModel
class FileUploadManager:
    def __init__(self) -> None:
        pass
    
    async def upload(self, files: List[UploadFile]):
        env_manager = EnvManager()
        ALLOWED_EXTENSIONS = env_manager.get_env_variable(EnvKeys.UPLOAD_ALLOWED_EXTENTIONS.value)
        upload_directory = f'{env_manager.get_env_variable(EnvKeys.UPLOAD_DIR.value)}'
        FileSystem().create_folder(folder_path=upload_directory)

        for file in files:
            file_extension = str(os.path.splitext(file.filename)[1]).lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=ResponseModel.NOT_ALLOWED_400, detail=f"File extension '{file_extension}' is not allowed.")

            file_path = os.path.join(upload_directory, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"Uploaded file: {file.filename}")
        return {"message":"Files uploaded successfully", "directory":upload_directory}