class Database:
    def __init__(self):
        self.users = {}

    def set_user_credentials(self, user_id: int, username: str, password: str):
        self.users[user_id] = {"username": username, "password": password}

    def delete_user_credentials(self, user_id: int):
        return self.users.pop(user_id, None)

    def get_user_credentials(self, user_id: int):
        creds = self.users.get(user_id)
        if creds:
            return creds["username"], creds["password"]
        return None, None

db = Database()
