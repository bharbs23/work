import hashlib
import binascii
from os import urandom

class Password(object):

    def __init__(self, user=None, pwhash=None):

        self.user = user
        self.pwhash = pwhash

    def auth_check(self, text_pass, hex_hash):

        salt = hex_hash.split(':')[0]
        test_hash = self.make_hash(text_pass, salt)

        if test_hash == hex_hash:
            return True
        
        return False

    def make_hash(self, pw, salt=None):
        # Unless None, salt is expected to by a python str type of only ascii hex characters
        # Otherwise, a binascii.Error will be raised
        # pw is expected to be a utf8 compatible string

        if salt is None:
            salt = self.new_salt().decode('utf8')

        bin_pw = bytes(pw, 'utf8')
        bin_salt = binascii.a2b_hex(salt)

        dk = hashlib.pbkdf2_hmac('sha256', bin_pw, bin_salt, 100000)
        hex_hash = binascii.hexlify(dk).decode('utf8')

        return '%s:%s' % (salt, hex_hash)
        
    def new_salt(self, byte_len=16):
        return self.urandom_hex(byte_len)

    def urandom_hex(self, byte_len):
        rand = urandom(byte_len)
        return binascii.hexlify(rand)
