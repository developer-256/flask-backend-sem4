-- Active: 1731131296284@@127.0.0.1@1433@Project
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
    likes INT DEFAULT '0',
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
    createdAt datetime NOT NULL,
    updatedAt datetime NOT NULL,
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
    Tag VARCHAR(50) UNIQUE NOT NULL
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

SELECT
    QUESTIONS.QuesID,
    QUESTIONS.UserID,
    USERS.UserName,
    QUESTIONS.Title,
    QUESTIONS.Content,
    QUESTIONS.updatedAt,
    STUFF((
    SELECT ', ' + QTAG.Tag
    FROM QTAG
        INNER JOIN Question_QTAG ON Question_QTAG.QTagID = QTAG.QTagID
    WHERE Question_QTAG.QuesID = QUESTIONS.QuesID
    FOR XML PATH('')
), 1, 1, '') AS Tags
FROM
    QUESTIONS
    INNER JOIN USERS ON QUESTIONS.UserID = USERS.UserID
ORDER BY QUESTIONS.updatedAt;

SELECT
    QUESTIONS.QuesID,
    QUESTIONS.UserID,
    USERS.UserName,
    QUESTIONS.Title,
    QUESTIONS.Content,
    QUESTIONS.updatedAt
FROM
    QUESTIONS
    INNER JOIN USERS ON QUESTIONS.UserID = USERS.UserID
ORDER BY QUESTIONS.updatedAt;

SELECT *
FROM QTAG


SELECT
    QUESTIONS.QuesID,
    QUESTIONS.Title,
    QUESTIONS.createdAt
FROM
    QUESTIONS
    INNER JOIN Question_QTAG ON Question_QTAG.QuesID = QUESTIONS.QuesID
    INNER JOIN QTAG ON QTAG.QTagID = Question_QTAG.QTagID
WHERE 
    QTAG.QTagID = 1;




SELECT
    QTAG.QTagID,
    QTAG.Tag,
    COUNT(QUESTIONS.QuesID) AS TotalQuestions
FROM
    QTAG
    LEFT JOIN
    Question_QTAG ON QTAG.QTagID = Question_QTAG.QTagID
    LEFT JOIN
    QUESTIONS ON Question_QTAG.QuesID = QUESTIONS.QuesID
GROUP BY 
    QTAG.QTagID, QTAG.Tag
ORDER BY 
    TotalQuestions DESC;

