"""Campus Customs catalogue API."""
import sqlite3
import re
import json
import hashlib
import hmac
import secrets
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
try:
    from .agent import run_chat
    from .models import ChatDependencies, ChatHistoryMessage, ChatReply, ChatRequest, ProductCard
except ImportError:
    from agent import run_chat
    from models import ChatDependencies, ChatHistoryMessage, ChatReply, ChatRequest, ProductCard

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "campus_customs.db"
PRODUCTS_PATH = ROOT / "data" / "products"
TRANSPARENT_PRODUCTS_PATH = ROOT / "data" / "products_transparent"
app = FastAPI(title="Campus Customs API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?", allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])
app.mount("/product-images", StaticFiles(directory=PRODUCTS_PATH), name="product-images")
app.mount("/transparent-product-images", StaticFiles(directory=TRANSPARENT_PRODUCTS_PATH), name="transparent-product-images")

class AccountCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

PBKDF2_ITERATIONS = 600_000
PBKDF2_DIGEST_BYTES = 32

def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS, dklen=PBKDF2_DIGEST_BYTES).hex()
    return f"pbkdf2_sha256${salt}${digest}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, expected = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    actual = hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(actual, expected)

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/api/auth/register", status_code=201)
def register(account: AccountCreate) -> dict:
    first_name, last_name, email = account.first_name.strip(), account.last_name.strip(), account.email.strip().lower()
    if not first_name or not last_name or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(status_code=400, detail="Please provide a valid name and email.")
    if len(account.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if account.password != account.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    password_hash = hash_password(account.password)
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute("INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)", (f"{first_name} {last_name}", email, password_hash, first_name, last_name))
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    return {"id": user_id, "first_name": first_name, "last_name": last_name, "email": email}

@app.post("/api/auth/login")
def login(credentials: LoginRequest) -> dict:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        user = connection.execute("SELECT id, first_name, last_name, email, password_hash FROM users WHERE email = ?", (credentials.email.strip().lower(),)).fetchone()
    if user is None or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"id": user["id"], "first_name": user["first_name"], "last_name": user["last_name"], "email": user["email"]}

@app.get("/api/chat/history/{user_id}", response_model=list[ChatHistoryMessage])
def chat_history(user_id: int) -> list[ChatHistoryMessage]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
    history = []
    for row in rows:
        try:
            products = [ProductCard.model_validate(item) for item in json.loads(row["products_json"] or "[]")]
        except (TypeError, ValueError):
            products = []
        history.append(ChatHistoryMessage(role=row["role"], content=row["content"], products=products))
    return history

@app.post("/api/chat", response_model=ChatReply)
async def chat(request: ChatRequest) -> ChatReply:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        dependencies = ChatDependencies()
        if request.user_id is not None:
            with sqlite3.connect(DATABASE_PATH) as connection:
                connection.row_factory = sqlite3.Row
                user = connection.execute("SELECT id, name, email FROM users WHERE id = ?", (request.user_id,)).fetchone()
            if user:
                dependencies = ChatDependencies(user_id=user["id"], customer_name=user["name"], customer_email=user["email"])
        if request.page_product_id:
            with sqlite3.connect(DATABASE_PATH) as connection:
                product = connection.execute("SELECT name FROM catalogue WHERE product_id = ?", (request.page_product_id,)).fetchone()
            if product:
                dependencies.page_product_id = request.page_product_id
                dependencies.page_product_name = product[0]
        result = await run_chat(request.message.strip(), dependencies)
        if dependencies.user_id:
            with sqlite3.connect(DATABASE_PATH) as connection:
                connection.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", (dependencies.user_id, "user", request.message.strip(), "[]"))
                connection.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", (dependencies.user_id, "assistant", result.reply, json.dumps([item.model_dump() for item in result.products])))
        return result
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))

def _row_to_product(row: sqlite3.Row) -> dict:
    filename = Path(row["image_file_path"]).stem + ".png"
    image_url = "/transparent-product-images/" + filename if (TRANSPARENT_PRODUCTS_PATH / filename).exists() else "/product-images/" + Path(row["image_file_path"]).name
    return {"product_id": row["product_id"], "name": row["name"], "garment_type": row["garment_type"], "description": row["description"], "price": row["price"], "colors": row["colors"], "image_url": image_url}

@app.get("/api/products")
def products() -> list[dict]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT product_id, name, garment_type, description, colors, price, image_file_path FROM catalogue ORDER BY name").fetchall()
    return [_row_to_product(row) for row in rows]

@app.get("/api/products/{product_id}")
def product_detail(product_id: str) -> dict:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT product_id, name, garment_type, description, colors, price, image_file_path FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        inventory = connection.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size", (product_id,)).fetchall()
    product = _row_to_product(row)
    product["inventory"] = [{"size": item["size"], "quantity": item["quantity"]} for item in inventory]
    return product
