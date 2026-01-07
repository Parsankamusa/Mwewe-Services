import string
import random
import time
import hashlib

def password_gen(length=12):
    """Generate random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def hash_gen():
    """Generate unique hash for IDs."""
    random.seed(time.time())
    characters = string.ascii_letters + string.digits
    char_mangle = ''.join(random.choice(characters) for _ in range(12))
    return hashlib.shake_256(char_mangle.encode()).hexdigest(10)
