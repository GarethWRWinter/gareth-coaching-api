# gareth-coaching-api

AI cycling-coaching product (FastAPI backend + Next.js frontend). Solo dev, building toward PMF.

## Two-account collaboration protocol (READ FIRST)

This repo is worked on by **two Claude accounts taking turns on the same branch** (`main`),
in this same local folder, syncing through GitHub (`origin`). Never both at once.

`HANDOFF.md` at the repo root is the **baton**. It records who holds the turn and what is in flight.

### At the START of every turn — claim the baton
1. `git pull --rebase` to get the other account's latest work.
2. Open `HANDOFF.md`. If `Holder:` is **FREE** or already you, you may work. If it names the
   **other** account, STOP and tell the user the other account still holds the turn.
3. Set `Holder:` to your account name and update `Updated:` with the date.

### While working
- Stay inside this folder (`gareth-coaching-api/`). Never run `git add .` from the home directory
  — `/Users/garethwinter/.git` is a stray repo and must not be committed to.
- Keep commits small and pushed often, so a handoff is always possible.

### At the END of every turn — release the baton
1. `git add -A && git commit` your work (clear message).
2. `git push origin main`.
3. Update `HANDOFF.md`: set `Holder:` to **FREE** (or the other account), fill in
   **In flight / Next** so the other account knows where to pick up. Commit + push that too.

### If `git pull --rebase` hits a conflict
Resolve in-folder, finish the rebase, then push. If unsure, stop and surface it to the user —
do not force-push over the other account's commits.

## Accounts
- **work** — the Mindvalley/work Claude login (`claude`)
- **personal** — the personal login (`claude-personal`, `CLAUDE_CONFIG_DIR=~/.claude-personal`)
