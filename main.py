import os
import stripe
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, Field


# Load environment variables
load_dotenv()

# Set up Stripe API keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

if not STRIPE_SECRET_KEY:
    raise ValueError("⚠️ Stripe Secret Key is missing! Check your .env file.")

stripe.api_key = STRIPE_SECRET_KEY  # Use only secret key for API calls

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DATABASE_URL = "postgresql://postgres:12345@localhost/SIGNUP"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# Create Tables
Base.metadata.create_all(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone_number: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Signup
@app.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        password=hashed_password
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists or invalid data.")
    return {"message": "User created successfully!"}

# User Login
@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    return {"message": f"Welcome {db_user.username}!", "username": db_user.username}

# Setting up templates and static files
templates = Jinja2Templates(directory="public")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("Index.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@app.get("/updatedindex", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("updatedindex.html", {"request": request})

@app.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    return templates.TemplateResponse("change-password.html", {"request": request})
@app.get("/moneyform", response_class=HTMLResponse)
async def change_password_page(request: Request):
    return templates.TemplateResponse("moneyform.html", {"request": request})
@app.get("/footwareblanket", response_class=HTMLResponse)
async def change_password_page(request: Request):
    return templates.TemplateResponse("footwareblanket.html", {"request": request})

@app.post("/change-password")
async def change_password(data: dict, db: Session = Depends(get_db)):
    username = data.get("username")
    new_password = data.get("newPassword")

    if not username or not new_password:
        raise HTTPException(status_code=400, detail="Missing username or password")

    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        db_user.password = pwd_context.hash(new_password)
        db.commit()
        db.refresh(db_user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Password updated successfully"}

# Other pages
@app.get("/aboutus", response_class=HTMLResponse)
async def about_us_page(request: Request):
    return templates.TemplateResponse("aboutus.html", {"request": request})

@app.get("/gallery", response_class=HTMLResponse)
async def gallery_page(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request})

@app.get("/services", response_class=HTMLResponse)
async def services_page(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})
@app.get("/childkit", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("childkit.html", {"request": request})
@app.get("/success", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})
@app.get("/cancel", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("cancel.html", {"request": request})

# Payment Request Model
class PaymentRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount must be greater than 0")  # Prevents zero/negative values



@app.post("/create-checkout-session")
async def create_checkout_session(payment: PaymentRequest):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": "Donation"},
                    "unit_amount": payment.amount * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Donation for Footwear & Blankets
class DonationRequest(BaseModel):
    footwear_count: int = 0
    blanket_count: int = 0

FOOTWEAR_PRICE = 500
BLANKET_PRICE = 450

@app.post("/create-footwear-blanket-checkout")
async def create_footwear_blanket_checkout(data: DonationRequest):
    try:
        line_items = []

        if data.footwear_count > 0:
            line_items.append({
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": "Footwear Donation"},
                    "unit_amount": FOOTWEAR_PRICE * 100,
                },
                "quantity": data.footwear_count,
            })

        if data.blanket_count > 0:
            line_items.append({
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": "Blanket Donation"},
                    "unit_amount": BLANKET_PRICE * 100,
                },
                "quantity": data.blanket_count,
            })

        if not line_items:
            raise HTTPException(status_code=400, detail="No items selected")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )

        return {"checkout_url": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class DonationRequest(BaseModel):
    name: str
    phone: str
    address: str
    pincode: str
    quantity: int

@app.post("/donate-education-kit")  
async def donate_education_kit(donation: DonationRequest):
    try:
        total_amount = donation.quantity * 2500  # Each kit costs 2500 INR

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "inr",  # Set currency to INR
                    "product_data": {
                        "name": "Education Kit (Books, Compass, Uniform, Shoes)"
                    },
                    "unit_amount": total_amount * 100  # Convert to paise
                },
                "quantity": 1
            }],
            mode="payment",
            success_url="https://yourwebsite.com/success",
            cancel_url="https://yourwebsite.com/cancel",
            metadata={
                "name": donation.name,
                "phone": donation.phone,
                "address": donation.address,
                "pincode": donation.pincode,
                "quantity": donation.quantity
            }
        )
        
        return {"url": checkout_session.url}

    except Exception as e:
        return {"error": str(e)}