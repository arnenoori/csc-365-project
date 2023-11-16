# Group Project: V4 - Add additional complexity and handle concurrency

Version 4 of the group project has three separate requirements to it:

## Address all peer review feedback
You must address all peer review feedback or state why you think the peer review feedback was not relevant. Document the changes you made to address peer review feedback (or cases where you purposefully decided not to address feedback) in a file called peer_review_response.md

### Peer Feedback:

#### Code Reviews:

❌ Return statement outside try block
This may be personal preference (in fact maybe this is an incorrect suggestion) but I find it more readable when the main return statement for a function is in the try block with the rest of the code instead of after the except DBAPIError. Like when you do something like return {"user_id": user_id} I like to see that return statement happen right after all the logic that you used to get that user id. It makes more sense to me because if you receive an exception in your code you will never get to a return statement after the exception handler anyway so why would you feel the need to put it outside the try block.

✅ create_user - Code for creating user
Your code for creating a new user does not first check if the given email is already used for an existing user in the database. If you are using email as a username for each user you probably don't want different people creating user accounts under the same email. I get that each user will user their unique id to identify themselves but having duplicate emails in the users table could potentially mess with password authentication or bleed into other areas of your code.

✅ get_user - Directly returning query result ans (also applies to other functions in code)
This may be another personal preference thing but I'm not sure it's a good idea to directly return whatever CursorResult you get from your SQL query. I know that the query will never return more than one row because you are using the id and the columns you want are specified in the query as well. However, I feel like it is still important to be explicit about what exactly you are returning instead of just returning everything from the query. It is easy enough (with this small function) to see what is returned by looking at the query, but If your code logic in this function or the query itself were more complex (or gets changed) it would be a different story. You even have a comment right above return ans presumably to remind you exactly what is getting returned. At that point you might as well just explicitly write out what you want to return.

✅ update_user - Checking for duplicate emails
For the same reason as listed above it may be a good idea to check if the new email provided is already in use. If you were to only check this upon account creation and then allow people to use whatever email they want later it would defeat the purpose.

✅ Using transaction as tag for router
This is definitely a preference thing but you use @router.get("/", tags=["transaction"]) and similar for your transactions endpoints. Firstly I don't think you actually need the tags=["transaction"] every time like that but that is totally fine and not what I am worried about. What it noticed is that the tag transaction doesn't match the endpoint path /transactions. I just think it's nice when everything matches up. Right now in the docs for example, you see the tag transaction but then all the endpoint paths are using transactions plural.

✅ get_transaction- Why use .all()[0]?
I'm curious why you used .all()[0] I feel think there are other functions that only return 1 row by default. Like .first() for example

✅ get_transaction - What happens when requesting a transaction that doesn't exist
I noticed that you raise an HTTP exception in get_user when a user is not found. Right now get_transaction doesn't do that if a transaction is not found. In fact, it gives an internal server error when the transaction doesn't exist so you may want to do some more error checking.

✅ get_transaction- What happens when a certain user requests a transaction that isn't theirs (applies to purchases as well)
You don't do any checks on wether the transaction_id they are requesting information for actually belongs to the given user_id. Any user can access any and all transactions which is a big breach of user privacy. What if Alice doesn't want people knowing she shops at Trader Joe's?

✅ update_transaction - Any user can change any transaction (applies to purchases as well)
Same as above, you probably don't want just any user changing all of Alice's transactions. You may also want to consider versioning instead of updating the rows so that you can have a history of what the transaction was before.

✅ delete_transaction - Any user can delete any and all transactions (applies to purchases as well)
Same as above, you probably want to make sure that only the owner of the transaction can delete it. Additionally, especially when it comes to deleting information, you may want to require more authentication than just the user_id.

✅ get_purchases Desired behavior for non-existent purchase
If a purchase with the given transaction id does not exist you return an empty list. Is this the desired result? Should you print a message detailing that the given transaction does not (yet) have any purchases associated with it?

✅ All Purchases endpoints should validate if transactions or purchases belong to the given user
In addition to making sure that a given transaction belongs to the given user, it is probably important to make sure that users are only accessing purchases that are connected to a transaction that they own.

✅ get_purchase Requesting a purchase that doesn't exist
Aside from the fact that user_id and transaction_id aren't used and could literally be anything in this function. If a user inputs a purchase_id that does not exist it gives an internal server error.



✅ create_user: lacks a check for existing emails
The current way of creating a new user is missing a check for seeing whether the given email is already being used for a user, potentially leading to duplicate entries. To address this, I'd suggest having a check for a get_user_by_email function before going ahead with the insertion, ensuring that values are stored/returned the way they're supposed to.

✅ get_transactions: data privacy issue
The methods for getting transactions don't safeguard data privacy/security, since any user can retrieve another user's transaction data with no problem. I would consider implementing a check to see if the user)id passed in is actually the user's id so that they can only view their data (least privilege).

❌ All methods (queries): separate query text
For all SQL queries, I would consider separating query text from inside the sqlalchemy.text() to promote readability. I would consider creating variable values to store the text then using those variable values inside the queries.

❌ get_transactions: no check to see if transaction exists in DB
I would raise an exception in the case that ans returns empty (there is no transactions for a user). Right now there is no handling for that case.

✅ create_transactions: in-depth exception handling
With so many variables at play with the queries, it would make sense to handle exceptions individually. For example, merchant, description, and user_id all come in from user input and are thus vulnerable to user error. It would make sense to handle each error case and throw an exception for each.

✅ get_transaction(s) refactoring into one method
It may make sense to merge get_transaction and get_transactions into one instead of using 2 different endpoints. The 2 can be merged into one get_transactions with an optional transaction_id parameter that would output a specific transaction if provided for the given user. If not, it would output all transactions for a given user. This could benefit readability and simplify things.

✅ get_transactions: implement pagination
You could implement pagination when displaying the transactions for a user so that in the case that there are a large number of transactions to display, it would still be readable for the user. This could be implemented in a similar way to our potions project.

update_transaction: implement idempotency
In case of network failure, you want to make sure you don't have any duplicate processes updating values in tables. To prevent this, you can record an id value during each call and only execute the call if this id value hasn't been seen before.

✅ get_purchases: data accessibility issue
I would ensure that only users with the given user id can retrieve/modify their respective purchases. In this context, I don't think it makes sense for users to be able to access other user data.

delete_user: who should have authority?
I think there should be a restriction placed on who should be able to delete users. Right now, any regular user can delete any other user they want, which likely shouldn't be the case.

✅ Purchases: user_id has no use
Despite being taken in as a parameter, none of the methods actually use the user_id value in any of the queries. I would likely utilize user_id as another aspect of the queries to ensure users are retrieving/manipulating their own purchase values.

❌ Purchases: price data type
I would change the way price is currently stored to only handle dollar and cents decimal placing. Right now, you're able to set a price value to 2.89999 for example.

✅ Purchases: date types
For the date values (warranty_date, return_date), there should be an additional constraint to ensure that you can't enter in a random string as a value. This is something I ran into while testing.



Implement the endpoints from the ExampleFlows.md file: dashboard, recommendations, export, authenticate, goal

✅ Transactions.py: get_transaction takes in a user_id, but does not use it in the query. If it is not necessary, I would remove that parameter. Otherwise, it would be a good thing to implement into the query as you want to make sure it is specific to a certain user.

✅ Transactions.py: get_transaction and get_transactions seem to do the same thing. I would try to make a transaction_id an optional parameter if the user wants a specific transaction, otherwise return all.

✅ Transactions.py: update_transaction takes in a user_id but does not use it in the query. Try to implement it to ensure the transaction given is specific to the user.

✅ Transactions.py: delete_transaction takes in a user_id but does not use it in the query. Try to implement it to ensure the transaction given is specific to the user.

✅ Transactions.py: update_transaction returns the merchant and description even when the user or transaction ids do not exist. I think it would be better for a message to indicate whether the ids exist and if the task was possible.

✅ Transactions.py: It might be a good idea here to check if a user exists for the case of getting transactions. It does return an empty array with an user_id that doesn’t exist, but it kind of indicates that the user does exist when it returns something expected. Maybe here you can return an error message that indicates the user does not exist.

❌ Users.py: Including a password field would be beneficial. Especially with the auth/signin endpoint from the example flows, if implemented.

✅ Users.py: get_user has an issue with handling a user that does not exist. Instead of the exception error being raised, a 500 error is seen in the render docs. Make sure the correct error is being raised (404 status code in the get_user endpoint)

✅ Users.py: update_user returns something unexpected when an update should fail due to the user corresponding with a certain user_id not there. It should return a message like: user_id not found, or something like this instead of the name and email to be changed when a user doesn’t exist.

✅ Users.py: many of the endpoints should check if a user exists or not. When testing with user_id that does not exist, the behavior of the endpoints makes it seem like the actions are valid. I think it would be good to have a message indicating the user doesn’t exist

✅ Purchases.py: all endpoints take in a user_id, but do not use in the query. The only place I see it being used is for a print statement. I think it would be beneficial to take in the user_id and use it just to ensure that the correct information is returned specific to a user.

✅ Purchases.py: the get endpoints have the same functionality, so I think it would be nice to compress the two. Maybe have the transaction_id as an optional field, like the get endpoints in transactions.py.

✅ Purchases.py: for the price input, I see that it is a float. It could be a good option for the endpoint to handle cases where a user just puts the dollar amount like 500 instead of 500.00. Probably unnecessary, but could be a nice thing to have with users being lazy.

#### Repeated Code Review Feedback:

Checking for Duplicate Emails in User Creation and Update:

✅ Both in the creation (create_user) and updating (update_user) of user accounts, there's a repeated suggestion to check if the email provided is already in use. This is to prevent multiple accounts with the same email, which could lead to issues with authentication and account management.

Data Privacy and Access Control:

✅ Several functions (get_transaction, update_transaction, delete_transaction, get_purchases, and all purchases endpoints) lack proper checks to ensure that the requesting user is entitled to access or modify the specified data. This is a significant issue as it allows any user to access or alter another user's transaction and purchase data, which is a breach of privacy and security.

Directly Returning Query Results:

❌ In functions like get_user, there's a concern about directly returning the query results (CursorResult) without explicitly defining what is being returned. This could become problematic, especially if the query or function logic becomes more complex, leading to potential confusion or errors in data handling.

Non-existent Transaction/Purchase Handling:

✅ For get_transaction and get_purchases, there's repeated advice about handling cases where a transaction or purchase does not exist. Currently, these functions may return an error or an empty list, which might not be the most informative or user-friendly response.

Utilization of User IDs in Queries:

✅ In several places (transactions.py and purchases.py), it's noted that while user_id is accepted as a parameter, it is not always used in the actual query. This is a repeated observation that indicates a lack of consistency and potential security oversight in the code.

Merging Similar Functions:

✅ Suggestions are made to merge similar functions like get_transaction and get_transactions, where the former could be a specific case of the latter with an optional transaction ID parameter. This would enhance code efficiency and readability.
Error Handling and Exception Management:

✅ There are multiple instances where more robust error handling and exception management are recommended, especially in scenarios where the data may not exist or the user input could lead to errors.

#### Schema Design Comments:

❌ Most endpoints share a path with another operation
I am not 100% sure if this is a problem but almost all of your endpoints share a path with another one (i.e. you use /user/{user_id} for all of: making, changing, and deleting a user). This is fine if you are calling the site from the docs and maybe an application program but I am just imagining what would happen if you were to put these paths directly into the browser. For example, neither getting or deleting a user require a json input, so if I just put /user/{user_id} into my browser is it going to create a user or delete one? I would suggest changing your paths to make them all unique in some way.

❌ Consider making email part of primary key or ✅ at least constraining it to be unique
If you go on to use email and password in any form of authentication you will probably want email to be unique such that when you are validating passwords you don't end up checking against another user's password.

❌ Users can change their email?
I understand why you made it possible for users to change their name but if email is used as a way to uniquely identify the user as their username (as suggested above) you might not want them changing their email all the time. I would suggest adding an unchangeable username attribute for users if you want users to be able to change their email. That way you can have people put in a username and password instead of an email when authenticating.

User password?
Your table schema has no place for passwords or anything related to them. Your README suggests that the service will have logins and a dashboard for users but your schema and account creation endpoint don't seem to account for passwords

✅ /user/{user_id}/transactions/ Also output transaction_id
I am imagining this endpoint would be used by users to see all the transaction they have in the system if they have forgotten them. It could be very useful but what if they want to edit or remove a transaction that they see on the list? Unless they happen to have their own personal list of transactions with their associated transaction_ids, they will have no way of knowing what the transaction_ids for all those transactions are and would have no way of changing them. You should list the transaction_id along with the merchant, description, and created_at.

✅ /user/{user_id}/purchases/ Also output purchase_id
For a similar reason as above, you probably want to be returning the information necessary to actually work with those purchases that someone asks for. You should list the purchase_id alongside the other details of the purchase.

✅ /user/{user_id}/transactions/ Probably don't need created_at to be listed
I am assuming that in many use cases for this service, the created_at field of the transactions is not going to match the actual time the transaction occurred in real life so the created_at field may be unnecessary when listing a user's transactions.

❌ Purchases have warranty and return dates, but not a purchase date?
I might suggest adding a purchase date to either the transactions or purchases table so that users have a way to track their purchases over time.

How are Receipts used by a user
I see that you have a table for receipts which you stated would be text which was converted from images of a receipt. There is no way however for a user to view or change the content of the receipt. Are you going to convert the receipt into a transaction and purchases automatically and then make those things available for the user to edit as needed?

Financial Goals
Your README and ER diagram mentions financial goals and planning. You don't have any tables related to financial goals listed in your schema and there are no endpoints to create, view, or alter a financial goal.

How are you tracking and evaluating budgets
If you only have information about the purchases the user is making, how are you going to do any budget tracking or suggestions? I would suggest maybe having a user input their monthly income and using the purchase dates or purchases to see if they are on track with their budget or something like that. Or if you prefer you could use the financial goals mentioned above somehow to track or suggest budget information as well.

ER diagram mismatch
Your ER diagram does not accurately depict the entities you have within your application. Purchases should probably be connected to a transaction entity which connects to users in order to accurately depict the way your tables are connected to each other.


❌ The purchase endpoint has fields to reflect warranty and return date. Sometimes these fields don’t apply to all purchases like food items. I see they are optional, but might be a nice touch to differentiate the categories.

Example flows/API Specs out of date: reflect flows from V2 into ExampleFlows.md as they are not listed.

Example flows/API Specs out of date: API specs should include the endpoints mentioned in the ExampleFlows.md (dashboard, recommendations, export, authenticate, goal)

Receipts Table: Either implement or remove as it is not being used at this state

Receipts Table: has a field for an image, but the value is text. Update to the right data type if an image is possible, otherwise provide an alternative solution.

Receipts Table: both fields (transaction_id and image) should be required fields, if implemented.

❌ Purchases Table: Category attribute seems like something that should be a required field. It can be beneficial for the example flows listed in ExampleFlows.md (Financial advice, recommendations)

❌ Purchases Table: Price could have an option of being an int and the endpoint handles the case of adding the decimal places. People could be lazy and not enter the .00 part, but this isn’t super necessary.

✅ Transactions Table: Merchant seems like it should be a required attribute. Description can be required, but maybe depends on whether that information will be used in another endpoint like recommendations (if implemented)

✅ I think it would be beneficial to have restrictions on the categories that a user can enter for future additions to the project (recommendations, etc). It can help strictly categorize and force the user to choose a certain category for their purchase. The transaction description however can remain up to the user.

A filter option could be a good addition for getting the purchases. Like if a user wants purchases that reflect produce, they can just get those purchases rather than all.

✅ The email should probably constrain the end like @gmail, @yahoo, etc. That way only valid emails are used.

A required password field would be good in the case of a login being implemented.

❌ The path for many of the endpoints is the same, but they do different things. For example: user/{user_id} is the same path for get, update and delete user. I would have a way to indicate which endpoint is which like user/get/{user_id} or something.

Implementing the flows mentioned would be a great idea especially if the application is meant for helping users track their budget and receive suggestions! It would be a great addition to actually process the purchases and provide some sort of feedback rather than just serving as a storage for purchases/transactions.


It would make sense to have a 'password' field tracked in your users table to authenticate users into the system properly. RIght now, it doesn't seem like the login logic has been implemented.

From what I see, there is no handling of financial goals in the tables, something that was mentioned in the README. It would make sense to have a 'goal' field tracked for users and their transactions.

I did some research and found that it's recommended to store images as binary data in the database (bytea type). Images are currently stored as text types in the receipts table.

You likely need an additional table to store ChatGPT messages and interactions to then parse through when implementing functionality.

✅ Date values: I think tracking would benefit if a date value was added to the purchase and receipt tables for when each occurred.

❌ A lot of the endpoint paths are the same for transactions, purchases, and user despite accomplishing different tasks. I would try to work into the endpoint path an indication of what distinct function it serves for those that overlap.

I think there should be an endpoint to view/update data from scanned receipts in the receipt table. Right now, there is no available access to that information.

In the receipts table, transaction_id and image should be required values, since entries are based on scanned receipts and are linked to transactions per the README.

❌ In the purchases table, category should be a required value since you want to do analysis with this attribute moving forward.

✅ The email field in the users table should have an additional restriction to end with an email signature (@...) so that random text values aren't accepted as emails.

❌ Missing table for storing summary/graphical data (Dashboard) for users and respective endpoints. I would add this table and respective foreign key links to the other tables.

✅ While testing, I noted that the "get transactions" endpoint returned data that wasn't entirely relevant to the user. Instead of returning the date in which the table entry was created, a value reflecting the date in which the transaction actually occurred should be returned.

#### Repeated Feedback:

❌ Uniqueness of Endpoint Paths: Multiple comments highlight the issue of different operations (like create, update, delete) sharing the same endpoint path, which could lead to confusion or unintended actions.

✅ Email Address Concerns: There are several mentions of the need to handle email addresses more effectively. This includes making email part of the primary key or enforcing it as unique, and considerations about whether users should be able to change their email.

Lack of Password Field in User Schema: The absence of a password field or related security features in the user table is noted multiple times, emphasizing the importance of this for user authentication and security.

✅ Need for Explicit Transaction and Purchase IDs in Outputs: The feedback repeatedly suggests that endpoints for transactions and purchases should explicitly output their respective IDs (transaction_id and purchase_id) to enable users to interact more effectively with this data.

Receipts Table Utility and Implementation: Several comments question the implementation and practical use of the receipts table, including how users interact with it and the data types used.

Implementation of Specified Flows and Functionalities: There are multiple mentions of the need to implement the functionalities outlined in ExampleFlows.md or the README, like dashboard, recommendations, export, authenticate, and goal, to enhance the application's utility.

❌ Handling of Optional Fields in Purchases: The approach to managing optional fields in purchases, particularly for items where certain details like warranty or return dates may not apply, is brought up more than once.

#### Product Ideas:

✅ Search/Sorting endpoint
You could create a more versatile way for a user to look through their purchases with a searching endpoint similar to the one from the potion shops. Users could search for purchases that fall under a transaction from a particular merchant or search for purchases of a particular item or both.

✅ If there are multiple transactions from the same merchant this would let users see what and how much they buy from certain stores. If you also add a way for people to sort based on different attributes like the purchase date, item name, price, etc. It could help users further evaluate their own spending habits.

✅ Searching for particular items purchased could let users evaluate how often they buy a particular item for example.

✅ If a user really wanted to narrow things down they could search for a particular item purchased from a particular merchant and sort it based on purchase date, that way they could see if that merchant has increased the price for that item over time and maybe choose a different merchant based on this info.

Financial Goal endpoint
I wasn't totally sure how you had planned to implement financial goals and budget planning into your application but I thought it might be a good idea to just use a single endpoint. With this endpoint a user could input various information about themselves and what they want and the endpoint would use the information in the database about that user to give them a goal.

Something like a user inputting how much money they make in a month and the endpoint could tell them how much money they could spend per day for the rest of the month based on how much money they have already spent that month.

Or maybe the endpoint could take in just how much money the person currently has left and return how much they could spend per day for the rest of the month and If they have spent more per day on average per day in the last month than the suggested amount it could suggest some of the most expensive purchases to avoid in the coming days.

Or something else, I think there are many ways to leverage information about someones purchases and simple information that someone inputs in order to make financial/budgeting goals.


I think it would be cool to have an endpoint that looks through the history of purchases and provides suggestions for the stores they should continue purchasing a certain item from. Like if one store has a better deal on an item, it should suggest to the user to continue buying the item from that store. For example, the endpoint can find all purchases of bananas from different stores, and return the store with the best price. It can look at frequent purchases of certain items, and provide the best place to purchase said item.

An option for the user to create a shopping list would be a nice addition. This can be joined with the previous suggestion in which the program can suggest the best place to purchase the items to save money. For example, the user can input a grocery list, and the endpoint can return the best store to find all these items at the best price. Could be a cool addition, but the issues I see is if a certain item has never been in the database before, and the fact that prices can change in stores.


One suggestion for an endpoint would be one that would enable users to generate detailed financial reports for a specific time period. Users can specify the start and end dates to retrieve reports on expenses and savings. This feature would promote better financial planning and analysis. Right now, we are only able to retrieve transaction/purchase data for a specific id.

Another suggestion for an endpoint would be one that compares the user's spending habits with aggregated data from other users, under anonymity, of course. This feature would provide context on how the user's expenses align with broader trends to give them an idea on how their habits stand amongst consensus. This could give insight towards changing habits for the better.


## Build two complex endpoints
Create two complex endpoints. Complex meaning it does significantly more than just a straightforward create/update/delete/read from the database. If you believe you already have two endpoints that meet my definition of complex then you don't need to create additional endpoints. Document these endpoints in your existing API Spec and put a comment on your group's submission calling out what your two complex endpoints are.

## Write up concurrency control mechanisms used in your service
Write up three cases where your service would encounter phenomenon if it had no concurrency control protection in place. See https://observablehq.com/@calpoly-pierce/isolation-levels for a list of the type of phenomenon you should be referencing. Make a sequence diagram for each case. What will you do to ensure isolation of your transactions and why is that the appropriate case. If you believe your transactions don't have any such cases, your transactions either aren't complex enough and you need to build something more interesting or you aren't understanding what issues are occurring. Note, this can be both how a particular transaction definition interacts with other transaction definitions, but also how a transaction definition interacts with other concurrent instances of itself. Please document all of this in a markdown file named: concurrency.md checked into your group's github.
