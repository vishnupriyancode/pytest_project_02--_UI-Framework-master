import os
import json
import logging
import sqlite3
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import traceback

# Configure logging
logger = logging.getLogger(__name__)

# Define SQLAlchemy base
Base = declarative_base()

# Response metadata model
class ResponseMetadata(Base):
    __tablename__ = 'response_metadata'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    processing_time = Column(Float)
    response_size = Column(Integer)
    response_file = Column(String(500))
    error_type = Column(String(100))
    error_message = Column(Text)
    total_chunks = Column(Integer)
    successful_chunks = Column(Integer)
    failed_chunks = Column(Integer)
    
# Chunked response model
class ChunkMetadata(Base):
    __tablename__ = 'chunk_metadata'
    
    id = Column(Integer, primary_key=True)
    parent_filename = Column(String(255), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    total_chunks = Column(Integer)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    response_file = Column(String(500))
    error_message = Column(Text)

# JSON Data storage (for databases supporting JSON type)
class JSONData(Base):
    __tablename__ = 'json_data'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    chunk_index = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)
    data = Column(JSON)  # This will use JSON type for PostgreSQL, TEXT for SQLite

class DatabaseStorage:
    """Class for storing large JSON responses in databases"""
    
    def __init__(self, db_type='sqlite', connection_string=None):
        """Initialize database connection
        
        Args:
            db_type: Type of database ('sqlite', 'postgresql', etc.)
            connection_string: Database connection string
        """
        self.db_type = db_type
        
        # Default connection string if not provided
        if connection_string is None:
            if db_type == 'sqlite':
                # Create output directory if it doesn't exist
                output_dir = os.path.join(os.path.dirname(__file__), "output")
                os.makedirs(output_dir, exist_ok=True)
                connection_string = f"sqlite:///{os.path.join(output_dir, 'json_responses.db')}"
            elif db_type == 'postgresql':
                connection_string = "postgresql://username:password@localhost:5432/json_responses"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        
        self.connection_string = connection_string
        
        try:
            # Create engine and session
            self.engine = create_engine(connection_string)
            self.Session = sessionmaker(bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(self.engine)
            
            logger.info(f"Connected to {db_type} database: {connection_string}")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def save_processing_results(self, results):
        """Save processing results metadata to database
        
        Args:
            results: List of processing result dictionaries
        
        Returns:
            dict: Summary of database operations
        """
        session = self.Session()
        
        try:
            # Process main results
            for result in results:
                # Create metadata record
                metadata = ResponseMetadata(
                    filename=result.get('filename', ''),
                    status=result.get('status', 'unknown'),
                    timestamp=datetime.fromisoformat(result.get('timestamp')) if result.get('timestamp') else datetime.now(),
                    processing_time=result.get('processing_time'),
                    response_size=result.get('response_size'),
                    response_file=result.get('response_file'),
                    error_type=result.get('error_type'),
                    error_message=result.get('error_message'),
                    total_chunks=result.get('total_chunks'),
                    successful_chunks=result.get('successful_chunks'),
                    failed_chunks=result.get('failed_chunks')
                )
                session.add(metadata)
                
                # If chunked, add chunk metadata
                if result.get('status') == 'chunked' and 'chunk_results' in result:
                    for chunk in result.get('chunk_results', []):
                        chunk_metadata = ChunkMetadata(
                            parent_filename=result.get('filename', ''),
                            chunk_index=chunk.get('chunk_index'),
                            total_chunks=result.get('total_chunks'),
                            status=chunk.get('status', 'unknown'),
                            timestamp=datetime.fromisoformat(result.get('timestamp')) if result.get('timestamp') else datetime.now(),
                            response_file=chunk.get('response_file'),
                            error_message=chunk.get('error_message')
                        )
                        session.add(chunk_metadata)
            
            # Commit changes
            session.commit()
            logger.info(f"Saved metadata for {len(results)} processing results to database")
            
            return {
                'status': 'success',
                'records_saved': len(results),
                'database': self.db_type,
                'connection': self.connection_string
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving to database: {str(e)}")
            logger.error(traceback.format_exc())
            
            return {
                'status': 'error',
                'error': str(e),
                'database': self.db_type
            }
            
        finally:
            session.close()
    
    def save_json_data(self, filename, json_data, chunk_index=None):
        """Save actual JSON data to database (for databases that support this)
        
        This is most useful for PostgreSQL which has native JSON support.
        For SQLite, the JSON will be stored as TEXT.
        
        Args:
            filename: Source filename
            json_data: The JSON data to store
            chunk_index: Optional chunk index for large files
            
        Returns:
            bool: Success status
        """
        # Skip for very large JSON objects
        json_str = json.dumps(json_data)
        if len(json_str) > 10000000:  # 10MB limit
            logger.warning(f"JSON data for {filename} is too large for database storage (> 10MB)")
            return False
        
        session = self.Session()
        
        try:
            # Create data record
            data_record = JSONData(
                filename=filename,
                chunk_index=chunk_index,
                timestamp=datetime.now(),
                data=json_data if self.db_type == 'postgresql' else json_str  # Store as JSON or text
            )
            session.add(data_record)
            
            # Commit changes
            session.commit()
            logger.info(f"Saved JSON data for {filename} to database")
            
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving JSON data to database: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
        finally:
            session.close()
    
    def export_to_excel(self, output_path=None):
        """Export database contents to Excel for reporting
        
        Args:
            output_path: Path to save Excel file
            
        Returns:
            str: Path to saved Excel file
        """
        if output_path is None:
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"db_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        try:
            # Query data
            metadata_query = "SELECT * FROM response_metadata"
            chunks_query = "SELECT * FROM chunk_metadata"
            
            # Create DataFrames
            metadata_df = pd.read_sql(metadata_query, self.engine)
            chunks_df = pd.read_sql(chunks_query, self.engine)
            
            # Save to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                metadata_df.to_excel(writer, sheet_name='Processing Results', index=False)
                if not chunks_df.empty:
                    chunks_df.to_excel(writer, sheet_name='Chunk Details', index=False)
            
            logger.info(f"Exported database to Excel: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting database to Excel: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def query_results(self, status=None, filename=None, limit=100):
        """Query processing results with filters
        
        Args:
            status: Filter by status (success, error, chunked)
            filename: Filter by filename (can use % for wildcards)
            limit: Maximum number of results to return
            
        Returns:
            pandas.DataFrame: Query results
        """
        session = self.Session()
        
        try:
            # Build query
            query = "SELECT * FROM response_metadata WHERE 1=1"
            
            if status:
                query += f" AND status = '{status}'"
            
            if filename:
                query += f" AND filename LIKE '{filename}'"
            
            query += f" ORDER BY timestamp DESC LIMIT {limit}"
            
            # Execute query
            results_df = pd.read_sql(query, self.engine)
            
            return results_df
            
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            logger.error(traceback.format_exc())
            return pd.DataFrame()
            
        finally:
            session.close()

# Function to quickly create a database connection
def get_db_connection(db_type='sqlite', connection_string=None):
    """Create and return a database connection
    
    Args:
        db_type: Type of database ('sqlite', 'postgresql', etc.)
        connection_string: Optional connection string
        
    Returns:
        DatabaseStorage: Database connection object
    """
    return DatabaseStorage(db_type, connection_string) 