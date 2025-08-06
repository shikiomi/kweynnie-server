import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def update_admin_password():
    try:
        # Connect to your capstoni database
        db = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database="capstoni"
        )
        cursor = db.cursor()
        
        # Hash the existing password
        hashed_password = hash_password("kweynnie")
        
        # Update the admin user
        cursor.execute(
            "UPDATE Dim_User SET Password = %s WHERE Email = %s",
            (hashed_password, "tjd.regis@gmail.com")
        )
        
        db.commit()
        
        # Verify the update
        cursor.execute("SELECT Email, Role FROM Dim_User WHERE Email = %s", ("tjd.regis@gmail.com",))
        user = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if user:
            print("✅ Admin password updated successfully!")
            print("You can now login with:")
            print("Email: tjd.regis@gmail.com")
            print("Password: kweynnie")
        else:
            print("❌ Admin user not found!")
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")

if __name__ == "__main__":
    update_admin_password()
