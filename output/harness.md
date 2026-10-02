# Campus Customs Database Harness

## Database overview

The database supports the Campus Customs product catalogue, inventory tracking,
customer accounts, and chatbot conversations. The main relationships are:

- `catalogue.product_id` connects a product to its inventory records through
  `inventory.product_id`.
- `users.id` connects a customer account to that customer's messages through
  `chat_messages.user_id`.

## `catalogue`

This is the main product catalogue used to describe and recommend merchandise.

| Field | Why it matters |
|---|---|
| `product_id` | Uniquely identifies a product and links it to inventory. |
| `name` | Gives the product a clear customer-facing name. |
| `garment_type` | Helps classify and filter products, such as hoodies or t-shirts. |
| `description` | Provides product details that can support chatbot recommendations. |
| `colors` | Helps match products to a customer's color preferences. |
| `search_tags` | Provides keywords for matching customer requests to products. |
| `image_file_path` | Locates the product image for visual display or matching. |
| `price` | Supports price comparisons, recommendations, and purchase decisions. |

## `inventory`

This table shows what can actually be purchased at each size.

| Field | Why it matters |
|---|---|
| `id` | Uniquely identifies an inventory record. |
| `product_id` | Connects a size and quantity record to a catalogue product. |
| `size` | Identifies the available garment size. |
| `quantity` | Shows whether the product and size are in stock and how many remain. |

The relationship between `catalogue.product_id` and `inventory.product_id` lets the
shop distinguish products that exist in the catalogue from products that are
currently available to purchase.

## `users`

This table stores customer account information used to associate conversations with
individual customers.

| Field | Why it matters |
|---|---|
| `id` | Uniquely identifies a customer account. |
| `name` | Stores the customer's account name. |
| `email` | Provides the account's email address for account-related communication. |
| `password_hash` | Stores a hashed password rather than a plain-text password. |
| `created_at` | Records when the customer account was created. |
| `first_name` | Supports personalized chatbot messages and customer interactions. |
| `last_name` | Helps identify and personalize the customer's account. |

## `chat_messages`

This table stores the chatbot conversation history.

| Field | Why it matters |
|---|---|
| `id` | Uniquely identifies each message. |
| `user_id` | Connects the message to a customer in `users.id`. |
| `role` | Identifies whether the message came from the user or assistant. |
| `content` | Stores the actual conversation text. |
| `products_json` | Records products shown or recommended in the response. |
| `created_at` | Preserves the time order of the conversation. |

The `users.id` to `chat_messages.user_id` relationship lets the application retrieve
a customer's conversation history and understand which products were recommended.

## Authentication

Users store their first name, last name, email, account metadata, and a password hash
in the `users` table. The `users.id` value identifies the account, while the email is
used to find the account during login. The account fields support identifying and
personalizing a user, and `created_at` records account metadata.

Passwords are never stored as plaintext. During registration, the backend creates a
secure random salt and derives a password digest with PBKDF2-HMAC-SHA256 using
600,000 iterations and a 32-byte derived key. The stored value has the format
`pbkdf2_sha256$salt$hex_digest`.

During login, the backend looks up the user by the normalized email address, parses
the stored algorithm, salt, and digest, and derives a new digest from the submitted
password using the stored salt and the same PBKDF2 settings. It compares the new
digest with the stored digest using a constant-time comparison. Missing users,
unsupported formats, and incorrect passwords receive the same safe invalid-login
response. The seeded test account was updated to this same scheme after a database
backup; no other users or database tables were changed.

## Problem 5 agent and frontend communication

The bottom-right frontend chat widget sends the customer's message as JSON to
`POST /api/chat` on the FastAPI backend. The backend validates the message, runs the
PydanticAI agent, and returns a structured `ChatReply` containing response text and
any matching product cards. The frontend displays the returned reply and shows an
error message if the backend or agent is unavailable.

The agent is defined in `backend/agent.py`. It loads its voice and safety rules from
`backend/prompts/prompt.md`, uses `PORTKEY_API_KEY`, and calls `PORTKEY_MODEL` or the
default `gpt-5.6-luna` through Portkey's OpenAI-compatible endpoint. Its
`search_products` tool queries the existing `catalogue` table and returns at most
six matching `ProductCard` records. Product data and the database schema are not
modified.

Each product card also includes size-level `availability` from the related
`inventory` rows, so the agent can answer questions about available sizes and stock
without treating the catalogue description as the source for inventory.

`backend/tools.py` contains the database search helper. It searches product name,
description, search tags, and garment type, then reads matching size and quantity
rows from `inventory`. `backend/models.py` defines `ProductCard`,
`SizeAvailability`, and `ChatReply`, which keep product recommendations,
inventory details, and the agent response structured. `backend/agent.py` creates the
PydanticAI agent, registers the search tool, and runs the model with the loaded
system prompt. `backend/prompts/prompt.md` supplies the assistant voice, catalogue
grounding rules, and safety guidance.

For direct factual lookups, `get_product_info` queries `catalogue.product_id`,
`catalogue.name`, `catalogue.description`, and `catalogue.price`, returning a
structured `ProductInfo`. These fields identify the product and provide the
authoritative description and price.

`check_stock` uses `catalogue.product_id` to find the product and joins it to
`inventory.product_id`. It reads `inventory.size` and `inventory.quantity`, sums
quantities for overall stock, or returns the quantity for a requested size. Its
structured `StockInfo` includes the product ID and name, requested size when
applicable, that size's quantity, total inventory quantity, and an `in_stock` flag.
These fields let the agent distinguish overall availability from a specific
out-of-stock size without inventing values.

For category searches, the agent places matching `ProductCard` objects in the
`ChatReply.products` list. The frontend keeps that structured list instead of
flattening it into text, renders each product's database-backed image, name, price,
and description in the chat panel, and links each result to the existing
`/products/{product_id}` route. Clicking a chat result therefore opens the same
database-backed product-detail page used by the main Products grid.

## Problem 8 customer memory and context

When login succeeds, the frontend stores the returned user ID, name, and email in
the current browser session. Chat requests include that user ID; the backend looks
up the corresponding `users` row and inserts the user and assistant messages into
`chat_messages`, including structured product results in `products_json`. When a
logged-in customer opens the chat, the frontend loads `/api/chat/history/{user_id}`
and restores those messages. Guests omit the user ID, so their messages are sent to
the agent but are not saved.

The agent receives `ChatDependencies` containing the logged-in customer's ID, name,
and email when available. Requests also include the current product ID when the
chat is opened on a product-detail route. The backend resolves that ID through the
`catalogue` table and passes the product ID and name as request context, allowing
the agent to interpret phrases such as “this product” while continuing to use the
database tools for product facts.

## Problem 9 usability improvements

The Products page now filters the database-backed product list by name, description,
or garment type, filters by garment category, sorts by name or price in either
direction, and provides a clear control. The chat UI distinguishes customer and
assistant messages, scrolls to the newest message, offers starter prompts, and
shows a typing state.

`search_products` now scores matches using exact name, name, garment type, search
tag, and description matches before returning the top six results. `get_product_info`
and `check_stock` return an `AmbiguousProduct` result when several plausible
products match a non-exact lookup, allowing the agent to ask for clarification.
Exact names and product-page context continue to resolve normally.

## Problem 12 audit trail and safety

I added an append-preserving audit trail at `output/audit_trail.json`. Each record
has `time`, `tool_name`, short `args`, and a short `result`. Agent runs also record
`stopped_reason`, such as `completed` or a failed run reason. Earlier records stay
in the file when a new agent run is made.

The audit wrapper records calls to `search_products`, `get_product_info`, and
`check_stock`. It also records the final `agent_run`. The logged values are kept
short and the customer dependency context is not written to the audit record.

## Structured agent models

The structured fields make the agent return predictable information instead of
only free-form text. They also give the frontend the real catalogue and inventory
values it needs to display product cards and shopping answers.

| Model and field | Why it is useful |
|---|---|
| `ProductCard.product_id` | Identifies the real product and lets the frontend link to its detail page. |
| `ProductCard.name` | Displays the catalogue product name in search results and cards. |
| `ProductCard.price` | Displays the database-backed price and prevents the assistant from inventing one. |
| `ProductCard.description` | Gives the frontend short real product information. |
| `ProductCard.image_url` | Tells the frontend which existing product image to display. |
| `ProductCard.availability` | Carries size-level stock information with the product card. |
| `SizeAvailability.size` | Identifies each size returned from `inventory.size`. |
| `SizeAvailability.quantity` | Shows the actual quantity from `inventory.quantity`, including zero when out of stock. |
| `ProductInfo.product_id` | Identifies the product used for a direct factual lookup. |
| `ProductInfo.name` | Confirms which catalogue product the answer describes. |
| `ProductInfo.description` | Provides the authoritative catalogue description. |
| `ProductInfo.price` | Provides the authoritative catalogue price. |
| `AmbiguousProduct.query` | Preserves the unclear product request. |
| `AmbiguousProduct.candidates` | Gives the customer the possible product names to choose from. |
| `AmbiguousProduct.clarification_needed` | Tells the agent that it must ask for clarification instead of choosing arbitrarily. |
| `StockInfo.product_id` | Identifies the product whose inventory was checked. |
| `StockInfo.name` | Makes the stock response clear to the customer. |
| `StockInfo.size` | Records the requested size when the lookup is size-specific. |
| `StockInfo.quantity` | Reports the requested size quantity or the total quantity when no size is supplied. |
| `StockInfo.total_quantity` | Reports the sum of all inventory sizes. |
| `StockInfo.in_stock` | Gives a simple true/false availability result. |
| `ChatReply.reply` | Holds the concise customer-facing assistant response. |
| `ChatReply.products` | Holds structured product cards that the frontend can render. |
| `ChatDependencies.user_id` | Connects a logged-in chat to the user account and saved history. |
| `ChatDependencies.customer_name` | Lets the agent personalize a response when appropriate. |
| `ChatDependencies.customer_email` | Identifies the logged-in customer context without exposing it in the response. |
| `ChatDependencies.page_product_id` | Identifies the product page the customer is viewing. |
| `ChatDependencies.page_product_name` | Helps the agent understand phrases such as “this product.” |
| `ChatRequest.message` | Carries the customer's chat message to FastAPI. |
| `ChatRequest.user_id` | Optionally identifies the logged-in user for memory. |
| `ChatRequest.page_product_id` | Optionally passes the current product page context. |
| `ChatHistoryMessage.role` | Distinguishes a user message from an assistant message. |
| `ChatHistoryMessage.content` | Stores the conversation text loaded into the chat. |
| `ChatHistoryMessage.products` | Restores product cards shown in previous assistant responses. |

## Problem 12 tools and safety rules

`search_products(query)` searches the existing `catalogue` by product name,
description, search tags, garment type, and price constraints. It ranks matches by
relevance, returns at most six `ProductCard` objects, and reads related inventory
rows for each card.

`get_product_info(product_query)` returns a structured `ProductInfo` using the
catalogue description and price. If several non-exact products match, it returns
`AmbiguousProduct` so the agent asks the customer to clarify.

`check_stock(product_query, size)` reads `inventory` through the matched
`catalogue.product_id`. It returns overall stock or the requested size quantity in
`StockInfo`, and it clearly supports out-of-stock results.

The prompt tells the agent to use real catalogue and inventory information only,
never make up products, prices, descriptions, sizes, quantities, availability, or
policies, and use the relevant database tool for factual questions. It must not
expose passwords, payment details, emails, account details, chat history, or other
private information. When a request is unclear or ambiguous, it asks for
clarification instead of guessing.

## Main specifications and run commands

The agent uses `PORTKEY_MODEL` when it is configured, or the default model
`gpt-5.6-luna`, through Portkey's OpenAI-compatible endpoint. The PydanticAI agent
uses `retries=1`. Product searches return at most six results; direct ambiguous
lookups inspect up to twelve initial matches and list up to six candidate names.

From the project root, the frontend can be built with `npm run build` from the
`frontend/` folder. The frontend development server can be started with
`npm run dev`. The backend can be run from `backend/` with:

```text
uvicorn main:app --reload --port 8000
```
