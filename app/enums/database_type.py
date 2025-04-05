from enum import Enum

class DatabaseType(Enum):
    MSSQL = 'mssql'
    MYSQL = 'mysql'
    POSTGRESSQL = 'postgresql'
    SQLITE = 'sqlite'
    AWS_ATHENA = 'AWSAthena'
    DYNAMODB = 'dynamodb'
    AWS_REDSHIFT = 'AWSRedshift'
    SNOWFLAKE = 'Snowflake'
    FIREBOLT = 'Firebolt'
    APACHE_CASSANDRA = 'ApacheCassandra'
    APACHE_HIVE  = 'ApacheHive'
    APACHE_SPARK = 'ApacheSpark'
    MONGODB = 'mongodb'
    ORACLE = 'oracle'
    MARIADB = 'MariaDB'
    DB2 = 'DB2'
    REDIS = 'Redis'
    BIGQUERY = 'BigQuery'
    AMAZON_S3 = 'AmazonS3'
    
