from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import sqlite3
import os
import datetime

bcrypt = Bcrypt()

# Database paths
# Place users.db inside the app directory
USERS_DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
# Place gigs.db in the main project directory (same level as run.py)
GIGS_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gigs.db')

COMMENTS_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'comments.db')


def init_comments_db():
    conn = sqlite3.connect(COMMENTS_DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY, 
            gigId INTEGER, 
            username TEXT,
            text TEXT,  
            date TEXT  
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Comments database initialized at {COMMENTS_DB_PATH}")
# Initialize the users database
def init_users_db():
    conn = sqlite3.connect(USERS_DB_PATH)
    c = conn.cursor()
    # Create users table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            name TEXT,
            class_year INTEGER,
            dorm TEXT,
            venmo TEXT
        )
    ''')
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]

    if 'venmo' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN venmo TEXT")
    conn.commit()
    conn.close()
    print(f"Users database initialized at {USERS_DB_PATH}")


def init_gigs_db():
    conn = sqlite3.connect(GIGS_DB_PATH)
    cursor = conn.cursor()
    # Create the gigs table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gigs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_status TEXT,
            title TEXT,
            description TEXT,
            compensation TEXT,
            budget REAL,
            category TEXT,
            user_id TEXT,
            date TEXT,
            compensation_type TEXT,
            venmo TEXT
        )
    """)
    cursor.execute("PRAGMA table_info(gigs)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'venmo' not in columns:
        cursor.execute("ALTER TABLE gigs ADD COLUMN venmo TEXT")
    conn.commit()
    conn.close()
    print(f"Gigs database initialized at {GIGS_DB_PATH}")


def get_db(): # This gets the USER database connection
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Dbs intialized in __init__.py

class User(UserMixin):
    def __init__(self, username, name=None, class_year=None, dorm=None, venmo=None):
        self.id = username
        self.username = username
        self.name = name
        self.class_year = class_year
        self.dorm = dorm
        self.venmo=venmo
        
    @property
    def class_standing(self):
        if not self.class_year:
            return None

        try:
            current_year = datetime.date.today().year
            year_diff = int(self.class_year) - current_year

            if year_diff == 1:
                return "Senior"
            elif year_diff == 2:
                return "Junior"
            elif year_diff == 3:
                return "Sophomore"
            elif year_diff == 4:
                return "Freshman"
            elif year_diff <= 0:
                 return f"Alumnus ({self.class_year})"
            else:
                return f"Future Student ({self.class_year})"
        except (ValueError, TypeError):
             return None

    @staticmethod
    def check_password(username, password):
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        
        if result:
            stored_hash = result['password_hash']
            return bcrypt.check_password_hash(stored_hash, password)
        return False

    @staticmethod
    def get_all_users():
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT username FROM users')
        users = [row['username'] for row in c.fetchall()]
        conn.close()
        return users
    
    @staticmethod
    def add_user(username, password, name=None, class_name=None, dorm=None, venmo=None):
        conn = get_db()
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        if c.fetchone():
            conn.close()
            return False  # User already exists
            
        # Add new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            graduation_year = None
            if class_name:
                current_year = datetime.date.today().year
                if class_name == "Senior":
                    graduation_year = current_year + 1
                elif class_name == "Junior":
                    graduation_year = current_year + 2
                elif class_name == "Sophomore":
                    graduation_year = current_year + 3
                elif class_name == "Freshman":
                    graduation_year = current_year + 4

            c.execute('INSERT INTO users (username, password_hash, name, class_year, dorm, venmo) VALUES (?, ?, ?, ?, ?, ?)',
                     (username, hashed_password, name, graduation_year, dorm, venmo))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            conn.rollback()
            conn.close()
            return False
        
    @staticmethod
    def get(user_id):
        conn = get_db()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT username, name, class_year, dorm, venmo FROM users WHERE username = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return User(username=result['username'], name=result['name'], class_year=result['class_year'], dorm=result['dorm'], venmo=result['venmo'])
        return None

    @staticmethod
    def update_profile(user_id, name=None, dorm=None, venmo=None, class_year=None, new_password=None):
        conn = get_db() # Assumes get_db provides a connection with row_factory
        c = conn.cursor()
        
        updates = []
        params = []

        # Add fields to update if they are provided (and not empty strings)
        if name is not None: # Allow empty string to clear name, check for None
             updates.append("name = ?")
             params.append(name)
        if dorm is not None: # Allow empty string to clear dorm
             updates.append("dorm = ?")
             params.append(dorm)
        if venmo is not None: # Allow empty string to clear venmo
             updates.append("venmo = ?")
             params.append(venmo)
        if class_year is not None: # class_year can be None or an integer
            updates.append("class_year = ?")
            params.append(class_year)
            
        # Handle password update separately
        password_updated = False
        if new_password:
            # Hash the new password
            try:
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                updates.append("password_hash = ?")
                params.append(hashed_password)
                password_updated = True
            except Exception as e:
                 print(f"Error hashing new password for {user_id}: {e}")
                 conn.close()
                 return False # Indicate failure due to hashing error

        if not updates: # No fields to update
            conn.close()
            return True # Nothing to do, consider it success or maybe indicate no change?

        # Build the UPDATE query
        sql = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
        params.append(user_id)
        
        try:
            c.execute(sql, tuple(params))
            conn.commit()
            conn.close()
            return True # Indicate success
        except Exception as e:
            print(f"Error updating profile for {user_id}: {e}")
            conn.rollback()
            conn.close()
            return False # Indicate failure
