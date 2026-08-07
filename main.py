from models.database import engine, Base
import models.products
import models.inventory

def init_db():
    # إنشاء كافة الجداول في قاعدة البيانات محلياً
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()