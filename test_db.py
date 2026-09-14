from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connected successfully!")
        print(result.scalar())

except Exception as e:
    print("Database connection failed:")
    print(e)
