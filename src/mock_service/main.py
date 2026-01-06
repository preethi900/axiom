from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Axiom Mock Service")

# -- Models --
class ProfileUpdate(BaseModel):
    email: str
    full_name: Optional[str] = None

class ProfileResponse(BaseModel):
    email: str
    full_name: str
    account_tier: str

# -- Custom 404 --
from fastapi.responses import JSONResponse
@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "page-not-found"},
    )

# -- In-Memory Database --
fake_db = {
    "user": {
        "email": "user@example.com",
        "full_name": "John Doe",
        "account_tier": "gold"
    }
}

# -- Dependencies --
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # For demo purposes, accept any token unless it's explicitly 'invalid'
    token = authorization.split(" ")[1]
    if token == "invalid-token":
         raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.get("/profile", response_model=ProfileResponse)
async def get_profile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
         raise HTTPException(status_code=401, detail="Unauthorized")
    
    return fake_db["user"]

@app.put("/profile", response_model=ProfileResponse)
async def update_profile(update: ProfileUpdate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
         raise HTTPException(status_code=401, detail="Unauthorized")
    
    # INTENTIONAL BUG: No email validation logic here. 
    # Usually we would check if '@' in update.email etc., or let Pydantic EmailStr do it.
    # We are using 'str' so anything passes.
    
    fake_db["user"]["email"] = update.email
    if update.full_name:
        fake_db["user"]["full_name"] = update.full_name
    return fake_db["user"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
