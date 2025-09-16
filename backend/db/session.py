import os
from sqlalchemy import create_engine
from core import config

DATABASE_URL = (
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

# Adaptive Logic for SSL Configuration
ssl_args = {}
# Check the environment variable that we will set
if config.ENVIRONMENT == 'production':
   # In Cloud Run, just enable SSL verification without a specific CA file
    # The driver will use the system's root CAs
    ssl_args['ssl_verify_cert'] = True
    print("Running in PRODUCTION mode: Using system SSL verification.")
else:
     # Locally (development), we still need the ca.pem file
  
    ssl_args['ssl_ca'] = config.CA_PATH
    print("Running in DEVELOPMENT mode: Using local ca.pem file.")
  

try:
    engine = create_engine(DATABASE_URL,connect_args={"ssl": ssl_args})
    connection = engine.connect()
    connection.close()
    print("Connection to TiDB Cloud established successfully.")
except Exception as e:
    print(f"Failed to create database connection: {e}")
    engine = None