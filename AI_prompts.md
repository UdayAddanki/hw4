# AI Prompt Log

This file records the prompts used for each Homework 4 problem in sequential order.
Each section includes the problem number and title, the prompt typed, and any
follow-up prompt with an explanation of what was missing from the first prompt.

## Problem 1 — Create the Prompt Log

### Prompt(s)

> i will give pompts for reach problem, we will save it under AI prompts md file in a sequential order. For now create AI_prompts.md file and we will kep it update as we work on each problem, each section must include - problem number and title, prompt I typed, one follow up prompt if give any (and a sentence on what was lacking after first). The running application, database changes, and screenshots will serve as evidence of my work, so I do not need a separate proof essay

No follow-up prompt was needed.

## Problem 2 — Analyze the Campus Customs Database

### Prompt(s)

> Problem 2 is about analyzing the database and understand the fields of each table.
>
> I analyzed `data/campus_customs.db` and want you to create `output/harness.md` based on my analysis. The database has four relevant tables: `catalogue`, `inventory`, `users`, and `chat_messages`, with the fields and meanings I provided.
>
> Create `output/harness.md` using this analysis. For each table and field, add a short explanation of why it matters for the Campus Customs shop or chatbot. Also mention the key relationships between the tables, especially `catalogue.product_id` and `inventory.product_id`, and `users.id` and `chat_messages.user_id`.
>
> Keep it clear and concise. Don't modify the database. We'll build on this harness in the later problems.

No follow-up prompt was needed.

## Problem 3 — Set Up the Campus Customs React Frontend

### Prompt(s)

> Let's start Problem 3 one step at a time. For this first step, set up the React + Vite + TypeScript frontend for Campus Customs.
>
> Create a clean site structure with a top navigation bar linking to Home, Products, About Us, Log in, and Create account. Create working routes/pages for each section. For now, Products, Log in, and Create account can have simple placeholder content. Do not build the database integration, individual product pages, chat interface, or FastAPI backend yet.
>
> For the Home and About Us pages, use the copy I provided. Use this copy as provided. Do not copy text from the Yale Bulldog Blue website.
>
> Give the site a polished Campus Customs/Yale-inspired visual style, with a clean, premium collegiate feel. Focus on the layout, typography, navigation, and responsive design at this stage.
>
> Make sure the frontend runs successfully before considering this step complete.

No follow-up prompt was needed. The local environment does not currently have Node.js or npm installed, so the project files were created but the build could not be run here.

### Follow-up Prompt

> I installed Node.js and npm and ran `npm install` successfully. I then ran `npm run build`, and the build failed because TypeScript cannot find the React type declarations. The errors specifically mention missing declarations for `react`, `react/jsx-runtime`, and `JSX.IntrinsicElements`. Please diagnose and fix the dependency/configuration issue in the existing React + Vite + TypeScript frontend. Install or update only the dependencies/configuration needed to resolve the TypeScript errors. Do not change the application design, copy, routes, or start Problem 3's database integration yet. After fixing it, run `npm run build` again and confirm whether the build succeeds. If it succeeds, do not start the development server or move on to another Problem 3 task yet.

The missing `@types/react` and `@types/react-dom` development dependencies were added to provide React, JSX runtime, and intrinsic-element TypeScript declarations. The standard `vite-env.d.ts` declaration was also added so TypeScript recognizes the imported CSS file.

### Follow-up Prompt — Connect Products to the Database

> Let's continue with Problem 3. The frontend is now set up and `npm run build` succeeds. For this step, connect the Products page to the existing Campus Customs SQLite database at `data/campus_customs.db`.
>
> Create or extend the simple FastAPI backend in `backend/main.py` so it can read the `catalogue` table and provide the product information needed by the frontend. The Products page should retrieve the products from the backend and display them as a clean responsive product grid with the actual database image, name, price, and short description. Handle loading and error states.
>
> Do not build the individual product-detail pages, chat interface, or PydanticAI agent yet. Inspect the schema first, do not modify the database or product image files, run `npm run build`, check the backend, and update `AI_prompts.md`.

The database schema was inspected first. A SQLite-backed FastAPI catalogue endpoint, static product-image serving, and a frontend product grid with loading/error states were added.

### Follow-up Prompt — Complete the Rest of Problem 3

> We have completed the first two parts of Problem 3. Please now complete the rest of Problem 3 in one pass: add clickable product cards and database-backed product-detail pages with image, description, price, colors, sizes, and inventory stock; add a frontend-only bottom-right chat stub with a launcher, panel, messages, input, send button, and placeholder response; preserve the existing pages and navigation; do not modify the database or images; do not build the PydanticAI shopping agent or later Problem 4 functionality; run the frontend build and backend checks; verify the real inventory data and chat interaction; and update `AI_prompts.md` with what was implemented and verified.

Product-detail routing, catalogue/inventory API access, real size and stock display, and the frontend-only chat stub were added. Verification is in progress.

## Problem 4 — Account Flow, First Half

### Prompt(s)

> I want to work on Problem 4, first half first. Please build the normal Create Account and Log In flow for the Campus Customs site. For Create Account, I want fields for first name, last name, email, password, and confirm password. A new account should be saved in the existing `users` table, with passwords stored securely as hashes and never as plain text. For Log In, users should log in with their email and password, and the backend should check the password against the stored password hash and handle invalid credentials safely.
>
> Before making changes, look at the existing frontend, backend, and `users` table so this fits with what we already built. Reuse the existing structure. Do not change Products, product-detail, or chat functionality. Run `npm run build`, check the backend, verify a newly created user is saved with a password hash, and update `AI_prompts.md` with what was implemented.

Initially implemented bcrypt-backed registration and login endpoints, connected the existing account routes to forms, and verified the flow against an isolated database copy. The authentication scheme was later standardized on PBKDF2-HMAC-SHA256.

### Problem 4 — Second Half: Account Testing

#### Prompt

> Let's continue with Problem 4
>
> First, test the existing test account:
>
> - Email: `test@campuscustoms.yale.edu`
> - Password: `password`
>
> Verify that this account can successfully log in through the Campus Customs site.
>
> Then create a completely new account through the Create Account page using a new test email. Verify that the account is saved in the `users` table and that the new account can successfully log in afterward.
>
> Please don't change the existing authentication implementation unless you find an actual issue during testing.
>
> Don't start add any AI/PydanticAI functionality.

The first-half prompt requested the account implementation, while this follow-up added explicit testing of the seeded account, creation of a new account, database persistence, and subsequent login.

### Follow-up Prompt — Use PBKDF2-SHA256 for New Accounts

> okay use it

The agreed suggested value of 600,000 iterations was applied to PBKDF2-HMAC-SHA256
registration and verification. New hashes use the existing three-part format with a
32-byte digest, secure random salt, and constant-time comparison.

### Follow-up Prompt — Standardize the Seeded Account Hash

> Let's finish Problem 4 by standardizing the application on our PBKDF2-HMAC-SHA256 implementation: 600,000 iterations, a 32-byte derived key, hexadecimal digest, and securely generated salt. Back up `data/campus_customs.db` first, change only the unusable hash for `test@campuscustoms.yale.edu`, do not change other users, product data, or tables, then verify the seeded account, create and verify a new account, test wrong passwords, run `npm run build`, and update the harness with the password-protection facts.

Created `data/campus_customs.db.backup`, updated only the seeded test user's hash,
created a new PBKDF2 account, verified both logins and safe failures for wrong
passwords, confirmed table counts were unchanged, and confirmed the frontend build
passed.

## Problem 8 — Customer Memory

### Prompt

> Let's continue with Problem 8, customer memory. Please look at the existing authentication, chat, agent, database, frontend, and product-detail flow first, and build this on top of what we already have. When a customer is logged in, save their chat history in the existing `chat_messages` table and load that history when they return. The history should be tied to the logged-in user using the existing `users` relationship. The agent should also know who is chatting when the user is logged in. Pass the customer's name and email to the agent through the agent dependencies or another clear pattern that fits the existing PydanticAI setup. Guests should still be able to use the chat, but their chat history does not need to be saved to the database. Also pass enough page context to the agent so that if a customer is on a specific product page and asks something like "do you have this in pink?", the agent knows which product they are referring to. Use the existing product-detail page context and do not invent product information. Make sure chat history is loaded when a logged-in customer returns to the chat, and new messages are saved for that user. Do not save guest chat history. Use the existing `users` and `chat_messages` tables. Do not create unnecessary new tables or modify the database schema unless the existing schema genuinely cannot support the requirement. Update `output/harness.md` to explain how logged-in user chat history is stored and loaded, which customer fields the agent receives, how guest chats are handled, and how page/product context is passed to the agent. Update `AI_prompts.md` with this Problem 8 prompt and a short note about what was implemented and verified. Test both logged-in and guest behavior. Also test the product-page context by opening a product and asking a question that refers to "this" product. Run the backend checks and `npm run build`.

The existing `users` and `chat_messages` tables now support logged-in chat history. The frontend sends the logged-in user ID and product-page context, loads saved history, and leaves guest chats unsaved. The backend passes customer and product context into the PydanticAI run and stores both user and assistant messages for logged-in users.

### Final Problem 4 Verification

The login flow was also manually verified through the Campus Customs website. The
existing account `test@campuscustoms.yale.edu` logged in successfully and displayed
“Welcome, Test.” The new account `udayaddanki1995@gmail.com` also logged in
successfully with its created password and displayed “Welcome back, Uday.”

## Problem 5 — PydanticAI Agent Backend

### Prompt

> Let's start Problem 5, PydanticAI agent backend. Before making changes, inspect the existing Campus Customs project, including the current FastAPI backend, frontend chat widget, database, Python dependencies, and existing project structure.
>
> Based on the Problem 5 requirements, implement the PydanticAI agent backend and connect it to the existing frontend chat widget.
>
> The FastAPI app should remain in:
>
> `backend/main.py`
>
> Create the following files next to it:
>
> - `backend/prompts/prompt.md` for the system prompt
> - `backend/agent.py` for the PydanticAI agent and wiring
> - `backend/tools.py` for tools the agent can call
> - `backend/models.py` for Pydantic/PydanticAI structured types
>
> In `backend/main.py`, expose a chat route so a message from the existing website chat widget is sent to the PydanticAI agent and the agent's reply is returned to the frontend.
>
> once you do this, then follow these instructions -
>
> - Put the initial Campus Customs voice and safety basics in `backend/prompts/prompt.md`.
> - Start or update the structured types in `backend/models.py` for chat replies and product cards as needed.
> - Update `output/harness.md` to explain how the frontend communicates with FastAPI and how the agent is loaded using the prompt file and model.
> - Make sure the backend can run from the `backend/` folder using:
> ```
> uvicorn main:app --reload --port 8000
> ```
>
> Use the existing database and project structure. Do not modify existing product data, authentication behavior, or database schema.
>
> Connect the real agent to the existing bottom-right chat widget, replacing the current placeholder response.
>
> Before finishing, verify the backend imports and runs, test the chat route with a simple message, verify the frontend build, and verify that the frontend chat can receive a response from the agent.
>
> Update `AI_prompts.md` with this Problem 5 prompt and a concise implementation note.
>
> If something required by Problem 5 is unclear from the existing project, inspect the project first and tell me what you found before making an unnecessary assumption.

The PydanticAI agent, prompt file, product-search tool, structured reply models, FastAPI chat route, and frontend chat integration were added. The agent uses the existing catalogue and inventory tables without changing the database, product data, authentication, or frontend layout. Backend imports passed, the frontend build passed, and the live frontend chat was verified with catalogue and inventory results, including the Basic Hoodie Big Yale sizes and quantities.

### Follow-up Prompt — Include Inventory in Product Answers

> I tested the real Problem 5 agent with: “What sizes are available for the Basic Hoodie Big Yale?” The agent found the correct catalogue product, but responded that the catalogue listing does not specify available sizes. Our database has a separate `inventory` table with size and quantity information. Please inspect the current Problem 5 tools and database queries. If the current tool only searches `catalogue`, update it so the agent can retrieve relevant inventory information from `inventory` for size or availability questions. Use the existing schema and do not modify the database. Keep the current PydanticAI architecture and frontend unchanged unless a small supporting change is necessary. Test “Do you have any Yale hoodies?” and “What sizes are available for the Basic Hoodie Big Yale?”, run backend checks and `npm run build`, and update this prompt log.

The product-search tool now queries the related `inventory` rows and includes size and quantity data in each structured product card. The agent prompt now instructs it to use that availability data for size and stock questions.

## Problem 6 — Product Information and Stock Tools

### Prompt

> Let's continue with Problem 6, tools for product info and stock. Please look at the existing Problem 5 agent, tools, models, database, and prompt first and then implement Problem 6 using what we already have. The agent tools need to look up real information from `data/campus_customs.db` for product description, price, how many are in stock, and size-level stock when the customer asks for a specific size. The agent should always use the database for prices and quantities and should not make up prices or stock numbers. If a size is out of stock, it should clearly say that. Expand `backend/prompts/prompt.md` so the agent knows when to call these tools for price and stock questions. Add or update the return types in `backend/models.py` so the tool results are structured and include the fields actually needed for these lookups. Use the existing `catalogue` and `inventory` tables. Do not modify the database or its data. Update `output/harness.md` with each tool and explain which model fields are used for the lookup results and why those fields are useful. Test the agent with questions covering product description, price, overall stock, and size-level stock, including an out-of-stock size if there is one in the database. Make sure the backend still runs, `npm run build` still succeeds, and the existing frontend chat continues to work. Update `AI_prompts.md` with this Problem 6 prompt and a short note about what was implemented and verified.

No follow-up prompt was needed. The agent now has focused `get_product_info` and
`check_stock` database tools in addition to product search. Live chat verification
confirmed correct database-backed answers for product price, total stock, and
size-level stock questions, including out-of-stock handling. The backend/import
checks and frontend build also passed.

## Problem 7 — Chat Search That Updates the Page

### Prompt

> Let's continue with Problem 7, chat search that updates the page. Please build this using the existing Problem 5 and Problem 6 agent, tools, models, and frontend. First look at how the current chat and product cards work so we don't break anything we already built. When a customer asks something like "what hoodies do you have?", the agent should search the catalogue and return structured product matches. The frontend should then use those results to dynamically show the matching products as product cards on the website. Each product card should show the actual product image, name, price, and short information, using the existing database data. Do not invent product information. This should work as an API flow where the agent returns structured product matches and the frontend renders those products on the page. Also make sure the product cards returned through chat behave the same way as the product cards we built in Problem 3. When I click one of the products returned by the chat, it should open the existing single-product detail page with the large image and full product information. Update `backend/prompts/prompt.md` so the agent knows when a user is asking for a category or type of product and should return matching products for the frontend. Update `output/harness.md` to explain how the agent's structured search results reach the frontend and how the frontend turns them into clickable product cards. Keep the existing catalogue and inventory as the source of truth. Do not modify the database or product images. Test the feature with a question like "what hoodies do you have?" and verify that matching product cards appear on the page. Click at least one of those cards and verify that the existing product-detail page opens correctly. Also run the backend checks and `npm run build`. Update `AI_prompts.md` with this Problem 7 prompt and a short note about what was implemented and verified.

The chat now preserves structured product matches from `ChatReply.products`, renders
database-backed image/name/price/description cards, and links each result to the
existing product-detail route. Live website verification confirmed that “What hoodies
do you have?” displayed the correct matching cards and that clicking a returned card
opened the existing product-detail page. Backend checks and the frontend build also
passed.

## Problem 8 — Follow-up: Add Log Out for Memory Testing

### Prompt

> I want to finish testing Problem 8, but I noticed there is currently no visible Log out option in the Campus Customs site. Please inspect the existing authentication/frontend implementation and check how the logged-in user session is currently handled. If the Log out functionality is missing, add a simple Log out option to the existing account/navigation area. It should clear the logged-in user session and return the user to the normal logged-out state so I can test guest chat behavior. Do not change the authentication implementation or database schema. Do not change the existing login or registration flow. After adding it, run `npm run build` and verify that the existing logged-in chat memory still works. Do not start Problem 9. Update `AI_prompts.md` only if this requires an actual Problem 8 follow-up, and explain what was changed.

The navigation now shows a Log out control only when the frontend session contains a
logged-in user. It clears `campus_customs_user`, returns to the home page, and restores
the logged-out navigation state without changing authentication or the database.

## Problem 9 — Usability Improvements

### Prompt

> Let's work on Problem 9. I want to implement these 4 usability improvements that we identified from the current site.
>
> 1. Front-end: Improve product browsing. The Products page currently shows all 102 products but there is no way to search, filter, or sort them. Add a simple product search/filter experience so customers can find products more easily. At minimum, I want: search by product name or relevant product information, filter by garment type/category, sort by price, low to high and high to low, and a clear/reset option. Use the existing catalogue data. Do not invent any product information.
>
> 2. Front-end: Improve the chat shopping experience. Improve the current chat UI so it is easier for a customer to use. Please add the below things: clear visual distinction between customer and assistant messages, automatic scrolling to the newest message, a few clickable starter prompts when the chat is empty, such as "Show me Yale hoodies", "Find me a Yale gift", and "What do you have under $50?", and a clear loading/typing state while the assistant is responding. Keep the existing chat functionality, product cards, chat memory, and product-page context working.
>
> 3. Agent/backend: Improve product search relevance. The current `search_products` tool can return broadly matching products, but the results are mainly ordered alphabetically. Improve the search so the most relevant products are returned first. Use the existing catalogue fields and make the ranking prioritize things like exact product name matches, product name matches, garment type matches, search tag matches, and description matches. The goal is that when a customer asks for a specific type of product, the most relevant products appear first. Do not change the database schema.
>
> 4. Agent/backend: Handle ambiguous product names more safely. The current product lookup can select one product when a customer request could refer to multiple products. Improve this so that when a request is ambiguous, especially for price or stock questions, the agent does not silently choose an arbitrary product. It should ask the customer to clarify which product they mean when there are multiple plausible matches. For example, if the customer asks "How much is the Yale hoodie?" and there are multiple possible Yale hoodies, the assistant should clarify which hoodie they mean before giving a price. Make sure exact product names still work normally and existing product-page context still works.
>
> Before making changes, inspect the existing frontend, backend, agent, tools, models, and prompt so these improvements fit into what we already built. Do not break Problems 3 through 8, including authentication and logout, product catalogue and detail pages, chat memory, guest chat, chat product cards, product-page context, inventory and size availability, and the existing PydanticAI structure. Use the existing project structure and database.
>
> After implementing everything, run `npm run build`, check that the backend imports/runs, test product search/filter/sort, test chat starter prompts and chat UI, test normal and ambiguous product searches, and test exact product names and product-page context. Update `AI_prompts.md` with this actual prompt and a short note about what was implemented.

The Products page now supports search, category filtering, price sorting, and reset. The chat has distinct message styling, auto-scroll, starter prompts, and a typing state. Product search uses relevance scoring, while ambiguous factual lookups return candidate names for clarification. Backend imports and `npm run build` were verified.

### Follow-up Prompt — Apply Price Constraints in Product Search

> I found an issue while testing the Problem 9 chat improvement. When I click the starter prompt: "What do you have under $50?" the agent responds that there are no catalogue items under $50, but the catalogue has T-shirts priced at $32. Please fix this properly in the backend/tool rather than just changing the wording. Make `search_products` understand constraints such as under/below/less than with different price amounts, apply the constraint to the actual `catalogue.price` field, preserve relevance ranking, and support constraints combined with product types. Do not hardcode the $50 example or change the database. Test under $50, normal hoodie search, hoodies under $70, and the exact Basic Hoodie Big Yale price lookup. Do not start Problem 10. Run backend checks and `npm run build`, and update the Problem 9 note if needed.

The search tool now parses generic “under”, “below”, and “less than” price constraints and applies them to `catalogue.price` before relevance ranking. The backend checks and frontend build were rerun.

### Follow-up Prompt — Problem 9 Usability Documentation

> I want to finish the Problem 9 documentation.
>
> Please create/update `output/usability.md` with the following content exactly. Keep the wording and structure as written. Do not rewrite it.
>
> Problem 9: Usability Improvements
>
> 1. Product Browsing - I added a search bar, garment-type filters, price sorting, and a reset option to the Products page. Customers can now search for a product, filter the products by type, sort them by price, and reset the filters. We have more than 100 products in the catalogue, and I wanted to make it easier for customers to find what they are looking for without having to go through all the products.
>
> 2. Chat Shopping Experience - I improved the chat experience by making the customer and assistant messages visually different, adding automatic scrolling, starter prompts, and a loading state while the assistant is responding. I wanted to make the chat easier to use, especially for someone using it for the first time, and give customers a better idea of what they can ask the assistant.
>
> 3. Product Search Relevance - I improved the product search so that the assistant prioritizes products that are more relevant to what the customer is asking for. I also added support for price limits, such as under $50, so the assistant only returns products that meet the customer's price requirement. I wanted the assistant to better understand what the customer is actually looking for and avoid showing products that do not meet their requirements.
>
> 4. Ambiguous Product Requests - I added handling for ambiguous product requests so that when a customer asks about a product that could refer to multiple products, the assistant asks the customer to clarify instead of automatically choosing one. I wanted to reduce the chance of the assistant giving the customer the wrong price or inventory information and make sure the customer gets information about the product they actually mean.
>
> Do not change the implementation of Problem 9. This is only for the required usability documentation. After creating the file, confirm that it exists and that the content matches what I provided.

The requested usability documentation was added to `output/usability.md` with the wording and structure provided.

## Problem 10 — Overall Site Design and Usability

### Prompt

> Let's do Problem 10. I want to improve the overall style and usability of the Campus Customs site. Before making changes, first look at the current frontend, existing design, and actual product catalogue/database. Use the university merchandise sites I shared as references without copying either site's design. Keep the Campus Customs Yale-inspired navy, cream, gold, editorial serif, clean sans-serif, product imagery, whitespace, branding, and AI assistant. Make Home feel like a real merchandise storefront with real catalogue-based Shop the Collection categories and a real featured product section. Improve Products presentation while keeping Problem 9 search/filter/sort/reset. Improve product-detail hierarchy while keeping database inventory and product information. Improve navigation simply, preserve all Problems 5-9 AI shopping functionality, keep the site responsive, and do not invent products, prices, categories, inventory, or images. Do not change the database or authentication unless necessary and do not start Problem 11. Run `npm run build`, check the backend, test Home, Products, detail, login/logout, chat, Problem 9 controls, and existing agent flows, update `AI_prompts.md`, and create `output/design.md` in a simple first-person numbered style.

The Home page now has catalogue-backed collection cards and a Yale Favorites section. Product and detail pages have stronger merchandising hierarchy and subtle interactions, while the existing search, filters, sorting, chat, authentication, inventory, and product routes were preserved. `output/design.md` documents the design choices.

### Follow-up Prompt — Problem 10 Visual Design Pass

> I looked at the actual website after the Problem 10 changes, and I think the site is still a bit too plain and generic visually. I want to do another visual pass without changing the functionality we already built. Please improve the Home hero with a real local product image, make the real Hoodies, Crewnecks, and T-Shirts sections more editorial, vary the Yale Favorites merchandising layout, improve contrast and visual rhythm, strengthen Products and Product Detail hierarchy, and improve the visual presentation of the AI shopping assistant. Preserve all Problems 3-9 functionality, use only actual catalogue products and images, do not change the database or product data, run `npm run build`, check the existing pages and controls, update `AI_prompts.md`, and update `output/design.md` only if the design decisions materially changed. Do not start Problem 11.

The visual pass now uses a real catalogue image in the Home hero, varied editorial category and featured-product layouts, stronger product/detail hierarchy, and a more integrated chat presentation. Existing functionality and data sources were preserved.

### Follow-up Prompt — Strengthen Homepage Composition

> I know those elements are already there. My issue is not that anything is missing, it is that the site still feels too plain when I actually look at it. Please critically look at the current homepage as a designer and make meaningful visual changes focused on composition, scale, spacing, typography, image treatment, section transitions, and visual hierarchy. Use the existing product images, create more visual storytelling, vary the layouts instead of another grid, and make the hero feel stronger. Keep the navy, cream, and gold palette, avoid excessive animation, shadows, gradients, and decoration, preserve Problems 3-9 functionality, do not change product data, and run the build and checks afterward.

The homepage now uses a split navy-and-image hero, a larger editorial introduction, staggered category features, and an asymmetric favorites composition. Product images and hierarchy are more prominent while existing functionality remains unchanged.

### Follow-up Prompt — Refine Homepage Navigation and Merchandising Layout

> I think we should make a few changes to the homepage now. Change the header so the Campus Customs name/logo is centered and more prominent, with Home, Products, and About Us on the left and account options on the right. Make the three Shop the Collection product images bigger and reduce empty space around them. Put the three Yale Favorites products horizontally next to each other at the same size instead of having one larger product. Keep the current colors and style, use the existing product images, and keep all existing functionality working.

The header now has a centered, more prominent brand with primary navigation on the left and account navigation on the right. Collection imagery is larger, and Yale Favorites now uses three equal horizontal product columns.

### Follow-up Prompt — Light Product Image Treatment

> I want to change how the product images are displayed across the site. Remove the gray/beige rectangular image boxes and use the same light cream background as the page so the product looks like it is sitting directly on the page. Let the product fill most of the image area, keep the name and price underneath with space between the image and text, and use the same treatment on the homepage product sections, Products page, product-detail page, and chat product cards. Do not change the actual product images or product data.

The product image areas now use the page cream background without visible rectangular boxes, with more prominent product imagery and preserved spacing for names and prices across the site.

### Follow-up Prompt — Remove Product Image Backgrounds

> The black backgrounds are still visible on some product images. Please process the product images so the background around the clothing is transparent while keeping the clothing, edges, and logos unchanged. Display the transparent images on the cream background across the homepage, Products page, product-detail page, and chat product cards. Do not change the actual product data.

Created transparent sibling PNG assets for the 102 catalogue images using edge-connected background removal, preserved the original JPEGs, and updated the backend to serve the transparent assets when available.

### Follow-up Prompt — Fix Affected Transparent Assets

> The Basic Hoodie Big Yale is getting cropped, so please fix that image and check the other product images for the same issue. Leave images that already look good unchanged. The Benjamin Franklin 1/4 Zip still has a white background, so remove it to match the cream background.

Added transparent padding to the Basic Hoodie Big Yale so the complete garment remains visible, and regenerated only the Benjamin Franklin 1/4 Zip transparent asset to remove its remaining white background. Other processed assets were left unchanged.

### Follow-up Prompt — Correct the Basic Hoodie Cutout

> The attached screenshot shows the Basic Hoodie Big Yale cutout has a serious error: the background-removal process removed part of the dark garment and left white artifacts near the lower right. Please compare it with the original, regenerate only the affected asset with a more conservative mask, preserve the full clothing shape and Yale logo, and keep the other good product images unchanged.

The Basic Hoodie Big Yale transparent asset was regenerated with a conservative edge-connected black-background mask. The garment and logo are preserved, the full product has transparent breathing room, and no other processed assets were changed.

## Problem 11 — Application Checks

### Prompt

> I finished the three Problem 11 tests and have the screenshots ready. Please create `output/app_check.html` with three clearly separated sections for the inventory and price check, dynamic search-result cards, and the Problem 9 usability feature. Include the provided screenshots from `output/app_check_images/`, explain each result briefly, match the Campus Customs visual style, update `AI_prompts.md`, do not change site functionality or the database, run the build, and verify the HTML and image paths.

The Problem 11 application-check report was created with the three supplied screenshots and relative image links. It documents the $68.00 price and 60 units in stock for the Basic Hoodie Big Yale, dynamic hoodie search cards, and the “hoodie” filter showing 26 of 102 products. The frontend build passed.
