# CONVERT TUPLE, STRING AND IP / PORT BACK AND FORTH
def convert_tuple_to_string(credentials_tuple):
    return str(credentials_tuple[0]) + ":" + str(credentials_tuple[1])


def convert_string_to_tuple(credentials_string):
    credentials = credentials_string.split(":")
    return credentials[0], int(credentials[1])


def get_port(credentials_string):
    return int(credentials_string.split(":")[1])


def get_ip(credentials_string):
    return credentials_string.split(":")[0]


# VALIDATING THE FORMAT OF THE CREDENTIALS


# checking if the credentials are valid
def is_credentials_format(credentials):
    credentials = credentials.split(":")
    if len(credentials) == 2:
        if is_ip_format(credentials[0]) and is_port_format(credentials[1]):
            return True
        else:
            return False
    else:
        return False


# checking if the format of the ip-address is valid
def is_ip_format(address):
    # IPv4
    if len(address.split(".")) == 4:
        parts = address.split(".")
        for part in parts:
            try:
                part = int(part)
                if part < 0 or part > 255:
                    return False
            except ValueError:
                return False
        return True

    # IPv6
    if len(address.split(":")) == 8:
        parts = address.split(":")
        for part in parts:
            try:
                part = int(part, 16)
                if part < 0 or part > 65535:
                    return False
            except ValueError:
                return False
        return True


# checking if the format of the port is valid
def is_port_format(port):
    try:
        port = int(port)
        if 0 < port < 65536:
            return True
        else:
            return False
    except ValueError:
        return False
