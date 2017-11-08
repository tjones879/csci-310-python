from multipong.sockets import validate_username


def test_validate_username():
    shouldPass = ['asd', '123', '1a2b', 'asd 123']
    for option in shouldPass:
        assert(validate_username(option) == option)
    shouldNotPass = ['{', 'aaaaaaaaaaaaaaaaaaaaaaaaaa', '[', '=', '+']
    for option in shouldNotPass:
        assert(validate_username(option) != option)
