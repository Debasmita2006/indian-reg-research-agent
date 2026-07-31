from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
print([row[0] for row in result])
db.close()