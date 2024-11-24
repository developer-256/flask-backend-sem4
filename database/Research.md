## Thinking on the modules for database

1. # user module

   - id
   - fname, lname
   - username (unique)
   - email (unique)
   - password
   - bio
   - created and updated at
   - one to many with question
   - one to many with answers

2. # questions module

   - id
   - title
   - content
   - created and updated time
   - one to many with user
   - one to many with answers
   - many to many with question tags

   * make queries get questions newest, unanswered, oldest
   * make queries from question id to get answers in (no. of up or down votes, recent, oldest)

3. # answer module

   - id
   - content
   - upvotes (no time for tables)
   - downvotes (no time for tables)
   - one to many with questions
   - one to many with user

4. # Question tag

   - id
   - unique name
   - many to many with questions
