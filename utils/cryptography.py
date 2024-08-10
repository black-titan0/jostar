from cryptography.fernet import Fernet

from Jostar import settings


class EncryptionUtils:
    SECRET_KEY = settings.CRYPTOGRAPHY_SECRET_KEY
    cipher_suite = Fernet(SECRET_KEY)

    @staticmethod
    def encrypt_info(info: str) -> str:
        return EncryptionUtils.cipher_suite.encrypt(info.encode()).decode()

    @staticmethod
    def decrypt_info(encrypted_info: str) -> str:
        return EncryptionUtils.cipher_suite.decrypt(encrypted_info.encode()).decode()
