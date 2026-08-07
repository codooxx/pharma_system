from models.database import engine, Base
from security.licensing import generate_hardware_id
from views.main_window import PharmaApp
import models.products
import models.inventory

def main():
    Base.metadata.create_all(bind=engine)
    hwid = generate_hardware_id()
    print(f"[+] System Started. HWID: {hwid}")

    app = PharmaApp()
    app.mainloop()

if __name__ == "__main__":
    main()