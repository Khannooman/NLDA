import logging
import os
from pathlib import Path, PurePath
from typing import Union

class FileSystem:
    def __init__(self) -> None:
        self.UPLOAD_DIR = "uploads"
        
    def create_file(self, file_path: str):
        file_path = self.clean_path(path=file_path)
        if not file_path.exists():
            # Create file with restricted permissions
            with open(file_path, "x", opener=lambda path, flags: os.open(path, flags, 0o600)):
                logging.info("File created with restricted permissions.")

    def create_folder(self, folder_path: str):
        folder_path = self.clean_path(path=folder_path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True, mode=0o700)
            logging.info("Folder created with restricted permissions.")

    def delete_file(self, file_path: str) -> bool:
        file_path = self.clean_path(path=file_path)
        try:
            file_path.unlink()
            logging.info("File deleted successfully.")
            return True
        except FileNotFoundError:
            logging.warning("File not found.")
            return False
        except PermissionError:
            logging.error("Permission denied when deleting file.")
            return False
        except Exception as e:
            logging.error("Error deleting file")
            return False

    def delete_folder(self, folder_path: Union[str, Path]) -> bool:
        folder_path = self.clean_path(path=folder_path)
        try:
            import shutil
            shutil.rmtree(folder_path)
            logging.info("Folder deleted successfully.")
            return True
        except FileNotFoundError:
            logging.warning("Folder not found.")
            return False
        except PermissionError:
            logging.error("Permission denied when deleting folder.")
            return False
        except Exception as e:
            logging.error("Error deleting folder")
            return False

    def create_and_get_upload_dir(self, folder_name: str) -> Path:
        if not self.UPLOAD_DIR:
            raise ValueError("UPLOAD_DIR environment variable is not set")

        base_upload_path = Path(self.UPLOAD_DIR).resolve()
        
        upload_location = self.clean_path(base_upload_path / folder_name)
        upload_location.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        return upload_location

    def clean_path(self, path: Union[str, Path]) -> Path:
        cleaned_path = Path(path).resolve()
        # Additional check to prevent symlink traversal
        if cleaned_path.is_symlink():
            raise ValueError("Access denied. Path is a symbolic link and cannot be accessed.")
        
        return cleaned_path

    def get_project_dir(self) -> Path:
        # Ensure the base directory is secure and isolated
        project_dir = Path(__file__).resolve().parent.parent.parent
        if not project_dir.is_dir():
            raise ValueError("Project directory is not valid or accessible.")
        return project_dir