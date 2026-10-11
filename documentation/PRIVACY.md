# Private customization and deliberate publication

Crewloom keeps personal data separate from the distributable toolkit. Use a bound project ID/root; project memory belongs to that project, not to the installed library. Do not edit the installation's public `Brain/` or bundled role guides with customer history.

## Private layout

- `.crewloom/private/inputs/`: immutable conversation excerpts and private source copies.
- `.crewloom/private/overrides/`: personal instructions or templates. These are local data, not automatically executed code; record a preference through user context to carry it into the model prompt.
- `.crewloom/private/exports/`: explicitly selected publication ZIPs, owner-readable only.
- Existing `.crewloom/` context, lessons, task state and user memory remain ignored. Bound application projects also ignore root `Brain/` memory during privacy setup; the toolkit retains its public foundation memory.
- Installing roles adds an ignore rule for that host's `skills/*/brain/` project memory. Existing tracked files are **not** automatically removed from Git.

Put a conversation excerpt directly in a private input file, then use it with `crewloom user-context record/contract --source .crewloom/private/inputs/message.txt`. A source recorded outside that directory is copied privately, and its canonical original path is registered as non-publishable. The original is retained; freshness still checks its original hash. Explicit privacy setup registers source paths from older recorded user context too, without exposing their text or rewriting their records.

Recording new user context automatically enables the commit guard, preserving existing hooks. Other projects can enable it explicitly once bound:

```sh
crewloom privacy init --project /path/to/project
crewloom privacy check --project /path/to/project
```

Finish or cancel the active task before explicit privacy setup. Recording context for the current task performs setup under that task's existing ownership checks. Setup records the prior hook directory privately, chains its pre-commit and preserves its other hooks. It never disables the existing hook or overwrites its source. A missing/changed owned guard or previous pre-commit is refused.

## What commits are rejected

Generated host instructions use the portable `crewloom` command and keep checkout IDs out of public instruction text. Existing custom instructions are not rewritten just to remove older paths.

The guard reads **index blobs**, not just current working files. It rejects tracked/staged `.crewloom` state, private role memory, registered conversation sources, dotenv secrets, key files, recognized credential patterns and files above the 2 MiB scan limit. Forced `git add -f` does not bypass it. Temporary commit indexes must belong to the selected checkout.

The toolkit's own `crewloom-toolkit` identity permits its public role-memory templates; private runtime paths, registered user sources and known credentials remain blocked. Its mandatory repository gate performs those index checks as well.

`init` or `check` returns exit 2 when tracked private data is found. Review those files and, if appropriate, remove them **from the index while retaining local contents**. Crewloom does not automatically untrack files or rewrite history. `.gitignore` alone cannot hide tracked changes. Never use `assume-unchanged` or `skip-worktree` as a confidentiality boundary.

## Selected publication packet

```sh
crewloom privacy export --project /path/to/project \
  --include README.md --include src/app.py \
  --out .crewloom/private/exports/public-code.zip
```

Include exact regular files, not directory wildcards. The command rejects private paths, aliases to private paths, symlinks/hardlinks and recognized credentials. It permits at most 256 unique files, 2 MiB per file and 16 MiB total. An existing output is never overwritten. The report names selected files and the packet hash; no push, upload or repository creation occurs. Extract and review the packet in a separate publication checkout before uploading it.

## Boundaries and recovery

Known-pattern credential detection does not identify all secrets, personal information or proprietary content. A clean scan is not proof of confidentiality. Review selected content; use a private remote for personal backup. Avoid adding private data outside these namespaces or pasting it into tracked code/docs.

These checks protect the Git commit path while installed hooks remain active; they do not sandbox host tools, prevent authorized external uploads or control model-provider retention. Existing history and already uploaded data require separate inspection. Real exposed credentials require rotation, not merely a new ignore rule. Crewloom never rewrites history or changes repository visibility automatically.

Hook configuration lives in local Git config and ignored metadata. Each cloned checkout needs its own setup. Preserve the prior hook directory; if it disappears, restore it before committing. Hook removal/bypass is outside the protection boundary. No encryption or universal leakage-prevention guarantee is claimed.

New coordinator worktrees initialize missing role memory from public templates and empty project entries. Existing guides and local lessons are preserved. Private root lessons are not automatically copied into parallel tasks.

Linked worktrees inherit Git hook configuration. The guard verifies their shared Git directory and project binding, then checks the committing worktree’s index and runs the previous hook there. A worktree from another project is refused.
