#!/usr/bin/env python3
"""Resumable work ledger for multi-agent programmes (stdlib only, Python 3.9+).

The ledger is a JSON file next to the programme documents. It records which work
package is todo, claimed, done, blocked or dormant, who holds a lease, what was
checkpointed, the evidence for completion and a hash manifest of the files the
package owns. Every mutation takes a file lock and replaces the ledger
atomically, so several agents can work in parallel and a successor can resume
exactly where a predecessor stopped.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = WORKSPACE_ROOT / "core" / "Brain" / "computer-use-program" / "ledger.json"
DEFAULT_WORK_PACKAGES = DEFAULT_LEDGER.parent / "WORK-PACKAGES.md"

STATUSES = ("todo", "claimed", "done", "blocked", "dormant")
IGNORED_DIRS = frozenset({"node_modules", "lib", ".build", "dist", "out", "__pycache__", ".git"})
MAX_MANIFEST_FILES = 2000
MIN_EVIDENCE_CHARS = 20
LOCK_STALE_SECONDS = 30
LOCK_ATTEMPTS = 200
LOCK_SLEEP_SECONDS = 0.05

Data = Dict[str, Any]


class LedgerError(Exception):
    """Expected, user-correctable ledger failure."""


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


# --------------------------------------------------------------------------- persistence


@contextlib.contextmanager
def file_lock(path: Path) -> Iterator[None]:
    """Cross-process exclusive lock using O_EXCL; a lock older than LOCK_STALE_SECONDS is broken."""
    lock_path = path.with_name(path.name + ".lock")
    for _ in range(LOCK_ATTEMPTS):
        try:
            descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                if time.time() - lock_path.stat().st_mtime > LOCK_STALE_SECONDS:
                    lock_path.unlink()
                    continue
            except FileNotFoundError:
                continue
            time.sleep(LOCK_SLEEP_SECONDS)
            continue
        os.write(descriptor, str(os.getpid()).encode("ascii"))
        os.close(descriptor)
        break
    else:
        raise LedgerError(f"could not lock {path}; remove {lock_path} only if no agent is writing")
    try:
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock_path.unlink()


def read_ledger(path: Path) -> Data:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise LedgerError(f"ledger not found: {path}") from error
    except json.JSONDecodeError as error:
        raise LedgerError(f"ledger is not valid JSON ({error}); restore it from version control") from error
    if data.get("schema") != 1 or not isinstance(data.get("packages"), dict):
        raise LedgerError("unsupported ledger schema")
    return data


def write_ledger(path: Path, data: Data) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(str(temporary), str(path))


def mutate(path: Path, change: Callable[[Data], Any]) -> Any:
    """Apply `change` to the ledger under the lock; the file is written only if `change` returns."""
    with file_lock(path):
        data = read_ledger(path)
        result = change(data)
        write_ledger(path, data)
        return result


# --------------------------------------------------------------------------- queries


def package(data: Data, wp_id: str) -> Data:
    try:
        return data["packages"][wp_id]
    except KeyError as error:
        raise LedgerError(f"unknown work package {wp_id}") from error


def lease_expired(wp: Data, now: datetime, lease_minutes: int) -> bool:
    beat = wp.get("heartbeat_at")
    return beat is None or now - parse_iso(beat) > timedelta(minutes=lease_minutes)


def live_claim(wp: Data, now: datetime, lease_minutes: int) -> bool:
    return wp["status"] == "claimed" and not lease_expired(wp, now, lease_minutes)


def dependencies_done(data: Data, wp: Data) -> bool:
    return all(data["packages"][dep]["status"] == "done" for dep in wp["depends_on"])


def _normal(prefix: str) -> str:
    return prefix.rstrip("/") + "/"


def paths_overlap(first: Sequence[str], second: Sequence[str]) -> bool:
    for left in first:
        for right in second:
            a, b = _normal(left), _normal(right)
            if a.startswith(b) or b.startswith(a):
                return True
    return False


def path_conflicts(data: Data, wp_id: str, now: datetime) -> List[str]:
    """Ids of other live-claimed packages whose owned paths overlap this package's."""
    mine = package(data, wp_id)["owns"]
    lease = data["lease_minutes"]
    return [
        other_id
        for other_id, other in data["packages"].items()
        if other_id != wp_id and live_claim(other, now, lease) and paths_overlap(mine, other["owns"])
    ]


def claim_state(data: Data, wp_id: str, now: datetime) -> str:
    """One of: claimable, takeover, claimed, done, blocked, dormant, waiting-deps, path-conflict."""
    wp = package(data, wp_id)
    status = wp["status"]
    if status in ("done", "blocked", "dormant"):
        return status
    if not dependencies_done(data, wp):
        return "waiting-deps"
    if status == "claimed":
        return "claimed" if live_claim(wp, now, data["lease_minutes"]) else "takeover"
    return "path-conflict" if path_conflicts(data, wp_id, now) else "claimable"


def next_candidates(data: Data, now: datetime) -> List[str]:
    states = {wp_id: claim_state(data, wp_id, now) for wp_id in data["packages"]}
    wanted = [wp_id for wp_id, state in states.items() if state in ("takeover", "claimable")]
    wanted.sort(key=lambda wp_id: (data["packages"][wp_id].get("optional", False), states[wp_id] != "takeover", wp_id))
    return wanted


# --------------------------------------------------------------------------- manifests


def manifest(owns: Sequence[str], root: Path) -> Dict[str, str]:
    """sha256 of every file under the owned paths, relative to `root`; bounded and deterministic."""
    result: Dict[str, str] = {}
    for owned in owns:
        base = root / owned
        files = [base] if base.is_file() else sorted(base.rglob("*")) if base.is_dir() else []
        for file in files:
            if not file.is_file() or IGNORED_DIRS.intersection(file.relative_to(root).parts):
                continue
            if len(result) >= MAX_MANIFEST_FILES:
                raise LedgerError(f"owned paths exceed {MAX_MANIFEST_FILES} files; narrow `owns`")
            result[file.relative_to(root).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    return result


def manifest_drift(recorded: Dict[str, str], current: Dict[str, str]) -> Dict[str, List[str]]:
    return {
        "missing": sorted(set(recorded) - set(current)),
        "changed": sorted(name for name in recorded if name in current and recorded[name] != current[name]),
        "added": sorted(set(current) - set(recorded)),
    }


# --------------------------------------------------------------------------- commands (pure on data)


def log(data: Data, now: datetime, agent: str, wp_id: str, event: str, note: str = "") -> None:
    data.setdefault("log", []).append({"at": iso(now), "agent": agent, "wp": wp_id, "event": event, "note": note})


def do_claim(data: Data, wp_id: str, agent: str, now: datetime, takeover: bool = False) -> str:
    state = claim_state(data, wp_id, now)
    if state == "takeover" and not takeover:
        raise LedgerError(f"{wp_id} has an expired lease; inspect its checkpoints and files, then use takeover")
    if state not in ("claimable", "takeover"):
        raise LedgerError(f"{wp_id} cannot be claimed: {state}")
    wp = package(data, wp_id)
    previous = wp.get("claimed_by")
    wp.update(status="claimed", claimed_by=agent, claimed_at=iso(now), heartbeat_at=iso(now))
    log(data, now, agent, wp_id, "takeover" if state == "takeover" else "claim", f"previous={previous}" if previous else "")
    return state


def do_heartbeat(data: Data, wp_id: str, agent: str, now: datetime) -> None:
    wp = package(data, wp_id)
    if wp["status"] != "claimed" or wp.get("claimed_by") != agent:
        raise LedgerError(f"{wp_id} is not claimed by {agent}")
    wp["heartbeat_at"] = iso(now)


def do_checkpoint(data: Data, wp_id: str, agent: str, note: str, now: datetime) -> None:
    do_heartbeat(data, wp_id, agent, now)
    if len(note.strip()) < 10:
        raise LedgerError("checkpoint note must say what is done, what is next and which files changed")
    package(data, wp_id).setdefault("checkpoints", []).append({"at": iso(now), "agent": agent, "note": note})
    log(data, now, agent, wp_id, "checkpoint", note[:120])


def do_done(data: Data, wp_id: str, agent: str, evidence: Sequence[str], now: datetime, root: Path) -> int:
    do_heartbeat(data, wp_id, agent, now)
    if not evidence or any(len(item.strip()) < MIN_EVIDENCE_CHARS for item in evidence):
        raise LedgerError(f"each --evidence needs a command and its real result (>= {MIN_EVIDENCE_CHARS} chars)")
    wp = package(data, wp_id)
    files = manifest(wp["owns"], root)
    wp.update(status="done", done_at=iso(now), done_by=agent, evidence=list(evidence), manifest=files)
    log(data, now, agent, wp_id, "done", f"{len(files)} files hashed")
    return len(files)


def do_rebaseline(data: Data, wp_id: str, agent: str, reason: str, now: datetime, root: Path) -> int:
    """Re-hash a done package after a follow-up package legitimately changed its files."""
    wp = package(data, wp_id)
    if wp["status"] != "done":
        raise LedgerError(f"{wp_id} is not done")
    if len(reason.strip()) < 10:
        raise LedgerError("rebaseline reason must name the follow-up package that changed the files")
    files = manifest(wp["owns"], root)
    drift = manifest_drift(wp["manifest"], files)
    wp["manifest"] = files
    wp.setdefault("rebaselines", []).append({"at": iso(now), "agent": agent, "reason": reason, "drift": drift})
    log(data, now, agent, wp_id, "rebaseline", reason[:120])
    return len(files)


def do_add_package(data: Data, wp_id: str, spec: Data, agent: str, now: datetime) -> None:
    """Add a follow-up package (for example a fix found in review) in the todo state."""
    if wp_id in data["packages"]:
        raise LedgerError(f"{wp_id} already exists")
    missing = [key for key in ("title", "lane", "role", "depends_on", "owns") if key not in spec]
    if missing:
        raise LedgerError(f"package spec lacks {', '.join(missing)}")
    entry = {"status": "todo", "claimed_by": None, "claimed_at": None, "heartbeat_at": None, "checkpoints": [], "evidence": []}
    entry.update(spec)
    data["packages"][wp_id] = entry
    log(data, now, agent, wp_id, "add", spec["title"])


def do_block(data: Data, wp_id: str, agent: str, reason: str, now: datetime) -> None:
    do_heartbeat(data, wp_id, agent, now)
    if len(reason.strip()) < 10:
        raise LedgerError("block reason must contain the evidence (command and output)")
    wp = package(data, wp_id)
    wp.update(status="blocked", blocked_reason=reason)
    log(data, now, agent, wp_id, "block", reason[:120])


def do_unblock(data: Data, wp_id: str, agent: str, note: str, now: datetime) -> None:
    wp = package(data, wp_id)
    if wp["status"] != "blocked":
        raise LedgerError(f"{wp_id} is not blocked")
    wp.update(status="todo", claimed_by=None, heartbeat_at=None)
    wp.pop("blocked_reason", None)
    log(data, now, agent, wp_id, "unblock", note)


def do_activate(data: Data, wp_id: str, agent: str, reason: str, now: datetime) -> None:
    wp = package(data, wp_id)
    if wp["status"] != "dormant":
        raise LedgerError(f"{wp_id} is not dormant")
    if len(reason.strip()) < 10:
        raise LedgerError("activation reason must cite the decision record that triggers it")
    wp["status"] = "todo"
    log(data, now, agent, wp_id, "activate", reason)


def validate(data: Data, work_packages_text: Optional[str] = None) -> List[str]:
    """Structural problems of the ledger (and its match with WORK-PACKAGES.md when given)."""
    problems: List[str] = []
    packages = data["packages"]
    for wp_id, wp in packages.items():
        if wp["status"] not in STATUSES:
            problems.append(f"{wp_id}: invalid status {wp['status']}")
        if not wp.get("owns"):
            problems.append(f"{wp_id}: owns is empty")
        for dep in wp["depends_on"]:
            if dep not in packages:
                problems.append(f"{wp_id}: unknown dependency {dep}")
        if wp["status"] == "done" and not wp.get("evidence"):
            problems.append(f"{wp_id}: done without evidence")
    visiting: Dict[str, int] = {}

    def visit(node: str) -> None:
        if visiting.get(node) == 1:
            problems.append(f"{node}: dependency cycle")
            return
        if visiting.get(node) == 2:
            return
        visiting[node] = 1
        for dep in packages[node]["depends_on"]:
            if dep in packages:
                visit(dep)
        visiting[node] = 2

    for wp_id in packages:
        visit(wp_id)
    if work_packages_text is not None:
        for wp_id in packages:
            if f"### {wp_id} " not in work_packages_text:
                problems.append(f"{wp_id}: no '### {wp_id} ' section in WORK-PACKAGES.md")
    return problems


# --------------------------------------------------------------------------- CLI


def render_status(data: Data, now: datetime) -> str:
    rows = [f"{'WP':7} {'STATE':14} {'LANE':12} {'FLAGS':12} TITLE"]
    for wp_id, wp in data["packages"].items():
        flags = ",".join(label for label, key in (("hw", "hw_gated"), ("optional", "optional")) if wp.get(key))
        rows.append(f"{wp_id:7} {claim_state(data, wp_id, now):14} {wp['lane']:12} {flags:12} {wp['title']}")
    totals = {state: sum(1 for p in data["packages"].values() if p["status"] == state) for state in STATUSES}
    rows.append("totals: " + ", ".join(f"{state}={count}" for state, count in totals.items()))
    return "\n".join(rows)


def render_show(data: Data, wp_id: str) -> str:
    wp = package(data, wp_id)
    return json.dumps({wp_id: wp}, indent=2, ensure_ascii=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--root", type=Path, default=WORKSPACE_ROOT, help="workspace root for manifest hashing")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "next", "check"):
        commands.add_parser(name)
    for name in ("show", "verify"):
        commands.add_parser(name).add_argument("wp")
    for name in ("claim", "takeover", "heartbeat"):
        sub = commands.add_parser(name)
        sub.add_argument("wp")
        sub.add_argument("--agent", required=True)
    sub = commands.add_parser("checkpoint")
    sub.add_argument("wp")
    sub.add_argument("--agent", required=True)
    sub.add_argument("--note", required=True)
    sub = commands.add_parser("done")
    sub.add_argument("wp")
    sub.add_argument("--agent", required=True)
    sub.add_argument("--evidence", action="append", default=[])
    for name in ("block", "unblock", "activate", "rebaseline"):
        sub = commands.add_parser(name)
        sub.add_argument("wp")
        sub.add_argument("--agent", required=True)
        sub.add_argument("--reason", required=True)
    return parser


def run(arguments: argparse.Namespace) -> int:
    ledger, now = arguments.ledger, utcnow()
    command = arguments.command
    if command in ("status", "next", "show", "verify", "check"):
        data = read_ledger(ledger)
        if command == "status":
            print(render_status(data, now))
        elif command == "next":
            candidates = next_candidates(data, now)
            for wp_id in candidates:
                wp = data["packages"][wp_id]
                print(f"{wp_id}  {claim_state(data, wp_id, now):10} {wp['title']}")
            if not candidates:
                print("nothing claimable: everything is done, blocked, dormant, claimed or waiting on dependencies")
        elif command == "show":
            print(render_show(data, arguments.wp))
        elif command == "verify":
            wp = package(data, arguments.wp)
            if wp["status"] != "done":
                raise LedgerError(f"{arguments.wp} is not done")
            drift = manifest_drift(wp["manifest"], manifest(wp["owns"], arguments.root))
            print(json.dumps(drift, indent=2))
            return 1 if drift["missing"] or drift["changed"] else 0
        else:
            text = DEFAULT_WORK_PACKAGES.read_text(encoding="utf-8") if DEFAULT_WORK_PACKAGES.exists() else None
            problems = validate(data, text)
            print("\n".join(problems) if problems else "ledger ok")
            return 1 if problems else 0
        return 0

    def apply(data: Data) -> str:
        if command in ("claim", "takeover"):
            return f"{arguments.wp}: {do_claim(data, arguments.wp, arguments.agent, now, takeover=command == 'takeover')}"
        if command == "heartbeat":
            do_heartbeat(data, arguments.wp, arguments.agent, now)
            return f"{arguments.wp}: heartbeat"
        if command == "checkpoint":
            do_checkpoint(data, arguments.wp, arguments.agent, arguments.note, now)
            return f"{arguments.wp}: checkpoint saved"
        if command == "done":
            count = do_done(data, arguments.wp, arguments.agent, arguments.evidence, now, arguments.root)
            return f"{arguments.wp}: done ({count} files hashed)"
        if command == "block":
            do_block(data, arguments.wp, arguments.agent, arguments.reason, now)
            return f"{arguments.wp}: blocked"
        if command == "unblock":
            do_unblock(data, arguments.wp, arguments.agent, arguments.reason, now)
            return f"{arguments.wp}: unblocked"
        if command == "rebaseline":
            count = do_rebaseline(data, arguments.wp, arguments.agent, arguments.reason, now, arguments.root)
            return f"{arguments.wp}: rebaselined ({count} files hashed)"
        do_activate(data, arguments.wp, arguments.agent, arguments.reason, now)
        return f"{arguments.wp}: activated"

    print(mutate(ledger, apply))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        return run(build_parser().parse_args(argv))
    except LedgerError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
