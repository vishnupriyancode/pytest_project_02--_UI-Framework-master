import sqlite3
import os
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add PostgreSQL support
import psycopg2
from psycopg2.extras import RealDictCursor
import dotenv

# Configure logging
logging.basicConfig(
    filename='logs/db_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()

class DatabaseManager:
    """
    A class for managing database operations related to API responses.
    Supports both SQLite and PostgreSQL databases.
    """
    
    def __init__(self, 
                db_type: str = "sqlite",
                db_file: str = "results/api_responses.db",
                pg_host: str = None,
                pg_port: str = None,
                pg_dbname: str = None,
                pg_user: str = None,
                pg_password: str = None):
        """
        Initialize the DatabaseManager with database connection parameters.
        
        Args:
            db_type: Database type - "sqlite" or "postgres"
            db_file: Path to the SQLite database file (for SQLite only).
            pg_host: PostgreSQL server host (for PostgreSQL only).
            pg_port: PostgreSQL server port (for PostgreSQL only).
            pg_dbname: PostgreSQL database name (for PostgreSQL only).
            pg_user: PostgreSQL username (for PostgreSQL only).
            pg_password: PostgreSQL password (for PostgreSQL only).
        """
        self.db_type = db_type.lower()
        
        # For SQLite
        self.db_file = db_file
        
        # For PostgreSQL - if not provided, try to get from environment variables
        self.pg_host = pg_host or os.getenv("PG_HOST", "localhost")
        self.pg_port = pg_port or os.getenv("PG_PORT", "5432")
        self.pg_dbname = pg_dbname or os.getenv("PG_DBNAME", "api_responses")
        self.pg_user = pg_user or os.getenv("PG_USER", "postgres")
        self.pg_password = pg_password or os.getenv("PG_PASSWORD", "")
        
        if self.db_type == "sqlite":
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
            logger.info(f"DatabaseManager initialized with SQLite file: {db_file}")
        elif self.db_type == "postgres":
            logger.info(f"DatabaseManager initialized with PostgreSQL: {self.pg_dbname} on {self.pg_host}")
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Initialize database
        self._init_db()
    
    def _get_connection(self):
        """Get a database connection based on the configured type."""
        if self.db_type == "sqlite":
            return sqlite3.connect(self.db_file)
        elif self.db_type == "postgres":
            return psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                dbname=self.pg_dbname,
                user=self.pg_user,
                password=self.pg_password
            )
    
    def _init_db(self):
        """Initialize the database with required tables."""
        try:
            conn = self._get_connection()
            
            if self.db_type == "sqlite":
                cursor = conn.cursor()
                
                # Create api_responses table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_responses (
                        edit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        input_json TEXT,
                        api_response TEXT,
                        expected_result TEXT
                    )
                ''')
            
            elif self.db_type == "postgres":
                cursor = conn.cursor()
                
                # Create api_responses table if it doesn't exist
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
            conn.close()
            
            logger.info(f"Database initialized successfully for {self.db_type}")
        
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def store_response(self, 
                      input_json: str, 
                      api_response: Dict[str, Any], 
                      expected_result: str = "Success") -> int:
        """
        Store an API response in the database.
        
        Args:
            input_json: The path to the input JSON file.
            api_response: The API response dictionary.
            expected_result: The expected result of the API call.
            
        Returns:
            The edit_id of the inserted record.
        """
        try:
            # Convert API response to JSON string
            api_response_str = json.dumps(api_response)
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Connect to database
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert the record
            if self.db_type == "sqlite":
                cursor.execute('''
                    INSERT INTO api_responses (timestamp, input_json, api_response, expected_result)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, input_json, api_response_str, expected_result))
                
                # Get the edit_id of the inserted record
                edit_id = cursor.lastrowid
            
            elif self.db_type == "postgres":
                cursor.execute('''
                    INSERT INTO api_responses (timestamp, input_json, api_response, expected_result)
                    VALUES (%s, %s, %s, %s)
                    RETURNING edit_id
                ''', (timestamp, input_json, api_response_str, expected_result))
                
                # Get the edit_id from the RETURNING clause
                edit_id = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored response for {input_json} with edit_id {edit_id}")
            return edit_id
        
        except Exception as e:
            logger.error(f"Error storing response: {str(e)}")
            raise
    
    def get_response_by_edit_id(self, edit_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a stored API response by its edit_id.
        
        Args:
            edit_id: The edit_id of the response to retrieve.
            
        Returns:
            A dictionary containing the response data, or None if not found.
        """
        try:
            # Connect to database
            conn = self._get_connection()
            
            if self.db_type == "sqlite":
                conn.row_factory = sqlite3.Row  # This enables column access by name
                cursor = conn.cursor()
                
                # Query the record
                cursor.execute('''
                    SELECT * FROM api_responses WHERE edit_id = ?
                ''', (edit_id,))
                
                # Fetch the record
                record = cursor.fetchone()
                
                conn.close()
                
                if record:
                    # Convert to dictionary
                    result = {
                        "edit_id": record["edit_id"],
                        "timestamp": record["timestamp"],
                        "input_json": record["input_json"],
                        "api_response": json.loads(record["api_response"]),
                        "expected_result": record["expected_result"]
                    }
                    logger.info(f"Retrieved response for edit_id {edit_id}")
                    return result
                
            elif self.db_type == "postgres":
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Query the record
                cursor.execute('''
                    SELECT * FROM api_responses WHERE edit_id = %s
                ''', (edit_id,))
                
                # Fetch the record
                record = cursor.fetchone()
                
                conn.close()
                
                if record:
                    # Record is already a dict-like object with RealDictCursor
                    result = {
                        "edit_id": record["edit_id"],
                        "timestamp": record["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        "input_json": record["input_json"],
                        "api_response": json.loads(record["api_response"]),
                        "expected_result": record["expected_result"]
                    }
                    logger.info(f"Retrieved response for edit_id {edit_id}")
                    return result
            
            logger.warning(f"No response found for edit_id {edit_id}")
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving response: {str(e)}")
            raise
    
    def get_all_responses(self) -> List[Dict[str, Any]]:
        """
        Retrieve all stored API responses.
        
        Returns:
            A list of dictionaries containing all response data.
        """
        try:
            # Connect to database
            conn = self._get_connection()
            
            # Query all records
            if self.db_type == "sqlite":
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM api_responses ORDER BY edit_id DESC')
                records = cursor.fetchall()
                
                conn.close()
                
                # Convert to list of dictionaries
                results = []
                for record in records:
                    results.append({
                        "edit_id": record["edit_id"],
                        "timestamp": record["timestamp"],
                        "input_json": record["input_json"],
                        "api_response": json.loads(record["api_response"]),
                        "expected_result": record["expected_result"]
                    })
            
            elif self.db_type == "postgres":
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute('SELECT * FROM api_responses ORDER BY edit_id DESC')
                records = cursor.fetchall()
                
                conn.close()
                
                # Convert to list of dictionaries
                results = []
                for record in records:
                    results.append({
                        "edit_id": record["edit_id"],
                        "timestamp": record["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                        "input_json": record["input_json"],
                        "api_response": json.loads(record["api_response"]),
                        "expected_result": record["expected_result"]
                    })
            
            logger.info(f"Retrieved {len(results)} responses")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving all responses: {str(e)}")
            raise

# For direct execution testing
if __name__ == "__main__":
    # Test with SQLite
    db_manager_sqlite = DatabaseManager(db_type="sqlite")
    
    # Test with PostgreSQL if credentials are available
    try:
        db_manager_postgres = DatabaseManager(db_type="postgres")
        print("Successfully connected to PostgreSQL database")
    except Exception as e:
        print(f"Could not connect to PostgreSQL: {str(e)}")
        print("Using SQLite instead for testing")
        db_manager_postgres = None
    
    # Store a sample response in SQLite
    edit_id = db_manager_sqlite.store_response(
        input_json="test.json",
        api_response={"status": "success", "message": "Edit is working properly"},
        expected_result="Success"
    )
    
    # Retrieve the response from SQLite
    response = db_manager_sqlite.get_response_by_edit_id(edit_id)
    print(f"Retrieved SQLite response: {response}")
    
    # If PostgreSQL is available, test it too
    if db_manager_postgres:
        # Store a sample response in PostgreSQL
        pg_edit_id = db_manager_postgres.store_response(
            input_json="test_pg.json",
            api_response={"status": "success", "message": "PostgreSQL is working"},
            expected_result="Success"
        )
        
        # Retrieve the response from PostgreSQL
        pg_response = db_manager_postgres.get_response_by_edit_id(pg_edit_id)
        print(f"Retrieved PostgreSQL response: {pg_response}") 