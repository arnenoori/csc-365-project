# Peer Review Feedback
## Code Reviews:
### Ash Mitchell
1. Return statement outside try block 
This may be personal preference (in fact maybe this is an incorrect suggestion) but I find it more readable when the main return statement for a function is in the try block with the rest of the code instead of after the except DBAPIError. Like when you do something like `return {"user_id": user_id}` I like to see that return statement happen right after all the logic that you used to get that user id. It makes more sense to me because if you receive an exception in your code you will never get to a return statement after the exception handler anyway so why would you feel the need to put it outside the try block.
- ❌ We simply prefer to leave the return statement at the end as a stylistic choice.
  
2. `create_user` - Code for creating user
Your code for creating a new user does not first check if the given email is already used for an existing user in the database. If you are using email as a username for each user you probably don't want different people creating user accounts under the same email. I get that each user will user their unique id to identify themselves but having duplicate emails in the users table could potentially mess with password authentication or bleed into other areas of your code.
- ✅ added checks for unique email when creating user or updating email
  
3. `get_user` - Directly returning query result `ans` (also applies to other functions in code)
This may be another personal preference thing but I'm not sure it's a good idea to directly return whatever CursorResult you get from your SQL query. I know that the query will never return more than one row because you are using the id and the columns you want are specified in the query as well. However, I feel like it is still important to be explicit about what exactly you are returning instead of just returning everything from the query. It is easy enough (with this small function) to see what is returned by looking at the query, but If your code logic in this function or the query itself were more complex (or gets changed) it would be a different story. You even have a comment right above `return ans` presumably to remind you exactly what is getting returned. At that point you might as well just explicitly write out what you want to return.
- ❌ another stylistic choice

4. `update_user` - Checking for duplicate emails
For the same reason as listed above it may be a good idea to check if the new email provided is already in use. If you were to only check this upon account creation and then allow people to use whatever email they want later it would defeat the purpose.
- ✅ added checks for unique email when creating user or updating email

5. Using `transaction` as tag for router
This is definitely a preference thing but you use `@router.get("/", tags=["transaction"])` and similar for your transactions endpoints. Firstly I don't think you actually need the `tags=["transaction"]` every time like that but that is totally fine and not what I am worried about. What it noticed is that the tag `transaction` doesn't match the endpoint path `/transactions`. I just think it's nice when everything matches up. Right now in the docs for example, you see the tag transaction but then all the endpoint paths are using transactions plural. 
- ✅ updated transaction tag
  
6. `get_transaction`-  Why use `.all()[0]`?
I'm curious why you used `.all()[0]` I feel think there are other functions that only return 1 row by default. Like `.first()` for example
- ✅ updated functions used

8. `get_transaction` - What happens when requesting a transaction that doesn't exist
I noticed that you raise an HTTP exception in `get_user` when a user is not found. Right now `get_transaction` doesn't do that if a transaction is not found. In fact, it gives an **internal server error** when the transaction doesn't exist so you may want to do some more error checking.
- ✅ added propper error handling

10. `get_transaction`-  What happens when a certain user requests a transaction that isn't theirs (applies to purchases as well)
You don't do any checks on wether the transaction_id they are requesting information for actually belongs to the given user_id. Any user can access any and all transactions which is a big breach of user privacy. What if Alice doesn't want people knowing she shops at Trader Joe's?
- ✅ added checks to all functions ensuring transactions belong to the user

12. `update_transaction` - Any user can change any transaction (applies to purchases as well)
Same as above, you probably don't want just any user changing all of Alice's transactions. You may also want to consider versioning instead of updating the rows so that you can have a history of what the transaction was before.
- ✅ added checks to all functions ensuring transactions belong to the user

14. `delete_transaction` - Any user can delete any and all transactions (applies to purchases as well)
Same as above, you probably want to make sure that only the owner of the transaction can delete it. Additionally, especially when it comes to deleting information, you may want to require more authentication than just the user_id.
- ✅ added checks to all functions ensuring transactions belong to the user

15.  `get_purchases` Desired behavior for non-existent purchase
If a purchase with the given transaction id does not exist you return an empty list. Is this the desired result? Should you print a message detailing that the given transaction does not (yet) have any purchases associated with it?
- ❌ is desired result

17. All Purchases endpoints should validate if transactions or purchases belong to the given user
In addition to making sure that a given transaction belongs to the given user,  it is probably important to make sure that users are only accessing purchases that are connected to a transaction that they own.
- ✅ added checks to all functions ensuring purchase belongs to transaction and that transaction belongs to user

19. `get_purchase` Requesting a purchase that doesn't exist
Aside from the fact that user_id and transaction_id aren't used and could literally be anything in this function. If a user inputs a purchase_id that does not exist it gives an **internal server error**.
- ✅ added propper error handling

### Yashwant Sathish Kumar
1. create_user: lacks a check for existing emails

The current way of creating a new user is missing a check for seeing whether the given email is already being used for a user, potentially leading to duplicate entries. To address this, I'd suggest having a check for a get_user_by_email function before going ahead with the insertion, ensuring that values are stored/returned the way they're supposed to.

- ✅ added checks for unique email when creating user or updating email

2. get_transactions: data privacy issue

The methods for getting transactions don't safeguard data privacy/security, since any user can retrieve another user's transaction data with no problem. I would consider implementing a check to see if the user)id passed in is actually the user's id so that they can only view their data (least privilege).

- ✅ added checks to all functions ensuring transactions belong to the user

3. All methods (queries): separate query text

For all SQL queries, I would consider separating query text from inside the sqlalchemy.text() to promote readability. I would consider creating variable values to store the text then using those variable values inside the queries.

- ❌ stylistic choice

4. get_transactions: no check to see if transaction exists in DB

I would raise an exception in the case that ans returns empty (there is no transactions for a user). Right now there is no handling for that case.

- ✅ added propper error handling and checks

5. create_transactions: in-depth exception handling

With so many variables at play with the queries, it would make sense to handle exceptions individually. For example, merchant, description, and user_id all come in from user input and are thus vulnerable to user error. It would make sense to handle each error case and throw an exception for each.

- ✅ added propper error handling and checks

6. get_transaction(s) refactoring into one method

It may make sense to merge get_transaction and get_transactions into one instead of using 2 different endpoints. The 2 can be merged into one get_transactions with an optional transaction_id parameter that would output a specific transaction if provided for the given user. If not, it would output all transactions for a given user. This could benefit readability and simplify things.

- ✅ refactored into one method get_transactions()

7. get_transactions: implement pagination

You could implement pagination when displaying the transactions for a user so that in the case that there are a large number of transactions to display, it would still be readable for the user. This could be implemented in a similar way to our potions project.

- ✅ implemented pagination

8. update_transaction: implement idempotency

In case of network failure, you want to make sure you don't have any duplicate processes updating values in tables. To prevent this, you can record an id value during each call and only execute the call if this id value hasn't been seen before.

9. get_purchases: data accessibility issue

I would ensure that only users with the given user id can retrieve/modify their respective purchases. In this context, I don't think it makes sense for users to be able to access other user data.
- ✅  addressed earlier

10. delete_user: who should have authority?

I think there should be a restriction placed on who should be able to delete users. Right now, any regular user can delete any other user they want, which likely shouldn't be the case. 
- ❌ likely would require something outside the scope of this project

11. Purchases: user_id has no use

Despite being taken in as a parameter, none of the methods actually use the user_id value in any of the queries. I would likely utilize user_id as another aspect of the queries to ensure users are retrieving/manipulating their own purchase values. 
- ✅  addressed earlier
  
12. Purchases: price data type

I would change the way price is currently stored to only handle dollar and cents decimal placing. Right now, you're able to set a price value to 2.89999 for example.
- ✅  chanegd price to cents stored as int

13. Purchases: date types

For the date values (warranty_date, return_date), there should be an additional constraint to ensure that you can't enter in a random string as a value. This is something I ran into while testing.
- ✅  added proper error handling and checks for inputs

  
### Felicia Patel
1. Implement the endpoints from the ExampleFlows.md file: dashboard, recommendations, export, authenticate, goal
- ❌ some of them have been scrapped but the ones meant to be kept have been implemented
  
2. Transactions.py: get_transaction takes in a user_id, but does not use it in the query. If it is not necessary, I would remove that parameter. Otherwise, it would be a good thing to implement into the query as you want to make sure it is specific to a certain user.
- ✅  addressed earlier

  
3. Transactions.py: get_transaction and get_transactions seem to do the same thing. I would try to make a transaction_id an optional parameter if the user wants a specific transaction, otherwise return all.
- ✅  addressed earlier

4. Transactions.py: update_transaction takes in a user_id but does not use it in the query. Try to implement it to ensure the transaction given is specific to the user.
- ✅  addressed earlier
5. Transactions.py: delete_transaction takes in a user_id but does not use it in the query. Try to implement it to ensure the transaction given is specific to the user.
- ✅  addressed earlier
6. Transactions.py: update_transaction returns the merchant and description even when the user or transaction ids do not exist. I think it would be better for a message to indicate whether the ids exist and if the task was possible.
- ✅  addressed earlier
7. Transactions.py: It might be a good idea here to check if a user exists for the case of getting transactions. It does return an empty array with an user_id that doesn’t exist, but it kind of indicates that the user does exist when it returns something expected. Maybe here you can return an error message that indicates the user does not exist.
- ✅  addressed earlier
8. Users.py: Including a password field would be beneficial. Especially with the auth/signin endpoint from the example flows, if implemented.
- ❌ proper password auth seems to be outside the scope of this project
9. Users.py: get_user has an issue with handling a user that does not exist. Instead of the exception error being raised, a 500 error is seen in the render docs. Make sure the correct error is being raised (404 status code in the get_user endpoint)
- ✅  addressed earlier
10. Users.py: update_user returns something unexpected when an update should fail due to the user corresponding with a certain user_id not there. It should return a message like: user_id not found, or something like this instead of the name and email to be changed when a user doesn’t exist.
- ✅  addressed earlier
11. Users.py: many of the endpoints should check if a user exists or not. When testing with user_id that does not exist, the behavior of the endpoints makes it seem like the actions are valid. I think it would be good to have a message indicating the user doesn’t exist
- ✅  addressed earlier
12. Purchases.py: all endpoints take in a user_id, but do not use in the query. The only place I see it being used is for a print statement. I think it would be beneficial to take in the user_id and use it just to ensure that the correct information is returned specific to a user.
- ✅  addressed earlier
13. Purchases.py: the get endpoints have the same functionality, so I think it would be nice to compress the two. Maybe have the transaction_id as an optional field, like the get endpoints in transactions.py.
- ✅ combined to create one bigger function
14. Purchases.py: for the price input, I see that it is a float. It could be a good option for the endpoint to handle cases where a user just puts the dollar amount like 500 instead of 500.00. Probably unnecessary, but could be a nice thing to have with users being lazy.
  - ✅  changed price to int of cents
 
### Nick Perlich
1) There should be more comments explaining logic inside functions. I ideally would like to read the function like a paragraph.
- ✅  added more comments
3) It would be nice to get a little blurb at the top of each file explaining what it represents or what the file’s main purpose is.
- ❌ I think the file's names are pretty self-explanatory, as they title what all the functions are related to.
4) Transaction and purchase are quite similar words. It would be nice to change the names of these files to make them more distinct.
- ❌ stylistic choice
5) There are comments describing what a function returns on some of the functions which are really nice. They would improve the readability of functions that do not have these comments a lot.
- ✅  added to all get_functions
6) It would be good if variable names better represented what they contain. Specifically, changing abbreviations to full words would be nice for readability.
  - ❌ stylistic choice
7) Add security measures in place to stop bad actors from randomly posting, deleting or updating information in the database.
- ✅  addressed earlier
8) Delete empty files to have a cleaner and more organized code base.
  - ✅  deleted empty files
9) Some lines of code are really long. It would be nice to shorten them by splitting up certain lines.
  - ❌ stylistic choice although did shorten certain longer lines
10) Add a linter to your codebase to help with picking up on issues.
  - ❌ prefer not to with this project
11) Add a code formatter to make sure there is a consistent style across all code written by contributors.
  - ❌ since there are only 4 of us, we a code formatter isn't absolutely required
12) Edit your project README file on GH, and add a "Contributing" section describing your coding standards, or pointing to the style guide(s) that should be followed by code contributors in your project. Also, provide instructions on how to set up IDE plugins if you have used them.
      - ❌ only us 4 are going to contribute to this project and we all already know how to contribute to it, so no need
13) Implement a cron so that when users hit your endpoints it is faster.
  - ❌ the SwaggerUI already exists which already simplifies the calling of endpoints
14) POST purchase function should be able to receive negative numbers or there should be some kind of error message explaining that only positive numbers should be put in the request.
- ✅  addressed earlier

## Schema/API Design

### Ash Mitchell

1. Most endpoints share a path with another operation
I am not 100% sure if this is a problem but almost all of your endpoints share a path with another one (i.e. you use `/user/{user_id}` for all of: making, changing, and deleting a user). This is fine if you are calling the site from the docs and maybe an application program but I am just imagining what would happen if you were to put these paths directly into the browser. For example, neither getting or deleting a user require a json input, so if I just put `/user/{user_id}` into my browser is it going to create a user or delete one? I would suggest changing your paths to make them all unique in some way.
- ❌ stylistic choice
2. Consider making email part of primary key or at least constraining it to be unique
If you go on to use email and password in any form of authentication you will probably want email to be unique such that when you are validating passwords you don't end up checking against another user's password.
- ✅  emails are now unique
3. Users can change their email?
I understand why you made it possible for users to change their name but if email is used as a way to uniquely identify the user as their username (as suggested above) you might not want them changing their email all the time. I would suggest adding an unchangeable username attribute for users if you want users to be able to change their email. That way you can have people put in a username and password instead of an email when authenticating.
- ❌ users should be able to change their email
4. User password?
Your table schema has no place for passwords or anything related to them. Your README suggests that the service will have logins and a dashboard for users but your schema and account creation endpoint don't seem to account for passwords
- ❌ addressed earlier
5. `/user/{user_id}/transactions/` Also output transaction_id
I am imagining this endpoint would be used by users to see all the transaction they have in the system if they have forgotten them. It could be very useful but what if they want to edit or remove a transaction that they see on the list? Unless they happen to have their own personal list of transactions with their associated transaction_ids, they will have no way of knowing what the transaction_ids for all those transactions are and would have no way of changing them. You should list the transaction_id along with the merchant, description, and created_at.
- ✅  added id to output
6. `/user/{user_id}/purchases/` Also output purchase_id
For a similar reason as above, you probably want to be returning the information necessary to actually work with those purchases that someone asks for. You should list the purchase_id alongside the other details of the purchase.
- ✅  added id to output
7. `/user/{user_id}/transactions/` Probably don't need created_at to be listed
I am assuming that in many use cases for this service, the created_at field of the transactions is not going to match the actual time the transaction occurred in real life so the created_at field may be unnecessary when listing a user's transactions.
- ✅  added date instead of created at to output
8. Purchases have warranty and return dates, but not a purchase date? 
I might suggest adding a purchase date to either the transactions or purchases table so that users have a way to track their purchases over time.
- ✅  added date instead of created at to output
9. How are Receipts used by a user
I see that you have a table for receipts which you stated would be text which was converted from images of a receipt. There is no way however for a user to view or change the content of the receipt. Are you going to convert the receipt into a transaction and purchases automatically and then make those things available for the user to edit as needed?
- ✅  implemented receipts
10. Financial Goals
Your README and ER diagram mentions financial goals and planning. You don't have any tables related to financial goals listed in your schema and there are no endpoints to create, view, or alter a financial goal.
- ❌ scrapped this idea
11. How are you tracking and evaluating budgets
If you only have information about the purchases the user is making, how are you going to do any budget tracking or suggestions? I would suggest maybe having a user input their monthly income and using the purchase dates or purchases to see if they are on track with their budget or something like that. Or if you prefer you could use the financial goals mentioned above somehow to track or suggest budget information as well.
- ✅  implemented budgets
12. ER diagram mismatch
Your ER diagram does not accurately depict the entities you have within your application. Purchases should probably be connected to a transaction entity which connects to users in order to accurately depict the way your tables are connected to each other.
- ❌ updated what we wanted to do with this project

### Felicia Patel

1. The purchase endpoint has fields to reflect warranty and return date. Sometimes these fields don’t apply to all purchases like food items. I see they are optional, but might be a nice touch to differentiate the categories.
- ❌ no need, warranty and return dates can be null if not applicable

3. Example flows/API Specs out of date: reflect flows from V2 into ExampleFlows.md as they are not listed.
- ✅  addressed earlier

4. Example flows/API Specs out of date: API specs should include the endpoints mentioned in the ExampleFlows.md (dashboard, recommendations, export, authenticate, goal)
- ✅  addressed earlier

5. Receipts Table: Either implement or remove as it is not being used at this state
- ✅  implemented receipts
6. Receipts Table: has a field for an image, but the value is text. Update to the right data type if an image is possible, otherwise provide an alternative solution.
- ✅  implemented receipts
7. Receipts Table: both fields (transaction_id and image) should be required fields, if implemented.
- ✅  implemented receipts
8. Purchases Table: Category attribute seems like something that should be a required field. It can be beneficial for the example flows listed in ExampleFlows.md (Financial advice, recommendations)
- ✅  made them required
9. Purchases Table: Price could have an option of being an int and the endpoint handles the case of adding the decimal places. People could be lazy and not enter the .00 part, but this isn’t super necessary.
- ✅ made prices ints of cents
10. Transactions Table: Merchant seems like it should be a required attribute. Description can be required, but maybe depends on whether that information will be used in another endpoint like recommendations (if implemented)
- ✅ merchant is required
11. I think it would be beneficial to have restrictions on the categories that a user can enter for future additions to the project (recommendations, etc). It can help strictly categorize and force the user to choose a certain category for their purchase. The transaction description however can remain up to the user.
- ✅ added restrictions
12. A filter option could be a good addition for getting the purchases. Like if a user wants purchases that reflect produce, they can just get those purchases rather than all.
- ✅ added filter
13. The email should probably constrain the end like @gmail, @yahoo, etc. That way only valid emails are used.
- ✅ added email format checking
14. A required password field would be good in the case of a login being implemented.
  - ❌ addressed earlier
15. The path for many of the endpoints is the same, but they do different things. For example: user/{user_id} is the same path for get, update and delete user. I would have a way to indicate which endpoint is which like user/get/{user_id} or something.
  - ❌ addressed earlier
16. Implementing the flows mentioned would be a great idea especially if the application is meant for helping users track their budget and receive suggestions! It would be a great addition to actually process the purchases and provide some sort of feedback rather than just serving as a storage for purchases/transactions.
- ✅ added new functionality

### Yashwant Sathish Kumar
1. It would make sense to have a 'password' field tracked in your users table to authenticate users into the system properly. RIght now, it doesn't seem like the login logic has been implemented. 
  - ❌ addressed earlier
2. From what I see, there is no handling of financial goals in the tables, something that was mentioned in the README. It would make sense to have a 'goal' field tracked for users and their transactions.  
- ✅  addressed earlier
3. I did some research and found that it's recommended to store images as binary data in the database (bytea type). Images are currently stored as text types in the receipts table. 
- ✅  addressed earlier
4. You likely need an additional table to store ChatGPT messages and interactions to then parse through when implementing functionality. 
  - ❌ removed this functionality
5. Date values: I think tracking would benefit if a date value was added to the purchase and receipt tables for when each occurred. 
- ✅  addressed earlier
6. A lot of the endpoint paths are the same for transactions, purchases, and user despite accomplishing different tasks. I would try to work into the endpoint path an indication of what distinct function it serves for those that overlap. 
- ✅  addressed earlier
7. I think there should be an endpoint to view/update data from scanned receipts in the receipt table. Right now, there is no available access to that information.
- ✅  data from reciepts is stored as purchases and transactions, so that is already possible
8. In the receipts table, transaction_id and image should be required values, since entries are based on scanned receipts and are linked to transactions per the README.
- ✅  addressed earlier
9. In the purchases table, category should be a required value since you want to do analysis with this attribute moving forward. 
- ✅  addressed earlier
10. The email field in the users table should have an additional restriction to end with an email signature (@...) so that random text values aren't accepted as emails.
- ✅  addressed earlier
11. Missing table for storing summary/graphical data (Dashboard) for users and respective endpoints. I would add this table and respective foreign key links to the other tables. 
- ✅  added budgets table
12. While testing, I noted that the "get transactions" endpoint returned data that wasn't entirely relevant to the user. Instead of returning the date in which the table entry was created, a value reflecting the date in which the transaction actually occurred should be returned.
  - ✅  addressed earlier

### Nick Perlich
1) You should let people set custom priorities for their goals.
  - ✅  addressed earlier
3) You should add a search functionality that lets users find purchases by merchant name for example.
  - ✅  addressed earlier
4) Giving financial advice can be very tricky in terms of legality. Be careful when you give those pieces of advice. Make sure to give some kind of explicit warning that you cannot be blamed for anything that goes wrong as a result of this advice. 
  - ❌ removed this functionality
5) Make sure that when you integrate ChatGPT, it should be explicitly clear to users that these recommendations are not coming from a human being.
  - ❌ removed this functionality
6) It could be nice if there was an option for the transaction description to be automatically generated.
  - ❌ not within scope of this project
7) I think there is too much trust in the user at this point with transactions and purchases. I think it might be better if you moved the merchant field to the Create Purchase endpoint and then in the backend a transaction was automatically generated.
  - ❌ addressed earlier by checking transaction belongs to user
8) You should add a password to Create User.
  - ❌ addressed earlier
9) It would be good to add some kind of check to make sure a user really wants to delete the thing they are deleting.
  - ❌ no need, as that would greatly overcomplicate the process of deletion
10) The same is true for confirming that a user wants to make a certain update.
  - ❌ no need, as that would greatly overcomplicate the process of updating
11) It would be nice if there was an endpoint similar to our potion shop’s audit that gives a summary of all your current spending statistics.
  - ✅  added
12) There should be some kind of protection for who can view transactions because bad actors might sell the spending data to send targeted advertisements that make it harder for people to succeed in achieving their goals.
  - ✅  addressed earlier
13) There should be some kind of fun reward system for making progress towards goals like maybe they get a cool emoji next to their username that represents various achievements.
  - ❌ no need, as that doesn't align with our goals for the project
