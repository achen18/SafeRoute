import sqlite3 
import hashlib
import os

DATABASE_NAME = 'users.db'

def database_init() -> None:
    """
    Create users.db if it does not exist already. 

    Arguments:
        None

    Returns:
        None

    Usage:
    Creates sqlite3 database "users.db". Within this, creates two tables, "accounts" and "profiles".  
    "accounts" takes username (unique), password, salt, and a role ('student' or 'admin')
    """
    with sqlite3.connect(DATABASE_NAME) as db:
        # store role for student/admin
        db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                userid INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL, 
                password TEXT NOT NULL, 
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'student'
            )
        """)
        
        # foreign key linked to accounts table
        db.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                userid INTEGER PRIMARY KEY,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                CONSTRAINT fk_user FOREIGN KEY(userid) REFERENCES accounts(userid) ON DELETE CASCADE
            )
        """)
        db.commit()

def generate_salt() -> str:
    """
    Generates random salt. 

    Arguments:
        None

    Returns:
        str: random string

    Usage:
    Used internally for login.py. Generates random string using os.urandom for salting passwords.
    """
    return os.urandom(16).hex()

def hash_password(password: str, salt: str) -> str:
    """
    Uses a given password and salt to determine the resulting hashed password + salt.

    Arguments:
        password (str): password input string to encrypt
        salt (str): salt sequence from user database entry

    Returns:
        str: hashed combination of password and salt

    Usage:
    Used internally for login.py. Used to hash password + salt when registering new user and when logging in user.
    """
    if isinstance(password, dict):
        raise TypeError("Password cannot be a dictionary")
    
    hashed_bytes = hashlib.scrypt(
        password.encode(), 
        salt=salt.encode(), 
        n=16384, 
        r=8, 
        p=1
    )
    return hashed_bytes.hex()

def user_register(username: str, password: str, role: str, fname: str, lname: str) -> int:
    """
    Registers new user and profile information. 

    Arguments:
        username (str): username
        password (str): password
        role (str): authorized clearance level ('student' or 'admin')
        fname (str): first name entry
        lname (str): last name entry

    Returns: 
        int: userid if successful, -1 if user already exists 
    """
    salt = generate_salt()
    hashed_password = hash_password(password, salt)

    accounts_insert = """INSERT INTO accounts (username, password, salt, role)
                        VALUES (?, ?, ?, ?)"""
    
    profiles_insert = """INSERT INTO profiles (userid, fname, lname)
                        VALUES (?, ?, ?)"""
    try:
        with sqlite3.connect(DATABASE_NAME) as db:
            cursor = db.execute(accounts_insert, (username, hashed_password, salt, role))
            userid = cursor.lastrowid

            db.execute(profiles_insert, (userid, fname, lname))
            db.commit()
            return userid
    except sqlite3.IntegrityError:
        return -1

def user_exists(username: str) -> bool:
    """
    Determine if a given username exists.

    Arguments:
        username (str): username to be checked

    Returns:
        bool: True if match found, otherwise returns False.
    """
    find_username = "SELECT rowid FROM accounts WHERE username = ?"

    with sqlite3.connect(DATABASE_NAME) as db:
        cursor = db.execute(find_username, (username,))
        result = cursor.fetchone()
        return result is not None

def user_login(username: str, password: str) -> int | None:
    """
    Login user given username and password

    Arguments:
        username (str): attempted login username from client
        password (str): attempted password from client to hash and check

    Returns:
        int | None: returns userid if successful, returns None if username or password do not match
    """
    find_user = "SELECT userid, password, salt FROM accounts WHERE username = ?"

    with sqlite3.connect(DATABASE_NAME) as db:
        cursor = db.execute(find_user, (username,))
        result = cursor.fetchone()

    if result is None:
        return None
    
    userid, stored_password, salt = result

    if hash_password(password, salt) == stored_password:
        return userid
    
    return None

def get_user_profile(username: str) -> dict | None:
    """
    Retrieve a user's profile information

    Arguments:
        username (str): targeted username to look for

    Returns:
        dict | None: dictionary mapping profile details ('username', 'role', 'fname', 'lname') if found, else None.
    """
    with sqlite3.connect(DATABASE_NAME) as db:
        cursor = db.execute(
            """SELECT a.username, a.role, p.fname, p.lname 
               FROM accounts a JOIN profiles p ON a.userid = p.userid 
               WHERE a.username = ?""",
            (username,)
        )
        row = cursor.fetchone()
    
    if row:
        return {
            'username': row[0],
            'role': row[1],
            'fname': row[2],
            'lname': row[3],
        }
    return None


def update_password(username: str, new_password: str) -> bool:
    """
    Updates users's password

    Arguments:
        username (str): username of acconut to update
        new_password (str): new password to replace old password

    Returns:
        bool: Evaluates True if updates are successful, otherwise returns False.
    """
    salt = generate_salt()
    hashed = hash_password(new_password, salt)

    with sqlite3.connect(DATABASE_NAME) as db:
        cursor = db.execute(
            "UPDATE accounts SET password = ?, salt = ? WHERE username = ?",
            (hashed, salt, username)
        )
        db.commit()
        return cursor.rowcount > 0


def delete_user(username: str) -> None:
    """
    Deletes a user account

    Arguments:
        username (str): username of acconut to delete

    Returns:
        None
    """
    with sqlite3.connect(DATABASE_NAME) as db:
        db.execute("PRAGMA foreign_keys=on")
        db.execute("DELETE FROM accounts WHERE username = ?", (username,))
        db.execute("PRAGMA foreign_keys=off")
        db.commit()

def get_username(userid: int) -> str | None:
    """
    Retrieve a username given a numeric userid

    Arguments:
        userid (int): userid associated with username of interest

    Returns:
        str | None: text username if exists, else None
    """
    with sqlite3.connect(DATABASE_NAME) as db:
        cursor = db.execute("SELECT username FROM accounts WHERE userid = ?", (userid,))
        result = cursor.fetchone()
    
    if result:
        return result[0]
    return None

if __name__ == "__main__":
    database_init()
    print("Database initialized.")

    uid = user_register("A", "password", "admin", "Aaron", "Chen")
    print(get_user_profile("A"))
    print("User registered successfully.")

    update_password("A", "2")
    print("Password updated.")
    print(get_user_profile("A"))

    logged_uid = user_login("A", "2")
    print(f"Logged in user ID: {logged_uid}")

    delete_user("A")
    print("User deleted clean.")