-- Active: 1731131296284@@127.0.0.1@1433@master
-- create database uniproj

SELECT HAS_PERMS_BY_NAME(null, null, 'CREATE ANY DATABASE') AS CanCreateDatabase;


CREATE TABLE Users
(
    UserId INT PRIMARY KEY IDENTITY(1, 1),-- Auto-incrementing ID
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    UserName VARCHAR(50) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    UserPin VARCHAR(15) NOT NULL,
    sessionToken VARCHAR(50),
);

-- ALTER TABLE Users
-- ALTER COLUMN sessionToken VARCHAR(50);

CREATE NONCLUSTERED INDEX idx_sessionToken
ON Users (sessionToken);

-- Insert some users with valid session tokens
INSERT INTO Users
    (FirstName, LastName, Email, UserPin, sessionToken)
VALUES
    ('Alice', 'Johnson', 'alice.johnson@example.com', '12345', 'token1'),
    ('Bob', 'Smith', 'bob.smith@example.com', '67890', 'token2'),
    ('Charlie', 'Brown', 'charlie.brown@example.com', 'abcde', 'token3'),
    ('David', 'Williams', 'david.williams@example.com', '54321', NULL),
    ('Eve', 'Davis', 'eve.davis@example.com', '09876', NULL);

select *
from Users
