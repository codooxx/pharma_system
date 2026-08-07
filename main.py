from models.database import engine, Base
from security.licensing import generate_hardware_id
import models.products
import models.inventory

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
    hwid = generate_hardware_id()
    print(f"Device Hardware ID (HWID): {hwid}")