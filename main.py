from models.database import Base, SessionLocal, engine
import models.products
from services.auth import ensure_admin
from views.app import PharmacyApp
def main():
    Base.metadata.create_all(bind=engine); db=SessionLocal(); ensure_admin(db); db.close(); PharmacyApp().mainloop()
if __name__=="__main__": main()
