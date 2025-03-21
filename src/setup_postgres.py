import psycopg2
import os
import logging
import dotenv
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_postgres_database():
    """
    Set up a PostgreSQL database for API responses.
    This creates the database if it doesn't exist and creates the required table.
    """
    try:
        # Load environment variables
        dotenv.load_dotenv()
        
        # Get PostgreSQL connection parameters
        pg_host = os.getenv("PG_HOST", "localhost")
        pg_port = os.getenv("PG_PORT", "5432")
        pg_dbname = os.getenv("PG_DBNAME", "api_responses")
        pg_user = os.getenv("PG_USER", "postgres")
        pg_password = os.getenv("PG_PASSWORD", "")
        
        logger.info(f"Setting up PostgreSQL database '{pg_dbname}' on {pg_host}")
        
        # Connect to the default PostgreSQL database to create our database
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            dbname="postgres",  # Connect to default database first
            user=pg_user,
            password=pg_password
        )
        
        # Set autocommit to create the database
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if the database already exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{pg_dbname}'")
        if cursor.fetchone() is None:
            # Create the database
            cursor.execute(f"CREATE DATABASE {pg_dbname}")
            logger.info(f"Created database '{pg_dbname}'")
        else:
            logger.info(f"Database '{pg_dbname}' already exists")
        
        # Close connection to default database
        conn.close()
        
        # Connect to our database
        conn = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            dbname=pg_dbname,
            user=pg_user,
            password=pg_password
        )
        
        cursor = conn.cursor()
        
        # Create the api_responses table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_responses (
                edit_id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                input_json TEXT,
                api_response TEXT,
                expected_result TEXT
            )
        ''')
        
        conn.commit()
        
        # Check if the table was created
        cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = 'api_responses'")
        if cursor.fetchone():
            logger.info("Table 'api_responses' is ready")
        else:
            logger.error("Failed to create table 'api_responses'")
            return False
        
        conn.close()
        
        logger.info("PostgreSQL database setup completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error setting up PostgreSQL database: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_postgres_database()
    if success:
        print("PostgreSQL database setup completed successfully.")
        sys.exit(0)
    else:
        print("Failed to set up PostgreSQL database. Check the logs for details.")
        sys.exit(1) 