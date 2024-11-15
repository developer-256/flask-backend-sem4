-- delete  database forcefully

-- USE master;
-- ALTER DATABASE [Project] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
-- DROP DATABASE [Project];


USE master
GO

IF NOT EXISTS (
    SELECT name
FROM sys.databases
WHERE name = N'Project'
)
CREATE DATABASE Project
GO


USE Project
GO

IF NOT EXISTS (
    SELECT name
FROM sys.tables
WHERE name = N'USERS'
)
CREATE TABLE USERS
(
    UserID INT PRIMARY KEY IDENTITY(1, 1),
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    UserName VARCHAR(50) NOT NULL UNIQUE,
    Email VARCHAR(50) NOT NULL UNIQUE,
    UserPassword VARCHAR(50) NOT NULL,
    Bio VARCHAR(300),
    SessionToken VARCHAR(50),
    createdAt datetime NOT NULL,
    updatedAt datetime NOT NULL
)
GO

IF NOT EXISTS (
    SELECT name
FROM sys.tables
WHERE name = N'QUESTIONS'
)
CREATE TABLE QUESTIONS
(
    QuesID INT PRIMARY KEY IDENTITY(1, 1),
    Title VARCHAR(100),
    Content TEXT,
    createdAt datetime NOT NULL,
    updatedAt datetime NOT NULL,
    UserID INT,
    FOREIGN KEY(UserID) REFERENCES USERS(UserID)
)
GO

IF NOT EXISTS (
    SELECT name
FROM sys.tables
WHERE name = N'ANSWERS'
)
CREATE TABLE ANSWERS
(
    AnsID INT PRIMARY KEY IDENTITY(1, 1),
    content TEXT,
    upvotes INT DEFAULT 0,
    downvotes INT DEFAULT 0,
    UserID INT,
    Foreign Key (UserID) REFERENCES USERS(UserID),
    QuesID INT,
    Foreign Key (QuesID) REFERENCES QUESTIONS(QuesID)
)
GO

IF NOT EXISTS (
    SELECT name
FROM sys.tables
WHERE name = N'QTAG'
)
CREATE TABLE QTAG
(
    QTagID INT PRIMARY KEY IDENTITY(1, 1),
    name VARCHAR(50) UNIQUE NOT NULL
)
GO


IF NOT EXISTS (
    SELECT name
FROM sys.tables
WHERE name = N'Question_QTAG'
)
CREATE TABLE Question_QTAG
(
    QuesID INT,
    QTagID INT,
    PRIMARY KEY (QuesID, QTagID),
    Foreign Key (QuesID) REFERENCES QUESTIONS(QuesID),
    Foreign Key (QTagID) REFERENCES QTAG(QTagID)
)
GO

select *
from USERS
WHERE UserName = 'usman'