# _net.py — LAN address helper shared by server.py and ip.py.
#
# The usual UDP-connect trick is refused with EPERM on Raspberry Pi OS here,
# so this reads the address off the default-route interface instead.

import socket


def _iface_ip(name):
    """IPv4 address of one interface, via SIOCGIFADDR."""
    try:
        import fcntl
        import struct
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except OSError:
        return None
    try:
        packed = fcntl.ioctl(sock.fileno(), 0x8915,
                             struct.pack("256s", name[:15].encode()))
        return socket.inet_ntoa(packed[20:24])
    except OSError:
        return None
    finally:
        sock.close()


def _default_iface():
    try:
        with open("/proc/net/route") as fh:
            for line in fh.readlines()[1:]:
                fields = line.split()
                if len(fields) > 2 and fields[1] == "00000000":
                    return fields[0]
    except OSError:
        pass
    return None


def local_ip():
    """The LAN address other machines reach this Pi on, or None."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("10.255.255.255", 1))   # no packet is sent
        ip = sock.getsockname()[0]
        if ip and not ip.startswith("127."):
            return ip
    except OSError:
        pass
    finally:
        sock.close()

    candidates = []
    name = _default_iface()
    if name:
        candidates.append(name)
    try:
        candidates += [n for _, n in socket.if_nameindex()]
    except OSError:
        pass
    for name in candidates:
        ip = _iface_ip(name)
        if ip and not ip.startswith("127."):
            return ip

    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith("127."):
            return ip
    except OSError:
        pass
    return None
