import sys
import os
import hashlib
from PyQt6.QtWidgets import QApplication, QMessageBox
from app.services.database import engine, SessionLocal, Base
from app.core import models
from app.ui.login import LoginDialog
from app.ui.main_window import MainWindow

def auto_seed_on_startup():
    db = SessionLocal()
    try:
        # Check if database is empty by checking if any staff exist
        if not db.query(models.Staff).first():
            print("Database is empty. Auto-seeding baseline data...")
            hashed_password = hashlib.sha256('password123'.encode()).hexdigest()
            
            # Add Default Staff
            admin = models.Staff(
                username='admin', 
                password_hash=hashed_password, 
                name='Admin User', 
                role='admin', 
                is_active=True
            )
            cashier = models.Staff(
                username='cashier1', 
                password_hash=hashed_password, 
                name='Main Cashier', 
                role='cashier', 
                is_active=True
            )
            waiter = models.Staff(
                username='waiter1', 
                password_hash=hashed_password, 
                name='James Waiter', 
                role='waiter', 
                is_active=True
            )
            db.add_all([admin, cashier, waiter])
            db.commit()

            # Add Default Categories
            cats = ['Food', 'Drinks', 'Rooms', 'Services']
            for c in cats:
                category = models.Category(name=c)
                db.add(category)
            db.commit()

            # Add Default Store
            store = models.Store(name="Main Restaurant", location="Ground Floor")
            db.add(store)
            db.commit()

            # Add Default Settings
            settings = [
                models.Setting(key="business_name", value="KastomPOS"),
                models.Setting(key="currency", value="KES"),
                models.Setting(key="receipt_footer", value="Thank you for choosing KastomPOS.")
            ]
            db.add_all(settings)
            db.commit()
            
            print("Auto-seeding complete.")
    except Exception as e:
        print(f"Error during database auto-seeding: {e}")
    finally:
        db.close()

def main():
    # 1. Initialize SQLite Database
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database table creation failed: {e}")
        # Standard sys exit if DB fails
        sys.exit(1)

    # 2. Run Seeding if empty
    auto_seed_on_startup()

    # 3. Start Qt GUI Loop
    app = QApplication(sys.argv)
    
    # Show Login dialog
    login = LoginDialog()
    if login.exec() == LoginDialog.DialogCode.Accepted:
        # Fetch the authenticated user from the login dialog
        db = SessionLocal()
        try:
            # Query the user to get a fresh database session-attached object
            user = db.query(models.Staff).filter(models.Staff.username == login.username_input.text().strip()).first()
            if user:
                main_window = MainWindow(user)
                main_window.show()
                sys.exit(app.exec())
            else:
                QMessageBox.critical(None, "Authentication Error", "User record lost during session hand-off.")
                sys.exit(1)
        finally:
            db.close()
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
