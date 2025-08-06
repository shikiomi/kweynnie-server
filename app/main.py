from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db_connection
import bcrypt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Kweynnie API", version="1.0.0")


origins = [
    "http://localhost:3000",  
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health-check / welcome endpoint."""
    return {"message": "Welcome to Kweynnie API"}

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.post("/users/login")
async def user_login(request: Request):
    try:
        # Parse request data
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        # Database connection with error handling
        try:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
        except Exception as db_error:
            print(f"Database connection error: {db_error}")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        try:
            # Query user
            cursor.execute("SELECT * FROM Dim_User WHERE Email=%s", (email,))
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Verify password
            stored_password = user.get('Password')
            if not stored_password:
                raise HTTPException(status_code=401, detail="Account setup incomplete")
            
            # Check if password is hashed or plain text (for backward compatibility)
            if len(stored_password) < 50:  # Likely plain text
                password_valid = password == stored_password
            else:  # Likely hashed
                password_valid = verify_password(password, stored_password)
            
            if not password_valid:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Determine user type based on role
            user_role = user.get('Role', '').lower()
            if user_role == 'admin' or user_role == 'administrator':
                user_type = "admin"
            else:
                user_type = "user"
            
            return {
                "userType": user_type, 
                "user_id": user.get("User_ID"), 
                "role": user.get("Role"),
                "full_name": user.get("Full_Name"),
                "branch_id": user.get("Branch_ID")
            }
            
        finally:
            # Always close database connections
            cursor.close()
            db.close()
            
    except HTTPException:
        # Re-raise HTTP exceptions (they're handled properly by FastAPI)
        raise
    except Exception as e:
        # Log unexpected errors and return generic 500
        print(f"Unexpected login error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users")
def read_users():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Dim_User")  
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users


@app.post("/users")
async def create_user(request: Request):
    try:
        user_data = await request.json()   
        db = get_db_connection()
        cursor = db.cursor()

        # Hash the password if provided
        password = user_data.get("password", "defaultpassword123")
        hashed_password = hash_password(password)

        sql = (
            "INSERT INTO Dim_User (Full_Name, Role, Email, Branch_ID, Password) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        cursor.execute(
            sql,
            (
                user_data.get("Full_Name"),
                user_data.get("Role"),
                user_data.get("Email"),
                user_data.get("Branch_ID", 1),  # Default to Balangiga
                hashed_password,
            )
        )
        db.commit()
        cursor.close()
        db.close()
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"User creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")
