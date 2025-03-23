from app.constants.app_messages import AppMessages
from app.constants.app_constants import AppConstants
from app.constants.api_call_status import APICallStatus
from app.constants.data_type_constants import DataTypeConstants
from app.constants.directory_names import DirectoryNames
from app.constants.fast_api_constants import FastAPIConstants
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.constants.log_messages import LogMessages

class ConstantManager(AppMessages, AppConstants, APICallStatus, DataTypeConstants, DirectoryNames, FastAPIConstants, RoutePaths, RouteTags, LogMessages):
    def __init__(self) -> None:
        super().__init__()