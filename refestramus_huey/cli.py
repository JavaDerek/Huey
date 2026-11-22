"""Offline comparison, inspection, synthetic planting and localhost replay."""
from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

from .compare import compare_snapshots
from .files import FileError, Snapshot, load_capture, load_snapshot, plant
from .replayer import Replayer
from .safety import Refused

WARNING = (
    "Real console files contain private information and should not be published. "
    "This build accepts synthetic fixtures only; actual firmware 3.1.2 compatibility is unverified."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Read a supported synthetic file")
    inspect.add_argument("file", type=Path)
    inspect.add_argument("--pointer")
    compare = sub.add_parser("compare", help="Compare two supported synthetic snapshots")
    compare.add_argument("before", type=Path)
    compare.add_argument("after", type=Path)
    compare.add_argument("--ignore", action="append", default=[], metavar="POINTER")
    compare.add_argument("--ignore-pattern", action="append", default=[], metavar="GLOB")
    change = sub.add_parser("plant", help="Create a new synthetic file plus plant record")
    change.add_argument("file", type=Path)
    change.add_argument("pointer")
    change.add_argument("value", help="New scalar value as JSON")
    change.add_argument("output", type=Path)
    replay = sub.add_parser("replay", help="Serve a synthetic file on localhost")
    replay.add_argument("file", type=Path)
    replay.add_argument("--host", default="127.0.0.1", help="Must be numeric 127.0.0.1")
    replay.add_argument("--port", type=int, default=0)
    replay.add_argument("--discovery-port", type=int, default=0)
    replay.add_argument("--delay", type=float, default=0)
    replay.add_argument("--drop-rate", type=float, default=0)
    replay.add_argument("--late-every", type=int, default=0)
    replay.add_argument("--late-delay", type=float, default=0)
    replay.add_argument("--duration", type=float, help="Stop after this many seconds")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    try:
        if args.command == "inspect":
            file = (
                load_snapshot(args.file) if args.file.suffix == ".snap" else load_capture(args.file)
            )
            output = {
                "synthetic": file.synthetic,
                "identity": file.identity,
                "warning": WARNING,
                "assumed_compatibility": isinstance(file, Snapshot),
            }
            if args.pointer is not None:
                if not isinstance(file, Snapshot):
                    raise FileError("--pointer inspection currently accepts native snapshots")
                output["value"] = file.get(args.pointer)
            print(json.dumps(output, ensure_ascii=False))
        elif args.command == "compare":
            result = compare_snapshots(
                args.before, args.after, ignore=args.ignore, ignore_patterns=args.ignore_pattern
            )
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return result.exit_code
        elif args.command == "plant":
            path = plant(args.file, args.pointer, json.loads(args.value), args.output)
            print(json.dumps({"output": str(path), "synthetic": True, "warning": WARNING}))
        else:
            if args.duration is not None and (
                args.duration <= 0 or not args.duration < float("inf")
            ):
                raise ValueError("--duration must be finite and positive")
            with Replayer(
                args.file,
                host=args.host,
                port=args.port,
                discovery_port=args.discovery_port,
                delay=args.delay,
                drop_rate=args.drop_rate,
                late_every=args.late_every,
                late_delay=args.late_delay,
            ) as server:
                print(
                    json.dumps(
                        {
                            "osc": server.address,
                            "discovery": server.discovery_address,
                            "synthetic": True,
                            "warning": WARNING,
                        }
                    ),
                    flush=True,
                )
                deadline = time.monotonic() + args.duration if args.duration is not None else None
                while server.running and (deadline is None or time.monotonic() < deadline):
                    time.sleep(0.01)
        return 0
    except KeyboardInterrupt:
        return 0
    except Refused as exc:
        logging.error("Refused: %s", exc)
        return 5
    except (FileError, ValueError, OSError, RuntimeError) as exc:
        logging.error("Cannot complete operation: %s", exc)
        return 6


if __name__ == "__main__":
    raise SystemExit(main())
