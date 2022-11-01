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
        if port > 0 and port < 65536:
            return True
        else:
            return False
    except ValueError:
        return False