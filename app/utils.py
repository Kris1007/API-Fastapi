# Deals with Password hashing

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended() # uses latest recommended password hashing algo by fastapi: Argon2 currently

def hash(password: str):
    return password_hash.hash(password)

def verify(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)