import hashlib


def get_hash_value(in_str, in_digest_bytes_size=64, in_return_type='digest'):
    blake = hashlib.blake2b(in_str.encode('utf-8'), digest_size=in_digest_bytes_size)
    return blake.digest()