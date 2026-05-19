import redis
import uuid
from flask import session
from login import get_user_profile

r_server = redis.StrictRedis()
try:
    r_server.ping()
except Exception:
    print("REDIS: Not Running -- No Streams Available")
    r_server = None


def create_session(userid: int) -> str | None:
    """
    Initialize user session, store associated uuid in Redis dict.

    Arguments:
        userid (int): associated userid of account to start session for 

    Returns:
        str | None: UUID string with session token, or None if unable to reach Redis
    """
    if r_server is None:
        return None
    token = str(uuid.uuid4())
    r_server.set(token, userid)
    return token


def get_user_from_token(token: str) -> int | None:
    """
    Retrieve userid from Redis given token.

    Arguments:
        token (str): tracking token associated with a userid

    Returns:
        int | None: returns userid if token, found, None if unable to find token or user
    """
    if r_server is None or token is None:
        return None
    userid = r_server.get(token)
    if userid is None:
        return None
    return int(userid.decode())


def delete_session(token: str) -> bool:
    """
    Delete user's current session by removing session token from Redis.

    Arguments:
        token (str): associated user token to delete the entry for

    Returns:
        bool: Evaluates True if deletion successful, otherwise returns False
    """
    if r_server is None or token is None:
        return False
    r_server.delete(token)
    return True


def login_user(user_data: dict) -> bool:
    """
    Bridges Redis session management with app routing system.
    Expects user_data to contain at least {"userid": int} or uses username lookup.

    Arguments:
        user_data (dict): information such as userid and username

    Returns:
        bool: True if session creation successful, else False
    """
    from login import user_login 
    
    token = create_session(user_data.get("userid"))
    if token:
        session["session_token"] = token
        session["username"] = user_data.get("username")
        return True
    return False


def logout_user() -> None:
    """
    Clears out the active Redis tracking record and drops the browser cookie.

    Arguments:
        None

    Returns:
        None
    """
    token = session.get("session_token")
    if token:
        delete_session(token)
    session.clear()


def current_user() -> dict | None:
    """
    Looks up the active session token in Redis and returns the live user profile data.

    Arguments:
        None

    Returns:
        dict | None: A map containing parameters such as ('username', 'role', etc.), else None
    """
    token = session.get("session_token")
    username = session.get("username")
    
    if not token or not username:
        return None
        
    userid = get_user_from_token(token)
    if userid is None:
        return None
        
    return get_user_profile(username)


def logged_in() -> bool:
    """
    Validation check to determine if the user has an authorized session entry.

    Arguments:
        None

    Returns:
        bool: Evaluates True if authorized, otherwise returns False.

    """
    token = session.get("session_token")
    if not token:
        return False
    return get_user_from_token(token) is not None


if __name__ == "__main__":
    print("Redis tracking wrapper loaded cleanly.")