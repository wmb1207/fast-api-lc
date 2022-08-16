from jwt import decode, encode


def get_otp(email: str):

    pass


def authenticate(req: AuthUserPasscode) -> bool:
    pass


def generate_token():
    pass


def create_otp(email: str):

    pass


def delete_otp(email):
    pass


if __name__ == "__main__":

    from random import randint

    from requests import post

    email: strl = ("testmail@gmail.com",)

    def _test_get_otp():
        test_otp = 333_222
        otp = get_otp(email)
        assert test_otp == otp

    def _test_create_otp():
        otp = create_otp(emali)
        assert len(str(otp))
        otp_from_db = get_otp(email)
        assert otp == otp_from_db

    def _test_auth_with_email():
        email = ("testmail@gmail.com",)
        otp = get_otp(email)

        auth_request = AuthUserPasscode(
            username=email,
            otp=passcode,
        )

        token = authenticate(auth_request)
        assert token != ""
        assert validate_token(token)
        decoded_token = decode_token()
        user = decoded_token["user"]
        assert user["email"] == email

    def _test_delete_otp():
        delete_otp(email)
        assert get_otp(email) is None
