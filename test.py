from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import dotenv 

dotenv.load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'chinks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
    
    def __repr__(self):
        return f'<User(name={self.name}, fullname={self.fullname}, password={self.password})>'

print(f'Connecting to database at {os.getenv("DATABASE_URL")}')
engine = create_engine(os.getenv('DATABASE_URL'))

# Create the table in the database
Base.metadata.create_all(engine)

# Create a sessionmaker bound to the engine
Session = sessionmaker(bind=engine)

# Create a new session
session = Session()

print('Connected to database')

# Create a new user
new_user = User(name='ed', fullname='Ed Jones', password='edspassword')
session.add(new_user)
session.commit()

# Query the database using the session
users = session.query(User).all()

# Print the results
for user in users:
    print(user)

# Close the session when you're done
session.close()