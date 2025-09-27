import psycopg2
from dotenv import load_dotenv
import os

def db_query(statement: str):

    """ Execute an sql statement to a postgres database
    
    Args:
      statement -- the SQL statement to be executed

    Returns:
      The result of a SELECT query, if applicable

    Raises:
      An error message from the database
    """


    # Load environment variables from .env
    load_dotenv()

    # Fetch variables
    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")

    # Connect to the database
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection successful!")
        
        # Create cursor and execute the query
        cursor = connection.cursor()
        cursor.execute(statement)

        # Attempt to fetch the result
        # If the query is not a SELECT it it will return nothing
        try:
            result = cursor.fetchall()
        except Exception:
            result = None

        # Commit changes and close the cursor and connection
        connection.commit()
        cursor.close()
        connection.close()
        print("Connection closed.")

        return result

    # Return any errors, these can be syntax errors in the query or connection errors
    except Exception as e:
        print(f"Failed to connect: {e}")