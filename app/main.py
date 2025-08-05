from fastapi import FastAPI

app = FastAPI(title="Kweynnie API", version="1.0.0")

@app.get("/")
async def root():
    """Health-check / welcome endpoint."""
    return {"message": "Welcome to Kweynnie API"}

