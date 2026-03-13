import ipaddress


def is_ip_allowed(client_ip, allowed_network):
    """
    Checks if the client IP belongs to the allowed subnet.
    """

    # Allow local testing
    if client_ip in ["127.0.0.1", "::1"]:
        return True

    try:
        network = ipaddress.ip_network(allowed_network)
        ip = ipaddress.ip_address(client_ip)

        return ip in network

    except ValueError:
        return False