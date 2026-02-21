from sqlalchemy import text
from app.db.database import engine

def run_migration():
    with engine.connect() as connection:
        with open("backend/migrations/add_column_attack_logs.sql", "r") as f:
            sql = f.read()
            # Split by ; to run multiple statements if needed, but text() might handle it or need separate execution
            statements = sql.split(';')
            for statement in statements:
                if statement.strip():
                    connection.execute(text(statement))
            connection.commit()
            print("Migration executed successfully.")

if __name__ == "__main__":
    run_migration()
