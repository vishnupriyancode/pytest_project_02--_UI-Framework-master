# Recommended Backend Changes for Domain Column

To fully support the new Domain column in the API Responses table, the following changes are recommended for the backend:

## 1. Update Database Schema

Add a `domain` column to the `api_responses` table in your database:

### For SQLite:

```sql
ALTER TABLE api_responses ADD COLUMN domain TEXT DEFAULT 'unknown';
```

### For PostgreSQL:

```sql
ALTER TABLE api_responses ADD COLUMN domain VARCHAR(255) DEFAULT 'unknown';
```

## 2. Update Database Manager

Modify the `get_all_responses` method in `src/db_manager.py` to include the domain field:

```python
def get_all_responses(self) -> List[Dict[str, Any]]:
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
                # Get domain from record or set as unknown
                domain = record["domain"] if "domain" in record.keys() else "unknown"
                
                results.append({
                    "edit_id": record["edit_id"],
                    "domain": domain,
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
                # Get domain from record or set as unknown
                domain = record["domain"] if "domain" in record else "unknown"
                
                results.append({
                    "edit_id": record["edit_id"],
                    "domain": domain,
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
```

## 3. Update `store_response` Method

Modify the `store_response` method to accept and store the domain:

```python
def store_response(self, 
                  input_json: str, 
                  api_response: Dict[str, Any], 
                  expected_result: str = "Success",
                  domain: str = "unknown") -> int:
    """
    Store an API response in the database.
    
    Args:
        input_json: The input JSON string.
        api_response: The API response as a dictionary.
        expected_result: The expected result, e.g., "Success" or "Failed".
        domain: The domain associated with the API request.
    
    Returns:
        The edit_id of the stored response.
    """
    try:
        # Connect to database
        conn = self._get_connection()
        
        # Convert API response to JSON string
        api_response_str = json.dumps(api_response)
        
        # Insert the record
        if self.db_type == "sqlite":
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO api_responses (timestamp, input_json, api_response, expected_result, domain)
                VALUES (datetime('now'), ?, ?, ?, ?)
                ''',
                (input_json, api_response_str, expected_result, domain)
            )
            edit_id = cursor.lastrowid
            
        elif self.db_type == "postgres":
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO api_responses (timestamp, input_json, api_response, expected_result, domain)
                VALUES (NOW(), %s, %s, %s, %s)
                RETURNING edit_id
                ''',
                (input_json, api_response_str, expected_result, domain)
            )
            edit_id = cursor.fetchone()[0]
        
        # Commit the transaction
        conn.commit()
        conn.close()
        
        logger.info(f"Stored API response with edit_id {edit_id}")
        return edit_id
    
    except Exception as e:
        logger.error(f"Error storing API response: {str(e)}")
        raise
```

## 4. Update Database Initialization

Modify the `_init_db` method to include the domain column:

```python
def _init_db(self):
    """Initialize the database schema."""
    try:
        # Connect to database
        conn = self._get_connection()
        
        # Create tables
        if self.db_type == "sqlite":
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_responses (
                    edit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    api_response TEXT NOT NULL,
                    expected_result TEXT NOT NULL,
                    domain TEXT DEFAULT 'unknown'
                )
            ''')
            
        elif self.db_type == "postgres":
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_responses (
                    edit_id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    input_json TEXT NOT NULL,
                    api_response TEXT NOT NULL,
                    expected_result TEXT NOT NULL,
                    domain VARCHAR(255) DEFAULT 'unknown'
                )
            ''')
        
        # Commit the transaction
        conn.commit()
        conn.close()
        
        logger.info("Database schema initialized")
    
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
```

## 5. Update API Middleware

Ensure the API middleware correctly handles the domain field in requests and responses. This includes updating the endpoints that process new JSON files to extract and store domain information.

### Update `get_all_responses` Endpoint

Modify the endpoint to support domain filtering:

```python
def get_all_responses(self):
    """
    Endpoint to retrieve all stored API responses with optional domain filtering.
    
    Returns:
        JSON response with filtered stored data.
    """
    try:
        # Get domain filter parameter if provided
        domain_filter = request.args.get('domain')
        
        # Retrieve all responses from the database
        responses = self.db_manager.get_all_responses()
        
        # Apply domain filter if provided
        if domain_filter and domain_filter.lower() != 'all':
            responses = [r for r in responses if r.get('domain') == domain_filter]
        
        logger.info(f"Retrieved {len(responses)} responses" + 
                   (f" filtered by domain: {domain_filter}" if domain_filter else ""))
        
        return jsonify({
            "status": "success",
            "count": len(responses),
            "responses": responses
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving all responses: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error retrieving all responses: {str(e)}"
        }), 500
```

### Update `export_responses` Endpoint

Enhance the Excel export endpoint to support domain filtering:

```python
def export_responses(self):
    """
    Endpoint to export all responses to Excel with optional domain filtering.
    
    Returns:
        Excel file containing filtered API responses.
    """
    try:
        # Get domain filter parameter if provided
        domain_filter = request.args.get('domain')
        
        # Retrieve all responses from the database
        responses = self.db_manager.get_all_responses()
        
        # Apply domain filter if provided
        if domain_filter and domain_filter.lower() != 'all':
            responses = [r for r in responses if r.get('domain') == domain_filter]
            
        # Generate Excel file
        filename = "api_responses"
        if domain_filter and domain_filter.lower() != 'all':
            filename += f"_{domain_filter}"
        filename += ".xlsx"
        
        # ... existing Excel generation code ...
        
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        logger.error(f"Error exporting responses: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error exporting responses: {str(e)}"
        }), 500
```

## Implementation Strategy

1. Create a database migration to add the domain column to existing records
2. Update the database manager code with the changes above
3. Update the API middleware endpoints to handle domain filtering
4. Test the changes thoroughly to ensure backward compatibility
5. Verify the domain filtering works correctly in both the UI and Excel exports 