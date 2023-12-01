# Receipts Tracker+

**Contributors:** \
Connor O’Brien - cpobrian@calpoly.edu \
Bryan Nguyen - bnguy266@calpoly.edu \
Arne Noori - agnoori@calpoly.edu \
Sebastian Thau - sthau@calpoly.edu 

**Project Description:** \
Our project idea is to create a budget tracking app that assists users with tracking and managing their finances. Users can manually enter purchases as well as photos of receipts in order to store and track their purchases. These receipt images will be converted into text and stored in the database. Users will also be able to update financial goals and receive recommendations for managing their budget in the future.

**Database Diagram:**
![](Database Architecture Diagram.png)

User Authentication: Stores user credentials securely. Enables quick look-up for sign-in and sign-up processes.

Dashboard: Holds the summary and graphical data for each user's financial status. Enables quick retrieval for dashboard rendering.

Purchase: Keeps records of all purchases made by the user. Used for generating summaries, graphs, and budget recommendations.

Receipt: Stores images and OCR text of scanned receipts. Enables quick retrieval for editing and viewing.

Financial Goals: Holds the financial goals set by the user along with their progress. Used for tracking and notifications.

Budget Recommendations: Stores custom budget advice for each user based on their spending habits.


**Core Features**
1. User Authentication
* Sign Up: Users can register using an email and password.
* Sign In: Users can log in to access their personalized dashboard.
2. Dashboard
* Summary: Display a summary of the user's financial status, including total expenses, budget, and financial goals.
* Graphs: Show graphs for monthly spending, category-wise spending, etc.
3. Manual Entry of Purchases
* Form Fields: Users can manually enter details like item name, price, category, store name, and date.
4. Receipt Scanning
* Image Upload: Users can upload images of receipts or scan directly from within the app
* OCR (Optical Character Recognition): Extract text from the uploaded image using GPT Vision Model and Amazon S3 Bucket.
    * Data Parsing: Parse the extracted text to save the relevant details:
    * Store Name
    * Store's Address
    * List of Items
    * Prices for each Item
    * Subtotal, Tax, and Total
    * Date of Purchase

Export Data
**Roadmap**

Vector Databases
Semantic Search: Used for enabling natural language queries in the Chat GPT Integration feature. The Vector DB will hold the semantic embeddings of text for quick and accurate search results.

* Users can export their financial data in various formats like PDF, CSV, etc.
7. Search and Edit
* Semantic Search: Users can search their past purchases using natural language queries.
* Edit/Delete: Users can edit or delete entries, useful in cases like item returns.
8. Chat GPT Integration
* Query Handling: Users can ask the chatbot to find specific transactions, provide summaries, or offer budget advice.

* Bulk Import: Allow the import of multiple entries via a CSV file.

API integration to extract your data
Create an invoice
Split the bill with someone and share that
Twilio integration (after API integration)
