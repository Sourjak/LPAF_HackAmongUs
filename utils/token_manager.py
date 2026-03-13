import jwt
from datetime import datetime, timedelta
from flask import current_app


def generate_session_token(session_id):
    """
    Generates JWT token for attendance session.
    Token expires in 90 seconds.
    """

    payload = {
        "session_id": session_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=90)
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return token


def verify_session_token(token):
    """
    Verifies JWT token.
    Returns decoded payload if valid.
    Returns None if invalid or expired.
    """

    try:
        decoded = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )

        return decoded

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None