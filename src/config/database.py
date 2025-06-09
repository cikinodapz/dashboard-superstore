from sqlalchemy import create_engine

def get_db_connection():
    DB_USER = 'postgres'
    DB_PASS = '18agustuz203'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'dwh_superstore2'
    
    engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    return engine