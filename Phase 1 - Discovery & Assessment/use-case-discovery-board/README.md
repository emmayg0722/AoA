# Use Case Discovery Board

A workshop canvas for the session *before* prioritization: draw the client's
as-is workflow as connected blocks, mark the friction on the steps that carry
it, attach the systems each step touches, then hang candidate AI use cases off
the pain they address.

`index.html` is the tool. Like every other browser tool in this toolkit it is a
single self-contained file that runs entirely in the browser and saves to
`localStorage` — open it from the hub, or straight off disk.

## Why the blocks are typed

Five block types — `step`, `pain`, `system`, `usecase`, `note` — rather than a
blank whiteboard. That is the point of the tool, not a limitation of it: the
same drawing a workshop room understands also yields a structured deliverable
(a walkable workflow, a friction log, a systems list, a scored candidate list)
and a set of candidates that **Use Case Prioritization** can import directly. A
board of free-form shapes produces a nice picture and nothing else.

## The three worked examples

Pick one from the dropdown beside **🧪 Load sample**:

| Example | Process |
|---------|---------|
| Nordkap Insurance | First notice of loss to claim decision — the engagement the rest of the toolkit shares |
| Nordvik Furniture | Range plan to delivered, installed furniture |
| Grønhøj Foods | Grower contract to product on the retail shelf, where shelf life is the binding constraint |

Only the Nordkap board writes to the shared engagement profile. The two
supply-chain boards are illustrations, so loading one deliberately does *not*
rename the client across the rest of the toolkit.

---

# Running a workshop with several people — `workshop-relay.py`

By default the board is single-user and completely local: nothing leaves the
browser, which is what makes it safe to open in front of a client.

For a room that wants to brainstorm on one board at the same time, this folder
ships an **optional** relay you run on your own laptop.

```bash
cd "Phase 1 - Discovery & Assessment/use-case-discovery-board"
python3 workshop-relay.py
```

It prints two addresses — one for you, one to read out to the room:

```
  Open on this laptop:
    http://localhost:8000/Phase%201%20-%20.../use-case-discovery-board/?session=default

  Share with the room (same wifi):
    http://192.168.1.24:8000/Phase%201%20-%20.../use-case-discovery-board/?session=default
```

Everyone opens that address, types their name in **Live session**, and presses
**Go live**. The first person in seeds the session with the board they have
open; everyone after that adopts it — and is warned first if they had work of
their own on screen.

Options: `--port`, `--host`, `--session`, `--root`.

## What it does and does not do

- **Standard library only.** No dependencies, no build step, one file.
- **It serves the toolkit's static files as well as relaying edits.** That is
  not a convenience. A page served over `https` cannot talk to a plain-`http`
  relay on a local network, so the board and the relay have to share an origin
  — which means the room loads the board *from your laptop*, not from the
  public GitHub Pages site.
- **Nothing is written to disk and nothing reaches a third party.** The session
  lives in the relay process's memory. Stop it with Ctrl-C and the session is
  gone; each participant keeps their own copy in their own browser.
- **It is not an authenticated server.** Anyone who can reach the address can
  join the session and edit the board. That is fine for a meeting room on a
  trusted network and is not fine on a public one — do not expose the port to
  the internet.

## How the syncing behaves

- **Last writer wins, per block.** Two people editing different blocks never
  collide. Two people dragging the *same* block will fight over it, which is a
  social problem rather than a technical one.
- **Block ids can never collide.** The relay hands each participant its own id
  range on join, so two people adding a block at the same instant still produce
  distinct blocks.
- **Undo stays local.** Your undo stack is yours; undoing republishes the board
  as you now have it, which will pull back something a colleague changed in the
  meantime. In a live session, prefer deleting a block to undoing your way out.
- **Loading an example while live replaces the board for everyone**, by design
  — it is the same "reset the board" action it always was.
- **Not connected means not connected.** Until someone presses Go live the page
  makes no network calls at all. Opened from the public site, the panel simply
  reports that no relay answered.

## Verifying a change

There is no build step. Serve the repo and open the board:

```bash
python3 -m http.server            # from the repo root, single-user
python3 workshop-relay.py         # from this folder, multi-user
```

The behaviours worth re-checking by hand after editing the sync code: a second
browser adopting the board, an edit crossing between them, the presence list
emptying when someone closes their tab, and — most importantly — that a board
which never connects issues no `/sync/` requests at all.
