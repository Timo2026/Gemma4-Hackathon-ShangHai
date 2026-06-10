from app.core.database import SessionLocal
from app.models.models import User
from app.core.security import verify_password

db = SessionLocal()
user = db.query(User).filter(User.phone == '13800138000').first()
if not user:
    print("USER NOT FOUND")
elif not verify_password('demo123', user.password_hash):
    print("PASSWORD WRONG")
else:
    print("LOGIN OK, user_id:", user.id, "name:", user.name)
db.close()
