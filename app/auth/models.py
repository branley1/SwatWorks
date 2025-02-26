from flask_login import UserMixin

# Simple in-memory user database
users_db = {
    "bmmasi1": "password123",
    "jjones6": "password123",
    "mfalkju1": "password123",
    "vtadevo1": "password123"
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username
        
    @staticmethod
    def check_password(username, password):
        # Check if username and password are valid
        return username in users_db and users_db[username] == password

    @staticmethod
    def get_all_users():
        # Return a list of all usernames
        return list(users_db.keys())
    
    @staticmethod
    def add_user(username, password):
        # Add a new user to the database
        if username in users_db:
            return False  # User already exists
        users_db[username] = password
        return True
        
    @staticmethod
    def get(user_id):
        # Get user by ID (username)
        if user_id in users_db:
            return User(user_id)
        return None
