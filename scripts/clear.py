# clear.py — blanks the attached board and exits.
#
# Usage: clear.py [microdot|unicorn] ...   (no argument: try both)
#
# The microdot path writes the zero frame straight to the I2C chips. Importing
# microdotphat pulls in numpy, which costs about 4 s on a Pi Zero, and a clear
# should not wait for that. The library path stays as a fallback.

import sys

MICRODOT_ADDRS = (0x61, 0x62, 0x63)
CMD_MATRIX_1 = 0x01
CMD_MATRIX_2 = 0x0E
CMD_UPDATE = 0x0C
ZERO_FRAME = [0] * 8


def clear_microdot():
    try:
        from smbus2 import SMBus
    except ImportError:
        import microdotphat
        microdotphat.fill(0)
        microdotphat.show()
        print("clear.py: microdot-phat cleared (library)")
        return
    bus = SMBus(1)
    try:
        for addr in MICRODOT_ADDRS:
            bus.write_i2c_block_data(addr, CMD_MATRIX_1, ZERO_FRAME)
            bus.write_i2c_block_data(addr, CMD_MATRIX_2, ZERO_FRAME)
            bus.write_byte_data(addr, CMD_UPDATE, 0x01)
    finally:
        bus.close()
    print("clear.py: microdot-phat cleared")


def clear_unicorn():
    import unicornhat
    unicornhat.clear()
    unicornhat.show()
    print("clear.py: unicorn-hat cleared")


def main():
    targets = sys.argv[1:] or ["microdot", "unicorn"]
    for target in targets:
        try:
            if target == "microdot":
                clear_microdot()
            elif target == "unicorn":
                clear_unicorn()
            else:
                print("clear.py: unknown target", target)
        except Exception as exc:
            print("clear.py: no %s: %s" % (target, exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
