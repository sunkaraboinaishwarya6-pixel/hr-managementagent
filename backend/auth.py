import bcrypt

from database import db


def _build_crypt_context():
    class BcryptContext:
        def hash(self, password):
            if isinstance(password, str):
                password = password.encode("utf-8")
            return bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

        def verify(self, password, hashed_password):
            if isinstance(password, str):
                password = password.encode("utf-8")
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password, hashed_password)

    return BcryptContext()


pwd_context = _build_crypt_context()


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

def create_user(name, email, password, role="EMPLOYEE"):
    cursor = db.cursor()

    password_hash = hash_password(password)

    query = """
    INSERT INTO users (name, email, password_hash, role)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (name, email, password_hash, role))
    db.commit()

    cursor.close()

    return "User created successfully"

def login_user(email, password):
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT user_id, name, email, password_hash, role
    FROM users
    WHERE email = %s
    """

    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()

    if not user:
        return "User not found"

    if not verify_password(password, user["password_hash"]):
        return "Invalid password"

    return {
        "message": "Login successful",
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }