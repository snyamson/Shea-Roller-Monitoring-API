import os
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Hub, Submission

def get_database_url(filename='database.ini', section='postgresql') -> str:
    # Create a parser
    parser = ConfigParser()

    config_path = os.path.join(os.path.dirname(__file__), filename)

    # Read database.ini
    parser.read(config_path)
    if parser.has_section(section):
        user = parser.get('postgresql', 'user')
        password = parser.get('postgresql', 'password')
        host = parser.get('postgresql', 'host')
        dbname = parser.get('postgresql', 'dbname')

        # Return database URL
        return f'postgresql://{user}:{password}@{host}/{dbname}'
    else:
        raise Exception('Section {0} not found in file {1}.'.format(section, filename))
    

# Set up connection to the database
# Create the database engine
engine = create_engine(get_database_url(), echo=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables if they do not exist
Hub.__table__.create(bind=engine, checkfirst=True)
Submission.__table__.create(bind=engine, checkfirst=True)


# Exception handling for database connection
try:
    # Try connecting to the database
    with engine.connect() as connection:
        print("Successfully connected to the database")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    raise