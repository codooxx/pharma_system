import hashlib, hmac, os
from models.products import User
def hash_password(password):
    salt=os.urandom(16); digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,210_000); return f"pbkdf2_sha256$210000${salt.hex()}${digest.hex()}"
def verify_password(password,encoded):
    try:
        _,rounds,salt,digest=encoded.split("$",3); test=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),int(rounds)); return hmac.compare_digest(test.hex(),digest)
    except (ValueError,TypeError): return False
def authenticate(db,username,password):
    user=db.query(User).filter(User.username==username.strip(),User.active.is_(True)).first(); return user if user and verify_password(password,user.password_hash) else None
def ensure_admin(db):
    if not db.query(User).first(): db.add(User(username="admin",full_name="مدير النظام",role="admin",password_hash=hash_password("admin123"))); db.commit()
