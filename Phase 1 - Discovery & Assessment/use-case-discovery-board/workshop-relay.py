#!/usr/bin/env python3
"""
Workshop relay for the Use Case Discovery Board.

Runs on the facilitator's own laptop so a room can edit one board together.
It does two things:

  1. Serves the toolkit's static files, so participants open the board from
     this laptop rather than the public site. That is not a convenience: a
     page served over https cannot talk to a plain-http relay on the local
     network, so the board and the relay have to share an origin.
  2. Relays board edits between the browsers in the room.

Everything stays on this machine and the local network. Nothing is written to
disk and nothing is sent to any third party — stop the process and the session
is gone. That is the whole point: it keeps the toolkit's "client data never
leaves the room" promise while still allowing several people to draw at once.

Standard library only. No dependencies, no build step.

    python3 workshop-relay.py                 # serve the repo, port 8000
    python3 workshop-relay.py --port 9000
    python3 workshop-relay.py --session acme  # name the session

Then share the printed LAN address with the room.
"""

import argparse
import json
import os
import secrets
import socket
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# How long a poll waits for something to happen before answering empty. Long
# enough that idle clients are not hammering the relay, short enough that a
# closed laptop is noticed quickly.
POLL_TIMEOUT = 25.0
# A peer that has not polled in this long is dropped from the roster.
PEER_TTL = 45.0
# Ops kept for late/slow clients. Past this a client is told to resync from
# the full document instead of replaying history.
OPS_KEPT = 2000
# Colours handed to peers in order, so each person is identifiable on screen.
PEER_COLOURS = ["#1B1474", "#c0392b", "#1a8a5c", "#d4790e", "#5348c4",
                "#0e7c86", "#a3195b", "#5b6b1f"]

def blank_doc():
    return {"fields": {}, "nodes": [], "layout": {}, "edges": []}


class Session:
    """One board, shared by everyone who joined the same session name."""

    def __init__(self, name):
        self.name = name
        self.cond = threading.Condition()
        self.doc = blank_doc()
        self.seeded = False          # True once a first client has uploaded a board
        self.seq = 0
        self.ops = []                # [{seq, peer, op}]
        self.peers = {}              # peerId -> {name, colour, slot, seen}
        self.next_slot = 1

    # ── peers ────────────────────────────────────────────────────
    def join(self, display_name):
        with self.cond:
            peer_id = secrets.token_hex(6)
            slot = self.next_slot
            self.next_slot += 1
            self.peers[peer_id] = {
                "name": display_name or f"Guest {slot}",
                "colour": PEER_COLOURS[(slot - 1) % len(PEER_COLOURS)],
                "slot": slot,
                "seen": time.time(),
            }
            self.cond.notify_all()
            # Each peer mints node ids from its own range, so two people adding
            # a block at the same moment can never collide on an id.
            return peer_id, slot * 1_000_000

    def leave(self, peer_id):
        with self.cond:
            self.peers.pop(peer_id, None)
            self.cond.notify_all()

    def touch(self, peer_id):
        with self.cond:
            if peer_id in self.peers:
                self.peers[peer_id]["seen"] = time.time()

    def roster(self):
        now = time.time()
        stale = [p for p, v in self.peers.items() if now - v["seen"] > PEER_TTL]
        for p in stale:
            self.peers.pop(p, None)
        return [{"id": p, "name": v["name"], "colour": v["colour"]}
                for p, v in sorted(self.peers.items(), key=lambda kv: kv[1]["slot"])]

    # ── document ─────────────────────────────────────────────────
    def apply(self, op):
        """Fold one op into the authoritative document."""
        doc, t = self.doc, op.get("t")
        if t == "doc":
            incoming = op.get("doc") or {}
            self.doc = {
                "fields": incoming.get("fields", {}),
                "nodes": incoming.get("nodes", []),
                "layout": incoming.get("layout", {}),
                "edges": incoming.get("edges", []),
            }
            self.seeded = True
        elif t == "node":
            node, lay = op.get("node"), op.get("layout")
            if not node:
                return
            for i, existing in enumerate(doc["nodes"]):
                if existing.get("id") == node.get("id"):
                    doc["nodes"][i] = node       # replace in place, keep z-order
                    break
            else:
                doc["nodes"].append(node)
            if lay:
                doc["layout"][str(node.get("id"))] = lay
        elif t == "nodeDel":
            nid = op.get("id")
            doc["nodes"] = [n for n in doc["nodes"] if n.get("id") != nid]
            doc["layout"].pop(str(nid), None)
            doc["edges"] = [e for e in doc["edges"]
                            if e.get("from") != nid and e.get("to") != nid]
        elif t == "edge":
            edge = op.get("edge")
            if not edge:
                return
            for i, existing in enumerate(doc["edges"]):
                if existing.get("id") == edge.get("id"):
                    doc["edges"][i] = edge
                    break
            else:
                doc["edges"].append(edge)
        elif t == "edgeDel":
            doc["edges"] = [e for e in doc["edges"] if e.get("id") != op.get("id")]
        elif t == "field":
            doc["fields"][op.get("k")] = op.get("v")

    def push(self, peer_id, ops):
        with self.cond:
            for op in ops:
                self.apply(op)
                self.seq += 1
                self.ops.append({"seq": self.seq, "peer": peer_id, "op": op})
            if len(self.ops) > OPS_KEPT:
                self.ops = self.ops[-OPS_KEPT:]
            self.cond.notify_all()
            return self.seq

    def since(self, seq):
        """Ops after seq, or None when the caller has fallen too far behind."""
        if not self.ops:
            return []
        if seq < self.ops[0]["seq"] - 1:
            return None
        return [o for o in self.ops if o["seq"] > seq]


SESSIONS = {}
SESSIONS_LOCK = threading.Lock()


def get_session(name):
    with SESSIONS_LOCK:
        if name not in SESSIONS:
            SESSIONS[name] = Session(name)
        return SESSIONS[name]


class Handler(SimpleHTTPRequestHandler):
    # Quieter than the default: one line per sync call would drown the console.
    def log_message(self, fmt, *args):
        path = getattr(self, "path", "")
        if path.startswith("/sync/"):
            return
        super().log_message(fmt, *args)

    def handle_one_request(self):
        # Someone closing their laptop mid-poll drops the socket. That is
        # normal in a room full of people, so it must not print a traceback
        # and make a healthy relay look like it is crashing.
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # The board is normally served by this very process, so this is
        # belt-and-braces for anyone testing from another local origin.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        try:
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def _body(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, TypeError):
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/sync/poll":
            return self.handle_poll(parse_qs(parsed.query))
        if parsed.path == "/sync/state":
            q = parse_qs(parsed.query)
            s = get_session((q.get("session") or ["default"])[0])
            with s.cond:
                return self._send_json({"seq": s.seq, "doc": s.doc,
                                        "seeded": s.seeded, "peers": s.roster()})
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/sync/join":
            return self.handle_join()
        if parsed.path == "/sync/ops":
            return self.handle_ops()
        if parsed.path == "/sync/leave":
            body = self._body()
            get_session(body.get("session", "default")).leave(body.get("peerId", ""))
            return self._send_json({"ok": True})
        self.send_error(404, "Not a relay endpoint")

    def handle_join(self):
        body = self._body()
        s = get_session(body.get("session", "default"))
        peer_id, id_base = s.join(body.get("name", ""))
        seed = body.get("doc")
        with s.cond:
            # Whether this peer is adopting an existing board or seeding a new
            # one decides, on the client, if it must warn before replacing
            # whatever the person had open.
            adopted = s.seeded
            # The first person in seeds the session with whatever is on their
            # board; everyone after that adopts what is already there.
            if not s.seeded and seed:
                s.apply({"t": "doc", "doc": seed})
                s.seq += 1
                s.ops.append({"seq": s.seq, "peer": peer_id, "op": {"t": "doc", "doc": s.doc}})
            payload = {"peerId": peer_id, "idBase": id_base, "seq": s.seq,
                       "doc": s.doc, "seeded": s.seeded, "adopted": adopted,
                       "peers": s.roster(), "session": s.name}
            s.cond.notify_all()
        return self._send_json(payload)

    def handle_ops(self):
        body = self._body()
        s = get_session(body.get("session", "default"))
        peer_id = body.get("peerId", "")
        s.touch(peer_id)
        seq = s.push(peer_id, body.get("ops") or [])
        return self._send_json({"seq": seq})

    def handle_poll(self, q):
        s = get_session((q.get("session") or ["default"])[0])
        peer_id = (q.get("peerId") or [""])[0]
        try:
            since = int((q.get("since") or ["0"])[0])
        except ValueError:
            since = 0
        s.touch(peer_id)
        deadline = time.time() + POLL_TIMEOUT
        with s.cond:
            # Someone arriving or leaving is news too, not just an edit —
            # without this the roster would only refresh when the long poll
            # timed out, so a person joining took up to POLL_TIMEOUT to appear.
            started_with = [p["id"] for p in s.roster()]
            while True:
                ops = s.since(since)
                if ops is None:                       # fell behind: full resync
                    return self._send_json({"resync": True, "seq": s.seq,
                                            "doc": s.doc, "peers": s.roster()})
                fresh = [o for o in ops if o["peer"] != peer_id]
                roster = s.roster()
                if fresh or [p["id"] for p in roster] != started_with or time.time() >= deadline:
                    return self._send_json({"seq": s.seq, "ops": fresh, "peers": roster})
                s.cond.wait(min(1.0, max(0.05, deadline - time.time())))


def lan_ip():
    """Best-effort LAN address to read out to the room."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))      # never actually sends anything
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))
    ap = argparse.ArgumentParser(description="Workshop relay for the Use Case Discovery Board")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--session", default="default", help="session name (default: 'default')")
    ap.add_argument("--root", default=repo_root, help="directory to serve (default: the repo root)")
    args = ap.parse_args()

    handler = lambda *a, **kw: Handler(*a, directory=args.root, **kw)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    httpd.daemon_threads = True

    board = ("/Phase%201%20-%20Discovery%20%26%20Assessment/"
             "use-case-discovery-board/?session=" + args.session)
    print("\n  Use Case Discovery Board — workshop relay")
    print("  " + "-" * 46)
    print(f"  Serving:  {args.root}")
    print(f"  Session:  {args.session}")
    print("\n  Open on this laptop:")
    print(f"    http://localhost:{args.port}{board}")
    print("\n  Share with the room (same wifi):")
    print(f"    http://{lan_ip()}:{args.port}{board}")
    print("\n  Nothing is written to disk. Stop with Ctrl-C and the session is gone.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Session ended. Nothing was saved.\n")


if __name__ == "__main__":
    main()
