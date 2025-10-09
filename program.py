"""
Project: Mini_Twitter
Author: Muhtasim Fuad Chowdhury
"""

import sqlite3
from getpass import getpass
import re
from datetime import datetime

def main():
    database = sqlite3.connect("database.db")
    main_menu(database)
    database.close()

# Main Menu
def main_menu(database):
    while True:
        print("\n\n")
        print("*" * 60)
        print("Welcome to Fuads Attempt at making a Twitter-like Platform")
        print("*" * 60)
        print("\nOptions:")
        print("1. Sign up")
        print("2. Sign in")
        print("3. Exit")

        option_selected = input("Pick an option: ").strip()

        options = {
            '1': lambda: sign_up(database),
            '2': lambda: login(database),
            '3': exitProgram
        }

        action = options.get(option_selected, defaultMainMenu)
        result = action()

        if option_selected == '3':
            print("Leaving the Platform...")
            break
        elif result is not None:
            userID = result
            userMenu(database, userID)

# Sign up page
def sign_up(database):
    cursor = database.cursor()

    # Name
    while True:
        name = input("Enter your name: ").strip()
        if name:
            break
        print("Name cannot be empty. Please try again.")

    # Email
    email_regex = r"^[a-z0-9]+[\._]?[a-z0-9]+@[\w\-]+\.\w+$"
    while True:
        email = input("Enter your email: ").strip().lower()
        if not re.match(email_regex, email):
            print("Invalid email format. Please try again.")
            continue
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print("Email is already registered. Please log in or use a different email.")
        else:
            break

    # Phone
    while True:
        phone = input("Enter your phone number: ").strip()
        if phone.isdigit():
            break
        print("Phone number must be numbers. Please try again.")

    # Password
    while True:
        pwd = getpass("Create a password: ").strip()
        if pwd:
            break
        print("Password cannot be empty. Please try again.")

    # Ask for user-chosen ID
    while True:
        usr = input("Choose a User ID: ").strip()
        if not usr:
            print("User ID cannot be empty.")
            continue
        cursor.execute("SELECT 1 FROM users WHERE usr = ?", (usr,))
        if cursor.fetchone():
            print("That User ID is already taken. Try another.")
            continue
        break

    # Insert user
    cursor.execute(
        "INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)",
        (usr, name, email, phone, pwd),
    )
    database.commit()
    print("Sign-up successful! Your user ID is " + str(usr) + "\n")
    return usr

# Log in page
def login(database):
    cursor = database.cursor()

    # Ask for user id and password
    usr = input("Enter user ID: ").strip()
    while True:
        pwd = getpass("Enter Password: ").strip()
        if pwd:
            break
        print("Password cannot be empty. Please try again.")

    # Check credentials
    query = "SELECT 1 FROM users WHERE usr = ? AND pwd = ?"
    cursor.execute(query, (usr, pwd))
    user = cursor.fetchone()
    if user:
        print("Login successful!\n")
        return usr
    else:
        print("Invalid credentials. Try again.\n")
        return None

# Menu for user to choose from AFTER logging in.
def userMenu(database, userID):
    while True:
        print("\n\n")
        print("*" * 20)
        print("Fuad's Mini Twitter")
        print("*" * 20)
        print("\nOptions:")
        print("1. Compose a post for your followers!")
        print("2. See all Users")
        print("3. See Your Feed")
        print("4. See your Following list")
        print("5. Logout")

        option_selected = input("Pick an option: ").strip()

        options = {
            "1": lambda: send_post(database, userID),
            "2": lambda: users(database, userID),
            "3": lambda: posts(database, userID),
            "4": lambda: following_list(database, userID),
            "5": logout,
        }

        action = options.get(option_selected, defaultUserMenu)
        action()

        if option_selected == "5":
            break

# Page to post something for your followers to see
def send_post(database, userID):
    cursor = database.cursor()

    print("\n" + "-" * 40)
    print("Compose a post (Limit: 360 characters)")
    print("Type 'back' to cancel.")
    print("-" * 40)

    while True:
        content = input("> ").strip()

        if not content:
            print("Empty input. Discarded. Returning to Menu...")
            return

        if content.lower() == "back":
            print("Returning to menu...")
            return

        if len(content) > 360:
            print(f"Your post is {len(content)} characters; Maximum is 360 characters.")
            continue

        cursor.execute(
            "INSERT INTO posts (author_usr, content, created_at) VALUES (?, ?, datetime('now'))",
            (userID, content),
        )

        database.commit()

        print("Posted! Your followers will see this in their feed now.")
        return

# Page to see all users of the Program
def users(database, userID):
    cursor = database.cursor()

    while True:
        cursor.execute("""
            SELECT usr, name, email
            FROM users
            ORDER BY LOWER(name), email
        """)
        rows = cursor.fetchall()

        # Drop down of all users registered in the program (10 per page MAX)
        if not rows:
            print("There are no users yet.")
            while True:
                cmd = input("Type 'back' to return: ").strip().lower()
                if cmd == "back":
                    print("Going back...")
                    return
                else:
                    print("Invalid input. Type 'back' to return.")
        
        print(f"\nAll users ({len(rows)}):\n" + "-" * 40)

        page_size = 5
        i = 0
        while i < len(rows):
            for usr, name, email in rows[i:i + page_size]:
                me = " (you)" if usr == userID else ""
                print(f"ID: {usr}{me}")
                print(f"Name: {name}")
                print(f"Email: {email}")
                print("-" * 40)

            i += page_size

            if i < len(rows):
                # To go next page (If there are more users left) or go back to userMenu
                while True:
                    next_page = input("Press Enter for more, or type 'back' to return: ").strip().lower()
                    if next_page == "":
                        break
                    elif next_page == "back":
                        print("Going back...")
                        return
                    else:
                        print("Invalid input. Press Enter for more, or type 'back' to return.")
            else:
                # Once all user have been shown, you can view all users again, follow a user or go back to userMenu page
                while True:
                    choice = input("End of list. Press Enter to view again, type 'follow' to follow someone, or type 'back' to return\n>").strip().lower()
                    if choice == "":
                        print("\nRestarting list...\n" + "-" * 40)
                        i = 0
                        break
                    elif choice == "follow":
                        follow_user(database, userID)
                        return
                    elif choice == "back":
                        print("Going back...")
                        return
                    else:
                        print("Invalid input. Press Enter to view again, or type 'back' to return.")        

# Page taken to from users page to follow someone
def follow_user(database, userID):
    while True:
        # Type User ID of user you want to follow
        id_typed = input("Enter the user ID of the user you want to follow: or 'back' to go back to userMenu\n>").strip()

        if not id_typed:
            print("Please enter a user ID or type 'back' to return")
            continue
        if id_typed.lower() == "back":
            print("Going back...")
            return
        if id_typed == userID:
            print("You cannot follow yourself")
            continue
        if not user_exists(database, id_typed):
            print("Invalid User ID. To be clear, User ID is case-sensitive. Cannot accept 'bob_' if id is 'Bob_'")
            continue
        if is_following(database, userID, id_typed):   
            print(f"You already follow {id_typed}")  
            continue  

        # Exception just in case
        try:
            database.execute(
                "INSERT INTO follows (follower_usr, followee_usr, created_at) VALUES (?, ?, datetime('now'))",
                (userID, id_typed),
            )
            database.commit()
            print(f"You are now following {id_typed}.")

            while True:
                nxt = input("Press Enter to follow someone else, or type 'back' to return: ").strip().lower()
                if nxt == "":
                    break
                elif nxt == "back":
                    print("Going back...")
                    return
                else:
                    print("Invalid input. Press Enter to continue, or type 'back' to return.")

        except sqlite3.IntegrityError as e:
            print("Could not follow user:", e)      

# Page to see posts of users you follow
def posts(database, userID):
    cur = database.cursor()

    # SQL code for displaying selected users ID
    cur.execute("""
        SELECT p.id, p.author_usr, u.name, p.content, p.created_at
        FROM posts p
        JOIN follows f ON f.followee_usr = p.author_usr
        JOIN users  u ON u.usr = p.author_usr
        WHERE f.follower_usr = ?
        ORDER BY datetime(p.created_at) DESC
    """, (userID,))

    rows = cur.fetchall()

    # Drop down of posts of your followers (10 per page MAX)
    if not rows:
        print("No posts in your feed yet.")
        return

    print("\nYour feed:\n" + "-" * 40)
    PAGE = 5
    i = 0
    while i < len(rows):
        for pid, author, name, content, created in rows[i:i+PAGE]:
            print(f"{name} (@{author}) | {created}")
            print(content)
            print("-" * 40)
        i += PAGE
        if i < len(rows):
            while True:
                nxt = input("Press Enter for more, or type 'back' to return: ").strip().lower()
                if nxt == "":
                    break
                elif nxt == "back":
                    return
                else:
                    print("Invalid input. Press Enter or 'back'.")
       
# Page to see all the users you follow
def following_list(database, userID):
    cur = database.cursor()

    # SQL code to display selected users
    cur.execute("""
        SELECT u.usr, u.name
        FROM follows f
        JOIN users u ON u.usr = f.followee_usr
        WHERE f.follower_usr = ?
        ORDER BY LOWER(u.name), u.usr
    """, (userID,))

    # Drop down of all users you follow (10 per page MAX)
    rows = cur.fetchall()

    if not rows:
        print("You're not following anyone yet.")
        return

    print("\nYou're following:\n" + "-" * 40)
    PAGE = 10
    i = 0
    while i < len(rows):
        for usr, name in rows[i:i+PAGE]:
            print(f"{name} (@{usr})")
            print("-" * 40)
        i += PAGE
        if i < len(rows):
            while True:
                nxt = input("Press Enter for more, or type 'back' to return: ").strip().lower()
                if nxt == "":
                    break
                elif nxt == "back":
                    return
                else:
                    print("Invalid input. Press Enter or 'back'.")

# helpers/messages
# function to check if user ID inputted in follow_user page exists or not
def user_exists(db, usr: str) -> bool:
    return db.execute("SELECT 1 FROM users WHERE usr = ?", (usr,)).fetchone() is not None

# function to check if user already follows user ID or not
def is_following(db, follower: str, followee: str) -> bool:
    return db.execute("""
        SELECT 1 FROM follows WHERE follower_usr = ? AND followee_usr = ?""",
        (follower, followee)
    ).fetchone() is not None
    
def exitProgram():
    print("Exiting the program. Goodbye...")

def defaultMainMenu():
    print("Invalid! Please select a number between 1 and 3.")

def defaultUserMenu():
    print("Invalid! Please select a number between 1 and 5")

def logout():
    print("Logging out. Goodbye...")

if __name__ == "__main__":
    main()
