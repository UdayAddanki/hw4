import sqlite3
import re
from pathlib import Path

try:
    from .models import AmbiguousProduct, ProductCard, ProductInfo, StockInfo
except ImportError:
    from models import AmbiguousProduct, ProductCard, ProductInfo, StockInfo

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "data" / "campus_customs.db"
TRANSPARENT_PRODUCTS_PATH = ROOT / "data" / "products_transparent"


def _image_url(image_file_path: str) -> str:
    filename = Path(image_file_path).stem + ".png"
    return "/transparent-product-images/" + filename if (TRANSPARENT_PRODUCTS_PATH / filename).exists() else "/product-images/" + Path(image_file_path).name


def _find_products(connection: sqlite3.Connection, product_query: str) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    query = product_query.strip()
    return connection.execute("SELECT product_id, name, description, price FROM catalogue WHERE lower(name) LIKE lower(?) OR lower(search_tags) LIKE lower(?) OR lower(garment_type) LIKE lower(?) ORDER BY name LIMIT 12", (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()


def _single_product(connection: sqlite3.Connection, product_query: str) -> tuple[sqlite3.Row | None, AmbiguousProduct | None]:
    rows = _find_products(connection, product_query)
    exact = [row for row in rows if row["name"].lower() == product_query.strip().lower()]
    if len(exact) == 1:
        return exact[0], None
    if len(rows) > 1:
        return None, AmbiguousProduct(query=product_query, candidates=[row["name"] for row in rows[:6]])
    return (rows[0], None) if rows else (None, None)


def get_product_info(product_query: str) -> ProductInfo | AmbiguousProduct | None:
    """Look up the authoritative description and price for one product."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        row, ambiguity = _single_product(connection, product_query)
    if ambiguity:
        return ambiguity
    if row is None:
        return None
    return ProductInfo(product_id=row["product_id"], name=row["name"], description=row["description"], price=row["price"])


def check_stock(product_query: str, size: str | None = None) -> StockInfo | AmbiguousProduct | None:
    """Look up total or size-level stock for one product from inventory."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        row, ambiguity = _single_product(connection, product_query)
        if ambiguity:
            return ambiguity
        if row is None:
            return None
        total = connection.execute("SELECT COALESCE(SUM(quantity), 0) FROM inventory WHERE product_id = ?", (row["product_id"],)).fetchone()[0]
        if size and size.strip():
            quantity_row = connection.execute("SELECT quantity FROM inventory WHERE product_id = ? AND lower(size) = lower(?)", (row["product_id"], size.strip())).fetchone()
            quantity = quantity_row[0] if quantity_row else 0
        else:
            quantity = total
    return StockInfo(product_id=row["product_id"], name=row["name"], size=size.strip() if size else None, quantity=quantity, total_quantity=total, in_stock=quantity > 0)


def search_products(query: str) -> list[ProductCard]:
    """Find catalogue products relevant to a customer query."""
    price_match = re.search(r"\b(under|below|less\s+than)\s*\$?\s*(\d+(?:\.\d+)?)", query, re.IGNORECASE)
    price_operator = None
    price_amount = None
    if price_match:
        price_operator = "<=" if price_match.group(1).lower() == "under" else "<"
        price_amount = float(price_match.group(2))
        query = query[:price_match.start()] + query[price_match.end():]
    stop_words = {"what", "do", "you", "have", "any", "the", "a", "an", "for", "is", "are", "can", "i", "need", "looking"}
    raw_terms = [term.strip().lower().strip("?!.,") for term in query.split() if term.strip() and term.strip().lower().strip("?!.,") not in stop_words]
    terms = []
    for term in raw_terms:
        terms.append(term)
        if term.endswith("ies"):
            terms.append(term[:-1])
            terms.append(term[:-3] + "y")
        elif term.endswith("s") and len(term) > 3:
            terms.append(term[:-1])
    if not terms and price_amount is None:
        return []
    text_clauses = []
    values: list[str] = []
    for term in terms[:8]:
        pattern = f"%{term}%"
        text_clauses.append("(lower(name) LIKE ? OR lower(description) LIKE ? OR lower(search_tags) LIKE ? OR lower(garment_type) LIKE ?)")
        values.extend([pattern] * 4)
    clauses = [f"({' OR '.join(text_clauses)})"] if text_clauses else []
    if price_amount is not None:
        clauses.append(f"price {price_operator} ?")
        values.append(price_amount)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"SELECT product_id, name, price, description, image_file_path, garment_type, search_tags FROM catalogue WHERE {' AND '.join(clauses)}",
            values,
        ).fetchall()
        def relevance(row: sqlite3.Row) -> int:
            name, garment, tags, description = row["name"].lower(), row["garment_type"].lower(), row["search_tags"].lower(), row["description"].lower()
            score = 0
            for term in terms:
                if name == term: score += 100
                if term in name: score += 50
                if term in garment: score += 30
                if term in tags: score += 20
                if term in description: score += 10
            return score
        rows = sorted(rows, key=lambda row: (-relevance(row), row["name"]))[:6]
        products = []
        for row in rows:
            inventory = connection.execute(
                "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size",
                (row["product_id"],),
            ).fetchall()
            products.append(ProductCard(
                product_id=row["product_id"],
                name=row["name"],
                price=row["price"],
                description=row["description"],
                image_url=_image_url(row["image_file_path"]),
                availability=[{"size": item["size"], "quantity": item["quantity"]} for item in inventory],
            ))
    return products
