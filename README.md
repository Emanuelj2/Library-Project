# Library Management System

## Overview
This project is a Library Management System that allows users to register, check out books, return books, and view their borrowed books. An admin can manage books, view checkout history, and recover deleted books. The system uses MySQL for data storage and Python for handling user interactions.

## Features
### User Features:
- User Registration and Authentication (hashed passwords using bcrypt)
- Checkout up to 3 books at a time
- Return books
- View checked-out books

### Admin Features:
- View all checked-out books
- Insert new books (ensures no duplicates)
- Remove books (moved to a deleted books table)
- Recover deleted books
- Auto-delete old deleted books (via MySQL Event Scheduler)

## Technologies Used
- **Backend:** Python (MySQL Connector, bcrypt)
- **Database:** MySQL
- **Security:** Hashed passwords using bcrypt

## Installation and Setup
### Prerequisites
- Python 3.x installed
- MySQL Server installed
- MySQL Workbench (optional, for database management)
- Required Python libraries:
  ```sh
  pip install mysql-connector-python bcrypt
  ```

### Database Setup
1. Open MySQL Workbench.
2. Run the provided SQL script (`library_schema.sql`) to create the necessary tables.
3. Ensure the MySQL Event Scheduler is enabled to manage deleted books automatically:
   ```sql
   SET GLOBAL event_scheduler = ON;
   ```

### Running the Application
1. Update the `connect_db` function in `library_system.py` with your MySQL credentials.
2. Run the script:
   ```sh
   python library_system.py
   ```
3. Follow the prompts to register, login, and manage books.

## Database Schema
### Tables
- **Users**: Stores user login information.
- **Books**: Stores book details and their availability status.
- **Deleted Books**: Stores removed books with a timestamp for recovery.

## Future Improvements
- Implement a web interface using Flask or Django.
- Add email notifications for due dates.
- Enhance admin controls with a web dashboard.


