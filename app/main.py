from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db_connection


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

@app.post("/users/login")
async def user_login(request: Request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Dim_User WHERE Email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if user and password:  
        return {"userType": "user"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


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
    user_data = await request.json()  
    db = get_db_connection()
    cursor = db.cursor()

    sql = (
        "INSERT INTO Dim_User (Full_Name, Role, Email, Branch_ID) "
        "VALUES (%s, %s, %s, %s)"
    )
    cursor.execute(
        sql,
        (
            user_data.get("Full_Name"),
            user_data.get("Role"),
            user_data.get("Email"),
            user_data.get("Branch_ID"),
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "User created successfully"}
