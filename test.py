from sqlalchemy import create_engine
import os
import dotenv 

dotenv.load_dotenv()

print(f'Connecting to database at {os.environ["DATABASE_URL"]}')
engine = create_engine(os.getenv('DATABASE_URL'))
engine.connect()

print('Connected to database')