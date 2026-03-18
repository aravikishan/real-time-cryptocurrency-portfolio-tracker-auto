from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, String, Float, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    assets = Column(String)  # JSON string of assets
    total_value = Column(Float)

class MarketTrend(Base):
    __tablename__ = "market_trends"

    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    impact = Column(Float)

Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class PortfolioResponse(BaseModel):
    user_id: str
    assets: list
    total_value: float

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    with open("templates/dashboard.html") as f:
        return f.read()

@app.get("/profile", response_class=HTMLResponse)
async def read_profile():
    with open("templates/profile.html") as f:
        return f.read()

@app.get("/market", response_class=HTMLResponse)
async def read_market():
    with open("templates/market.html") as f:
        return f.read()

@app.post("/api/register")
async def register_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, full_name=user.full_name, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "email": db_user.email}

@app.get("/api/portfolio/{username}", response_model=PortfolioResponse)
async def get_portfolio(username: str, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioResponse(user_id=user.id, assets=eval(portfolio.assets), total_value=portfolio.total_value)

@app.get("/api/market-trends")
async def get_market_trends(db: SessionLocal = Depends(get_db)):
    trends = db.query(MarketTrend).all()
    return trends

@app.get("/api/prices")
async def get_prices():
    # Mock data for demo purposes
    return {
        "BTC": 50000.0,
        "ETH": 4000.0,
        "XRP": 1.0
    }

# Seed data
def seed_data():
    db = SessionLocal()
    if not db.query(User).first():
        user = User(username="demo", email="demo@example.com", full_name="Demo User", password_hash=get_password_hash("password"))
        db.add(user)
        db.commit()
        db.refresh(user)

        portfolio = Portfolio(user_id=user.id, assets=str([{"symbol": "BTC", "amount": 1.0}, {"symbol": "ETH", "amount": 10.0}]), total_value=54000.0)
        db.add(portfolio)
        db.commit()

    if not db.query(MarketTrend).first():
        trend = MarketTrend(trend_id="1", name="Bullish", description="Market is trending upwards", impact=0.8)
        db.add(trend)
        db.commit()

    db.close()

seed_data()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
