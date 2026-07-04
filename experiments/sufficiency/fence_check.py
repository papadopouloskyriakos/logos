#!/usr/bin/env python3
"""Argv-exact fence check — immune to self-detection (matches only python3 <...>/resume_sweep.py
--run|--cell, i.e. the script as argv[1], never a -c source string). Prints BREACH lines or nothing."""
import os, subprocess
PROT = set(range(14)) | {15, 16}
for pid in os.listdir('/proc'):
    if not pid.isdigit():
        continue
    try:
        argv = [a for a in open(f'/proc/{pid}/cmdline', 'rb').read().split(b'\x00') if a]
    except Exception:
        continue
    if len(argv) < 3 or not argv[0].endswith(b'python3') or not argv[1].endswith(b'resume_sweep.py'):
        continue
    if argv[2] not in (b'--run', b'--cell'):
        continue
    try:
        psr = int(subprocess.check_output(['ps', '-o', 'psr=', '-p', pid]).strip())
    except Exception:
        continue
    if psr in PROT:
        print(f'{pid} {psr}')
