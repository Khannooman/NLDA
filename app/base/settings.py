import logging
import logging.handlers
import os
from dotenv import load_dotenv
from app.utils.utility_manager import UtilityManager
from app.enums.env_keys import EnvKeys

class Settings(UtilityManager):

    def __init__(self):
        super().__init__()
        try:
            loaded = load_dotenv(".env")
            logging.info("Env-Loaded: {}".format(loaded))
            # set Use Agent
            user_agent = os.getenv(EnvKeys.APP_USER_AGENT.value)
            os.environ['USER_AGENT'] = user_agent
            # create upload folder if not exists
            folder_name = self.get_env_variable(EnvKeys.UPLOAD_DIR.value)
            self.create_folder(folder_name)

            self.APP_HOST = self.get_env_variable(EnvKeys.APP_HOST.value)
            self.APP_PORT = int(self.get_env_variable(EnvKeys.APP_PORT.value))
            self.APP_ENVIROMENT = self.get_env_variable(EnvKeys.APP_ENVIROMENT.value)
            fmt = self.get_env_variable(EnvKeys.APP_LOGGING_FORMATTER.value)
            level = self.get_env_variable(EnvKeys.APP_LOGGING_LEVEL.value)
            log_folder = self.get_env_variable(EnvKeys.APP_LOGGING_FOLDER.value)
            log_file = self.get_env_variable(EnvKeys.APP_LOG_FILE.value)
            max_byte = int(self.get_env_variable(EnvKeys.APP_LOGGING_MAXBYTES.value))
            backup_count = int(self.get_env_variable(EnvKeys.APP_LOGGING_BACKUPCOUNT.value))
            date_format = self.get_env_variable(EnvKeys.APP_LOGGING_DATEFORMAT.value)
            # Create log folder
            project_path = self.get_project_dir()
            log_folder_path = project_path / log_folder
            self.create_folder(folder_path=log_folder_path)
            
            log_file_path = f'{log_folder}/{log_file}'
            logging.getLogger().handlers.clear()
            # Ensure logs directory exists
            logging.basicConfig(
                handlers=[logging.handlers.RotatingFileHandler(
                     log_file_path,
                    maxBytes=max_byte,
                    backupCount=backup_count)  
                ],
                level=level,
                format=fmt,
                datefmt=date_format,
            )
            # set up logging to console
            console = logging.StreamHandler()
            console.setLevel(level=level)
            # set a format which is simpler for console use
            formatter = logging.Formatter(fmt)
            console.setFormatter(formatter)
            # add the handler to the root logger
            logging.getLogger('').addHandler(console)
            logging.info("Logging Configuration Set.")
            logging.getLogger('watchfiles').setLevel(logging.ERROR)
    
        except Exception as err:
            logging.error("Error setting up logging configuration.")
            raise err
        
   

