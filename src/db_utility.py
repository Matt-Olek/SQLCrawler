import psycopg2
from config import POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST

class PostgresDB:
    def __init__(self):
            
        self.connection = None
        
    def connect(self):
        """Connect to the PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                database=POSTGRES_DB
            )

            return self.connection
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and optionally fetch results"""
        if not self.connection:
            self.connect()
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()

    def health_check(self):
        """Check if the database is healthy"""
        try:
            self.connect()
            # Check if the connection is successful
            if self.connection:
                return True
            else:
                return False
        except Exception as e:
            return False