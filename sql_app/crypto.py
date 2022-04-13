
import os
from hashlib import pbkdf2_hmac

PASS_ENCODING='utf-8'
HASH_FUNC='sha256'
NUM_ITIRATIONS=100000

def get_new_salt(n_bytes : int = 32) -> bytes:
    
    if type(n_bytes) != int:
        n_bytes = 32 # Forece in case of misuse
    
    return os.urandom(n_bytes)


def gen_new_key(plain_passwd : str) -> tuple:
    """
    Generate a new key and salt to store.
    Returns (key, salt)
    """
    salt = get_new_salt(32)
    return (calc_key(plain_passwd, salt), salt)

def verify_key(plain_passwd : str, salt : bytes, stored_key : bytes) -> bool:
    key_tmp = calc_key(plain_passwd, salt)
    return (stored_key == key_tmp)

def calc_key(passwd: str, salt : bytes) -> bytes:
    return pbkdf2_hmac(HASH_FUNC, passwd.encode(PASS_ENCODING), salt, NUM_ITIRATIONS)
