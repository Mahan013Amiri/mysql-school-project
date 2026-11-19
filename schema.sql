CREATE DATABASE IF NOT EXISTS school_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE school_db;

CREATE TABLE IF NOT EXISTS students (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  email      VARCHAR(100) UNIQUE,
  age        INT,
  phone      VARCHAR(15) UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);