from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUPABASE_DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL')

if not SUPABASE_DATABASE_URL:
    raise ValueError("SUPABASE_DATABASE_URL is not set in the environment.")

try:
    engine = create_engine(SUPABASE_DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute("SELECT 1")
        print("Connection to Supabase database successful!")
except Exception as e:
    print(f"Error connecting to Supabase database: {str(e)}")
