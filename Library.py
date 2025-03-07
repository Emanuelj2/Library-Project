import mysql.connector
import bcrypt
#
# Connect to MySQL
def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="Enter the username",
        password="Enter password",
        database="Enter the db name"
    )

# Register a new user
def register_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', 
                       (username, hashed_password.decode('utf-8')))
        conn.commit()
        print(f"User {username} registered successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        conn.close()

# Authenticate user
def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        stored_hashed_password = user_data[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            return True
    return False

# User class
class User:
    def __init__(self, username):
        self.username = username

    #checkout the book
    def checkout_book(self, book_title):
        conn = connect_db()
        cursor = conn.cursor()

        # Check if user has already checked out 3 books
        cursor.execute("SELECT COUNT(*) FROM books_data WHERE status = 'checked out' AND borrowed_by = %s", (self.username,))
        count = cursor.fetchone()[0]

        if count >= 3:
            print("You can only check out up to 3 books at a time.")
            conn.close()
            return

        # Check if book is available
        cursor.execute("SELECT * FROM books_data WHERE Book_Title = %s AND status = 'available'", (book_title,))
        book = cursor.fetchone()

        if book:
            cursor.execute("UPDATE books_data SET status = 'checked out', borrowed_by = %s WHERE Book_Title = %s",
                           (self.username, book_title))
            conn.commit()
            print(f"Book '{book_title}' checked out successfully.")
        else:
            print("Book not available.")

        conn.close()

    #return the book
    def return_book(self, book_title):
        conn = connect_db()
        cursor = conn.cursor()

        # Check if the user actually checked out this book
        cursor.execute("SELECT * FROM books_data WHERE Book_Title = %s AND borrowed_by = %s", (book_title, self.username))
        book = cursor.fetchone()

        if book:
            cursor.execute("UPDATE books_data SET status = 'available', borrowed_by = NULL WHERE Book_Title = %s",
                           (book_title,))
            conn.commit()
            print(f"Book '{book_title}' returned successfully.")
        else:
            print("You haven't checked out this book.")

        conn.close()
    
    #viwe the checked out books
    def view_checked_out_books(self):
        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT Book_Title, Book_Author FROM books_data WHERE borrowed_by = %s", (self.username,))
            books = cursor.fetchall()
            if books:
                print("\nYour Checked Out Books: ")
                for book in books:
                    print(f"Titel: {book[0]}, By {book[1]}")
            else:
                print("\nYou have no books checked out.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            conn.close()    
        



# Admin class
class Admin:
    # view the checked out books
    def view_checked_out_books(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ISBN, Book_Title, borrowed_by FROM books_data WHERE status = 'checked out'")
        
        books = cursor.fetchall()

        if books:
            print("\nChecked Out Books:")
            for book in books:
                print(f"ISBN: {book[0]}, Title: {book[1]}, Borrowed by: {book[2]}")
        else:
            print("No books are currently checked out.")

        conn.close()
    #insert a book function
    #note make suer there are no duplicate books inserted
    def insert_new_book(self):
        conn = connect_db()
        cursor = conn.cursor()
        print("Insert the following inromation:")
        isbn = input("ISBN: ")
        book_title = input("Book Title: ")
        book_author = input("Book Author: ")
        publication_year = input("Publication year: ")
        publisher = input("Publisher: ")

        #these are the default values
        status = "avaliable"
        borrowed_by = None

        try:
            cursor.execute("""
                INSERT INTO books_data (ISBN , Book_Title, Book_Author, Year_Of_Publication, Publisher, status, borrowed_by)
                VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                (isbn, book_title, book_author, publication_year, publisher, status, borrowed_by))
            conn.commit()
            print(f"The Book {book_title} was inserted successfully.")
        except Exception as e:
            print(f"Error inserting book: {e}")
        finally:
            conn.close()
    
    #remove a book
    def delete_book(self):
        conn = connect_db()
        cursor =conn.cursor()
        print("Insert the following information:")
        ibsn = input("ISBN: ")
        book_title = input("Book title: ")
        book_author = input("Book Author: ")
        
        try:
            #first move the deleted book into the deleted books table
            cursor.execute(""" INSERT INTO deleted_books (ISBN, Book_Title, Book_Author, Year_Of_Publication, Publisher, status)
                           SELECT ISBN, Book_Title, Book_Author, Year_Of_Publication, Publisher, status
                           FROM books_data
                           WHERE ISBN = %s AND Book_Title = %s AND Book_Author = %s
                        """, (ibsn, book_title, book_author))
            
            #delete the book from the books_data table
            cursor.execute("""
                           DELETE FROM books_data WHERE ISBN = %s AND Book_Title = %s AND Book_Author = %s""",
                           (ibsn, book_title, book_author))
            conn.commit()
            print(f"The book {book_title} was deleted" )
        except Exception as e:
            print(f"Error deleting book: {e}") 
        finally:
            conn.close()
    
    #recover book
    def recover_book(self):
        conn = connect_db()
        cursor = conn.cursor()
        admin_choice = input("Do you want to see the list of books that have been deleted (Y/N)").strip().lower()
        
        if admin_choice == "y":
            try:
                cursor.execute("""
                            SELECT ibsn, book_title, book_author FROM deleted_books
                            """)
                books = cursor.fetchall()
                if books:
                    print("\nDeleted Books:")
                    for book in books:
                        print(f"ISBN: {book[0]}, Title: {book[1]}, Author: {book[2]}")
                else:
                    print("No deleted books found.")
            except Exception as e:
                print(f"Error recieving deleted books: {e}")    
        else:
            print("Insert the following information:")
            ibsn = input("ISBN: ")
            book_title = input("Book title: ")
            book_author = input("Book Author: ")
            try:
                cursor.execute("""
                            INSERT INTO books_data (ibsn, book_title, book_author)
                            SELECT ibsn, book_title, book_author FROM deleted_books
                            WHERE ibsn = %s AND book_title = %s AND book_author = %s
                            """, (ibsn, book_title, book_author))
                cursor.commit()
                print(f"Book {book_title} was recovered")
            except Exception as e:
                conn.rollback()
                print(f"Error recovering book: {e}")
            finally:
                cursor.close()
        

def main():
    admin = Admin()

    while True:
        print("\nLibrary System")
        print("1. Register User")
        print("2. Login User")
        print("3. Admin Login")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            register_user(username, password)

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            if authenticate_user(username, password):
                print(f"Welcome {username}!")
                user_obj = User(username)
                while True:
                    print("\nUser Menu")
                    print("1. Checkout Book")
                    print("2. Return Book")
                    print("3. Your Books")
                    print("4. Log Out")
                    user_choice = input("Choose an option: ")

                    if user_choice == "1":
                        book_title = input("Enter Book Title to checkout: ")
                        user_obj.checkout_book(book_title)
                    elif user_choice == "2":
                        book_title = input("Enter Book Title to return: ")
                        user_obj.return_book(book_title)
                    elif user_choice == "3":
                        user_obj.view_checked_out_books()
                    elif user_choice == "4":
                        break
                    else:
                        print("Invalid choice.")

        elif choice == "3":
            admin_username = input("Enter admin username: ")
            admin_password = input("Enter admin password: ")
            if admin_username == "admin" and admin_password == "admin123":
                print("Admin logged in.")
                while True:
                    print("1. View Checkout history")
                    print("2. Insert a new Book")
                    print("3. Remove a book")
                    print("4. Recover a book")
                    print("5. Log Out")
                    admin_input = input("Choose an option:")
                    if admin_input == "1":
                        admin.view_checked_out_books()
                    elif admin_input == "2":
                        admin.insert_new_book()
                    elif admin_input == "3":
                        admin.delete_book()
                    elif admin_input == "4":
                        admin.recover_book()
                    elif admin_input == "5":
                        break
                    else:
                        print("Invalid choice.")
            else:
                print("Invalid admin credentials.")


        elif choice == "4":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
