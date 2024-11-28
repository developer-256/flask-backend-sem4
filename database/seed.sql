USE Project
GO

-- Seed the USERS table
INSERT INTO USERS
    (FirstName, LastName, UserName, Email, UserPassword, Bio, SessionToken, createdAt, updatedAt)
VALUES
    ('John', 'Doe', 'john.doe', 'john.doe@example.com', 'password123', 'Software Developer', 'token123', GETDATE(), GETDATE()),
    ('Jane', 'Smith', 'jane.smith', 'jane.smith@example.com', 'password456', 'Product Manager', 'token456', GETDATE(), GETDATE()),
    ('Alice', 'Johnson', 'alice.johnson', 'alice.johnson@example.com', 'password789', 'UX Designer', 'token789', GETDATE(), GETDATE()),
    ('Bob', 'Brown', 'bob.brown', 'bob.brown@example.com', 'password101', 'Data Scientist', 'token101', GETDATE(), GETDATE());

-- Seed the QUESTIONS table
INSERT INTO QUESTIONS
    (Title, Content, createdAt, updatedAt, UserID)
VALUES
    ('What is SQL?', 'Can someone explain what SQL is and how it is used?', GETDATE(), GETDATE(), 1),
    ('How to optimize a database query?', 'I am facing performance issues with some queries, any suggestions?', GETDATE(), GETDATE(), 2),
    ('What is the difference between an inner join and a left join?', 'Can anyone explain the difference between inner and left joins?', GETDATE(), GETDATE(), 3),
    ('How to handle NULL values in SQL?', 'I am confused about handling NULL values in SQL, can someone help?', GETDATE(), GETDATE(), 4);

-- Seed the ANSWERS table
INSERT INTO ANSWERS
    (content, upvotes, downvotes, createdAt, updatedAt, UserID, QuesID)
VALUES
    ('SQL stands for Structured Query Language. It is used to communicate with databases.', 5, 0, GETDATE(), GETDATE(), 1, 1),
    ('To optimize a query, try to reduce the number of joins and indexes. Use proper indexes and avoid SELECT *.', 7, 1, GETDATE(), GETDATE(), 2, 2),
    ('An inner join returns only the rows where there is a match in both tables. A left join returns all rows from the left table, and matching rows from the right table, or NULL if no match is found.', 10, 0, GETDATE(), GETDATE(), 3, 3),
    ('Use IS NULL to check for NULL values in SQL. You can also use COALESCE or IFNULL to replace NULL with a default value.', 3, 0, GETDATE(), GETDATE(), 4, 4);

-- Seed the QTAG table
INSERT INTO QTAG
    (Tag)
VALUES
    ('SQL'),
    ('Database'),
    ('Optimization'),
    ('Joins'),
    ('NULL');

-- Seed the Question_QTAG table (Many-to-Many relationship between QUESTIONS and QTAG)
INSERT INTO Question_QTAG
    (QuesID, QTagID)
VALUES
    (1, 1),
    (2, 3),
    (3, 4),
    (4, 5),
    (1, 2),
    (2, 1),
    (3, 2),
    (4, 1);

-- Query to verify the inserted data
SELECT *
FROM USERS;
SELECT *
FROM QUESTIONS;
SELECT *
FROM ANSWERS;
SELECT *
FROM QTAG;
SELECT *
FROM Question_QTAG;

