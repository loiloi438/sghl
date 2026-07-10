import pyotp


def generate_secret() -> str:
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(str(code).strip(), valid_window=1)


def provisioning_uri(*, username: str, secret: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name='SGHL')
