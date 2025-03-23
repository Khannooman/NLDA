from enum import Enum

class AppEnvironment(Enum):
    PRODUCTION = 'production'
    STAGING = 'staging'
    DEVELOPMENT = 'development'
    TESTING = 'testing'