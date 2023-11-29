# Peer Review Feedback
## Code Reviews:
### Ash Mitchell:
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

