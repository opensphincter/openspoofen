#!/usr/bin/env python
"""Paramiko SSH helper for OpenSpoofen development."""
from __future__ import annotations

import argparse
import os
import sys

import paramiko


def _read_creds():
    """Credentials come from the environment: infisical run --path /openspoofen -- python scripts/pi-ssh.py ..."""
    return dict(os.environ)


def connect(hostname, username=None, password=None, timeout=10):
    creds = _read_creds()
    user = username or creds.get("PI_BOOTSTRAP_USERNAME")
    pw = password or creds.get("PI_BOOTSTRAP_PASSWORD")
    if not user or not pw:
        raise ValueError("No credentials. Set PI_BOOTSTRAP_USERNAME and PI_BOOTSTRAP_PASSWORD (Infisical Personal:/openspoofen; run under `infisical run --path /openspoofen --`)")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=user, password=pw, timeout=timeout, auth_timeout=timeout, banner_timeout=timeout)
    return client


def run(client, command, timeout=10):
    _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    out = stdout.read().decode(errors="replace").strip()
    err = stderr.read().decode(errors="replace").strip()
    return out, err


def main():
    parser = argparse.ArgumentParser(description="SSH into the OpenSpoofen Pi.")
    parser.add_argument("host", help="Pi hostname or IP")
    parser.add_argument("command", nargs="?", help="Command to run (default: interactive)")
    parser.add_argument("-u", "--user", help="SSH username")
    parser.add_argument("-p", "--password", help="SSH password")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Connection timeout")
    args = parser.parse_args()

    try:
        client = connect(args.host, args.user, args.password, args.timeout)
    except Exception as exc:  # noqa: BLE001 - top-level CLI guard reports any connect failure uniformly
        print(f"Connection failed: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command:
            out, err = run(client, args.command, args.timeout)
            if out:
                print(out)
            if err:
                print(f"[stderr] {err}", file=sys.stderr)
        else:
            print(f"Connected to {args.host}")
            print(f"  hostname: {run(client, 'hostname')[0]}")
            print(f"  uptime:   {run(client, 'uptime -p')[0]}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
