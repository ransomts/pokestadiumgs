#!/usr/bin/env python3
"""Filter decomp-permuter output into a compact, timestamped log.

The permuter rewrites one status line ("iteration N, E errors, score = S") with \\r
thousands of times per second. This filter passes every other line through with a
timestamp and emits only one status snapshot per SNAP_SECS (default 300), with the
iteration rate since the previous snapshot.

usage: permuter.py ... 2>&1 | farm_logfilter.py [snap_secs] > func.log
"""
import re
import sys
import time

SNAP = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0
ANSI = re.compile(r"\x1b\[[0-9;]*m")
STATUS = re.compile(r"iteration (\d+), (\d+) errors")


def stamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


last_status = None
last_snap = time.time()
last_iter = 0
last_iter_time = last_snap
buf = b""
out = sys.stdout

while True:
    chunk = sys.stdin.buffer.read1(65536) if hasattr(sys.stdin.buffer, "read1") else sys.stdin.buffer.read(65536)
    if not chunk:
        break
    buf += chunk
    parts = re.split(rb"[\r\n]", buf)
    buf = parts.pop()  # incomplete tail
    for raw in parts:
        line = ANSI.sub("", raw.decode("utf-8", "replace")).strip()
        if not line:
            continue
        m = STATUS.search(line)
        if m:
            last_status = (int(m.group(1)), int(m.group(2)), line)
        else:
            out.write(f"{stamp()} {line}\n")
            out.flush()
    now = time.time()
    if last_status and now - last_snap >= SNAP:
        it, err, line = last_status
        rate = (it - last_iter) / max(now - last_iter_time, 1e-6)
        out.write(f"{stamp()} STATUS {line} ({rate:.1f} it/s)\n")
        out.flush()
        last_snap, last_iter, last_iter_time = now, it, now

if last_status:
    it, err, line = last_status
    out.write(f"{stamp()} STATUS {line} (final)\n")
out.write(f"{stamp()} permuter exited\n")
out.flush()
