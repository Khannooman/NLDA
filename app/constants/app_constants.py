class AppConstants:
    STATIC = 'static'

    GET_TABLE_SCHEMA_QUERY = """
    SELECT * FROM {} ORDER BY RANDOM() LIMIT 5
    """
    