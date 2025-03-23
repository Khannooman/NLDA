from enum import Enum

class QueryOperationType(Enum):
    GENERATE = 'generate'
    EXECUTE = 'execute'
    VARIFICATION = 'varification'