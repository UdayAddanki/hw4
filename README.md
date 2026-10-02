Campus Customs
Campus Customs is a Yale merchandise storefront with an AI shopping assistant. The site lets users browse the product catalogue, search and filter products, view product details, create an account, log in, and ask the AI assistant questions about products, prices, inventory, and recommendations.
Features
- Browse the Campus Customs product catalogue
- Search, filter, and sort products
- View individual product details, including price, colors, sizes, and inventory
- Create an account and log in securely
- Ask the AI shopping assistant about products
- Search the catalogue through the AI assistant
- Display AI search results as clickable product cards
- Check product price and inventory through the database
- Save chat history for logged-in users
- Use the current product as context when chatting from a product page
- Append agent activity to an audit trail
- Responsive Yale-inspired storefront design
Tech Stack
Frontend
- React
- TypeScript
- Vite
Backend
- FastAPI
- Pydantic
- PydanticAI
- OpenAI
- SQLite
Project Structure
hw4/
├── backend/
│   ├── agent.py
│   ├── main.py
│   ├── models.py
│   ├── tools.py
│   └── prompts/
├── frontend/
├── output/
├── AI_prompts.md
├── requirements.txt
├── .env.example
└── .gitignore

Setup
The course data pack provides the local SQLite database and product images used by the application. Place the provided data/ folder in the project root.
Create a Python environment and install the backend dependencies:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create a local .env file based on .env.example and add the required Portkey API credentials.
For the frontend:
cd frontend
npm install

Run the Application
Start the backend from the project root:
python3 -m uvicorn backend.main:app --reload --port 8000

In a second terminal, start the frontend:
cd frontend
npm run dev

The frontend runs at:
http://localhost:5173

The backend runs at:
http://127.0.0.1:8000

Testing
To verify the frontend production build:
cd frontend
npm run build

To check that the Python backend compiles:
cd ..
python3 -m compileall backend

Documentation
- AI_prompts.md contains the prompts used while building the project.
- output/harness.md documents the agent, database, tools, models, safety rules, and system specifications.
- output/usability.md documents the usability improvements.
- output/design.md documents the design decisions.
- output/app_check.html documents the application checks completed for the final testing.
- output/audit_trail.json contains the append-only agent audit trail.