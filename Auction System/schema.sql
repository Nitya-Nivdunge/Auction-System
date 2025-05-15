-- Drop database if exists
DROP DATABASE IF EXISTS auction_system;

-- Create database
CREATE DATABASE auction_system;
USE auction_system;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Create auctions table
CREATE TABLE auctions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    min_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    created_by INT NOT NULL,
    winner_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    chat_log TEXT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id)
);

-- Create bids table
CREATE TABLE bids (
    id INT AUTO_INCREMENT PRIMARY KEY,
    auction_id INT NOT NULL,
    user_id INT NOT NULL,
    bid_amount DECIMAL(10, 2) NOT NULL,
    bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lamport_time INT NOT NULL DEFAULT 0,
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create chat table
CREATE TABLE chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    auction_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    timestamp VARCHAR(20) NOT NULL,
    date VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auction_id) REFERENCES auctions(id)
);