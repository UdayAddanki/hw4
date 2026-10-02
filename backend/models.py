from pydantic import BaseModel, Field


class ProductCard(BaseModel):
    product_id: str
    name: str
    price: float
    description: str
    image_url: str
    availability: list["SizeAvailability"] = Field(default_factory=list)


class SizeAvailability(BaseModel):
    size: str
    quantity: int


class ProductInfo(BaseModel):
    product_id: str
    name: str
    description: str
    price: float


class AmbiguousProduct(BaseModel):
    query: str
    candidates: list[str]
    clarification_needed: bool = True


class StockInfo(BaseModel):
    product_id: str
    name: str
    size: str | None = None
    quantity: int
    total_quantity: int
    in_stock: bool


class ChatReply(BaseModel):
    reply: str = Field(description="A concise, helpful response to the customer.")
    products: list[ProductCard] = Field(default_factory=list)


class ChatDependencies(BaseModel):
    user_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    page_product_id: str | None = None
    page_product_name: str | None = None


class ChatRequest(BaseModel):
    message: str
    user_id: int | None = None
    page_product_id: str | None = None


class ChatHistoryMessage(BaseModel):
    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)
