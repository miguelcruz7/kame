#!/usr/bin/env python3
"""Unlock the Kame Air780EG SIM once, without logging the PIN."""

import fcntl
import os
from pathlib import Path
import select
import sys
import termios
import time
import tty


PORT = Path('/dev/serial/by-id/usb-EigenComm_EigenComm_Compo_000000000001-if02')
PIN_FILE = Path('/etc/kame/air780eg-pin')
REJECTED = Path('/var/lib/kame-air780eg/pin-attempt-pending')
LOCK = Path('/run/lock/kame-air780eg.lock')


def exchange(fd, command, timeout=5):
    while select.select([fd], [], [], 0)[0]:
        try:
            os.read(fd, 4096)
        except BlockingIOError:
            break
    os.write(fd, command + b'\r')
    data = bytearray()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if select.select([fd], [], [], max(0, min(0.3, deadline - time.monotonic())))[0]:
            try:
                data.extend(os.read(fd, 4096))
            except BlockingIOError:
                continue
            if b'\r\nOK\r\n' in data or b'\r\nERROR\r\n' in data:
                break
    return bytes(data)


def main():
    if not PORT.exists():
        print('Air780EG AT port absent; nothing to do')
        return 0
    with LOCK.open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            exchange(fd, b'ATE0')
            reply = exchange(fd, b'AT+CPIN?')
            if b'+CPIN: READY' in reply:
                REJECTED.unlink(missing_ok=True)
                print('Air780EG SIM ready')
                return 0
            if b'+CPIN: SIM PIN' not in reply:
                print('Air780EG SIM state unclear; no PIN sent')
                return 1
            if REJECTED.exists():
                print('Prior PIN attempt unresolved; refusing to retry')
                return 2
            pin = PIN_FILE.read_text(encoding='ascii').strip()
            if not pin.isdecimal() or not 4 <= len(pin) <= 8:
                print('Invalid PIN file; no PIN sent')
                return 2
            REJECTED.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            REJECTED.write_text('PIN attempt started; verify before removing this marker.\n')
            os.chmod(REJECTED, 0o600)
            exchange(fd, b'AT+CPIN="' + pin.encode('ascii') + b'"', timeout=12)
            time.sleep(2)
            reply = exchange(fd, b'AT+CPIN?', timeout=8)
            if b'+CPIN: READY' in reply:
                REJECTED.unlink()
                print('Air780EG SIM unlocked')
                return 0
            print('Air780EG PIN attempt did not confirm READY; refusing to retry')
            return 2
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, old_settings)
            os.close(fd)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f'Air780EG unlock error: {type(error).__name__}')
        sys.exit(1)
