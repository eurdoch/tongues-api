class UserAlreadyExistsException(Exception):
    def __init__(self):
        super().__init__()
        self.status_code = 400
        self.detail = "User already exists"
