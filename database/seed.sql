USE Project
GO

INSERT INTO USERS
    (FirstName, LastName, UserName, Email, UserPassword, Bio, createdAt, updatedAt)
VALUES
    ('John', 'Doe', 'johndoe', 'johndoe@example.com', 'password123', 'Software Engineer', GETDATE(), GETDATE()),
    ('Jane', 'Smith', 'janesmith', 'janesmith@example.com', 'securepass456', 'Data Scientist', GETDATE(), GETDATE()),
    ('Alice', 'Brown', 'alicebrown', 'alicebrown@example.com', 'mypassword789', 'Product Manager', GETDATE(), GETDATE()),
    ('Bob', 'Williams', 'bobw', 'bobw@example.com', 'bobpass', 'Full-Stack Developer', GETDATE(), GETDATE()),
    ('Charlie', 'Davis', 'charlied', 'charlied@example.com', 'charlie123', 'Front-End Developer', GETDATE(), GETDATE()),
    ('Eva', 'Wilson', 'evaw', 'evaw@example.com', 'evapass', 'UX Designer', GETDATE(), GETDATE()),
    ('Frank', 'Miller', 'frankm', 'frankm@example.com', 'frankpass', 'DevOps Engineer', GETDATE(), GETDATE()),
    ('Grace', 'Taylor', 'gracet', 'gracet@example.com', 'grace123', 'Database Admin', GETDATE(), GETDATE()),
    ('Hank', 'Anderson', 'hanka', 'hanka@example.com', 'hankpass', 'Back-End Developer', GETDATE(), GETDATE()),
    ('Isabel', 'Thomas', 'isabelt', 'isabelt@example.com', 'isabel123', 'QA Engineer', GETDATE(), GETDATE());

INSERT INTO QUESTIONS
    (Title, Content, createdAt, updatedAt, UserID)
VALUES
    ('How to learn SQL?', 'I am looking for resources to learn SQL. Any suggestions?', GETDATE(), GETDATE(), 1),
    ('Best practices for database normalization?', 'Should I always normalize my database?', GETDATE(), GETDATE(), 2),
    ('What is the best way to secure a web app?', 'How do you handle security in web development?', GETDATE(), GETDATE(), 3),
    ('Tips for optimizing SQL queries?', 'Any tips on improving SQL query performance?', GETDATE(), GETDATE(), 4),
    ('How to set up DevOps for small teams?', 'What are essential tools and processes?', GETDATE(), GETDATE(), 5),
    ('How to use CSS Grid?', 'I am struggling to understand CSS Grid layout.', GETDATE(), GETDATE(), 6),
    ('Differences between SQL and NoSQL?', 'Which database is better for scalability?', GETDATE(), GETDATE(), 7),
    ('Best data types for large text?', 'Need help choosing the right data type.', GETDATE(), GETDATE(), 8),
    ('When to use indexes in SQL?', 'Do indexes always improve performance?', GETDATE(), GETDATE(), 9),
    ('What is a JOIN in SQL?', 'Can someone explain JOIN types?', GETDATE(), GETDATE(), 10);

INSERT INTO ANSWERS
    (Content, upvotes, downvotes, UserID, QuesID)
VALUES
    ('Try using JOINs instead of subqueries.', 5, 0, 1, 1),
    ('Normalizing helps avoid redundancy.', 10, 1, 2, 2),
    ('Always sanitize user input to avoid SQL injection.', 8, 1, 3, 3),
    ('Use indexes to speed up queries.', 7, 0, 4, 4),
    ('Use Docker and Jenkins for CI/CD.', 12, 2, 5, 5),
    ('Learn CSS Grid by practice.', 3, 1, 6, 6),
    ('SQL is good for structured data.', 6, 0, 7, 7),
    ('Use TEXT type for large text data.', 4, 0, 8, 8),
    ('Indexes improve read speed, not write.', 9, 1, 9, 9),
    ('JOINs combine tables based on relationships.', 11, 1, 10, 10);

INSERT INTO QTAG
    (Name)
VALUES
    ('SQL'),
    ('Security'),
    ('Optimization'),
    ('Web Development'),
    ('DevOps'),
    ('CSS'),
    ('NoSQL'),
    ('Database Design'),
    ('Performance'),
    ('JOINs');

INSERT INTO Question_QTAG
    (QuesID, QTagID)
VALUES
    -- 'How to learn SQL?' tagged with 'SQL'
    (1, 1),
    -- 'Best practices for database normalization?' tagged with 'Database Design'
    (2, 8),
    -- 'What is the best way to secure a web app?' tagged with 'Security'
    (3, 2),
    -- 'Tips for optimizing SQL queries?' tagged with 'Optimization'
    (4, 3),
    -- 'How to set up DevOps for small teams?' tagged with 'DevOps'
    (5, 5),
    -- 'How to use CSS Grid?' tagged with 'CSS'
    (6, 6),
    -- 'Differences between SQL and NoSQL?' tagged with 'NoSQL'
    (7, 7),
    -- 'Best data types for large text?' tagged with 'Database Design'
    (8, 8),
    -- 'When to use indexes in SQL?' tagged with 'Performance'
    (9, 9),
    -- 'What is a JOIN in SQL?' tagged with 'JOINs'
    (10, 10);
