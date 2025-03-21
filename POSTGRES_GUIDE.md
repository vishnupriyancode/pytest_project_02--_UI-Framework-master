# PostgreSQL Integration Guide

This guide explains how to set up and use PostgreSQL with the application instead of the default SQLite database.

## Prerequisites

1. PostgreSQL server installed and running
2. pgAdmin 4 installed (for graphical interface)
3. Python 3.6+ with required dependencies

## Setup Steps

### 1. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Configuration

Create a `.env` file in the project root directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file with your PostgreSQL connection details:

```
PG_HOST=localhost
PG_PORT=5432
PG_DBNAME=api_responses
PG_USER=postgres
PG_PASSWORD=your_password_here
```

### 3. Create the PostgreSQL Database

Run the setup script:

```bash
python src/setup_postgres.py
```

This will:
- Create the database if it doesn't exist
- Create the required table structure
- Verify that everything is set up correctly

### 4. Run the Application with PostgreSQL

```bash
python enhanced_main.py --db_type postgres
```

## Connecting with pgAdmin

1. **Launch pgAdmin 4**

2. **Connect to Your PostgreSQL Server**:
   - Right-click on "Servers" in the browser tree
   - Select "Create" > "Server..."
   - In the "General" tab, give your connection a name (e.g., "Local PostgreSQL")
   - In the "Connection" tab, enter your connection details:
     - Host: localhost (or your server address)
     - Port: 5432
     - Maintenance database: postgres
     - Username: postgres (or your username)
     - Password: your password
   - Click "Save"

3. **Navigate to Your Database**:
   - Expand "Servers" > "Your Server" > "Databases"
   - Find "api_responses" in the list of databases
   - Expand "api_responses" > "Schemas" > "public" > "Tables"
   - Right-click on "api_responses" table > "View/Edit Data" > "All Rows"

## Querying Data with pgAdmin

You can use pgAdmin's Query Tool to run SQL queries against your database:

1. Right-click on the "api_responses" database and select "Query Tool"
2. Enter SQL queries like:

```sql
-- Get all responses
SELECT * FROM api_responses ORDER BY edit_id DESC;

-- Get a specific response by edit_id
SELECT * FROM api_responses WHERE edit_id = 123;

-- Get the most recent 10 responses
SELECT * FROM api_responses ORDER BY timestamp DESC LIMIT 10;
```

## Testing PostgreSQL Connection

To test your PostgreSQL connection:

```bash
python -c "from src.db_manager import DatabaseManager; db = DatabaseManager(db_type='postgres'); print('Connection successful')"
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:

1. Check that PostgreSQL is running:
   ```bash
   # On Linux
   sudo systemctl status postgresql
   
   # On Windows
   # Check Services app for PostgreSQL service status
   ```

2. Verify your credentials in the `.env` file

3. Make sure your PostgreSQL server allows connections:
   - Check `pg_hba.conf` for client authentication settings
   - Ensure the PostgreSQL service is listening on the specified port

### Permissions Issues

If you encounter permissions errors:

1. Ensure your PostgreSQL user has the necessary permissions:
   ```sql
   -- Run in PostgreSQL as superuser
   GRANT ALL PRIVILEGES ON DATABASE api_responses TO your_user;
   ```

### Database Exists Error

If you get an error that the database already exists:

1. Use pgAdmin to connect to the existing database
2. You can either:
   - Use the existing database
   - Drop the database and recreate it:
     ```sql
     -- Run in PostgreSQL as superuser
     DROP DATABASE api_responses;
     ```
     Then run `python src/setup_postgres.py` again

## Switching Back to SQLite

To switch back to SQLite, run:

```bash
python enhanced_main.py --db_type sqlite
```

No additional setup is required for SQLite as it's the default option. 