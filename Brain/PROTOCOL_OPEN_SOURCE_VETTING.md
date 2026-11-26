# Protocol: Open-Source Component Vetting & Upstream Lifecycle (فحص واعتماد وإدارة المكونات مفتوحة المصدر)

Type: Protocol. Status: **active**.
Enforced by: `scripts/check-oss-updates.mjs`, `agent/apps/crewloom-desktop/tests/browser-packaging.test.mjs`, `.agent/rules/open-source-governance.md`, and `core/Brain/ARTIFACT_INDEX.md`.

```
name:        open-source-vetting
trigger:     any proposal to add, vendor, or update any third-party open-source component (native sidecars, runtime executables, AI models, vendored libraries or source trees, agent skills, MCP providers, system gateways or daemons) in any Crewloom workspace
steps:       A Intake & Provenance -> B Isolation & Packaging -> C Security Scan & Manifest -> D Decide & Register -> E Upstream Track & Single-Click Check
exit:        component is completely self-contained (zero host toolchain required), registered in docs/OPEN_SOURCE_STACK.md with its component type, and tracked via scripts/check-oss-updates.mjs across all four required types (Sidecars, Models, Libraries, Skills)
on_failure:  REJECT immediately; no external manual installation (brew/apt/pip/cargo/npm -g) may ever be demanded from the end-user
```

---

## 1. Scope (نطاق المكونات)

This protocol governs all external open-source assets across five distinct categories. Every external component MUST be tagged with exactly one of these categories in `docs/OPEN_SOURCE_STACK.md`:

1. **Native Sidecars & Executables:** Binary runtimes bundled with the desktop app (`whisper.cpp`, `agent-browser`, `ffmpeg`).
2. **Vendored Libraries & Source Trees:** Embedded third-party libraries and source code maintained inside the repo (`vendor/cordis`).
3. **Open AI Models & Weights:** Local acoustic/reasoning weights (`ggml-small.bin`, Pulse triage matrices, downloaded GGUF weights).
4. **Agent Skills & MCP Providers:** Accredited skill folders (`.agent/skills/`) and MCP server providers.
5. **System Gateways & Daemons:** Open IPC bridges and system communication components (only when third-party; first-party gateways such as `crewloom-bridge` are tracked as first-party releases).

*(Standard package-lock dependencies managed by `pnpm-lock.yaml` and `Cargo.lock` are tracked through their respective lockfiles and exempt from manual protocol staging. They are NOT listed in `docs/OPEN_SOURCE_STACK.md`.)*

### 1.1 Required component-type coverage

The four component types that MUST be covered by both `docs/OPEN_SOURCE_STACK.md` and `scripts/check-oss-updates.mjs` are:

| Required type | Stack registry section | Script category label |
|---|---|---|
| Sidecars | §1 Native Desktop Sidecars | `Native Desktop Sidecar` |
| Models | §3 Models & Inference Weights | `Model Weight` |
| Libraries | §2 Engines & Vendored Cores (vendored third-party only) | `Vendored Library` |
| Skills | §4 Accredited Third-Party Skills & Plugins | `Accredited Cloud Skills` / `Document Processors` / `Browser Diagnostics` / `Modern Web Engineering` |

A protocol run is **not complete** unless all four types have at least one tracked entry OR an explicit documented reason (e.g. "no third-party libraries vendored at this time") recorded in `docs/OPEN_SOURCE_STACK.md`.

---

## 2. The 5-Stage Vetting Pipeline

| Stage | Objective | Tools & Requirements | Exit Condition |
|---|---|---|---|
| **A. Intake & Provenance** | Verify legitimate origin, license, and necessity | `gh api repos/<owner>/<repo>`, SPDX license verification. Permissive licenses only (MIT, Apache-2.0, BSD, ISC, MPL-2.0). | Upstream repository URL, pinned release tag/commit, and license recorded. |
| **B. Isolation & Self-Containment** | Enforce the **Zero-External-Install Invariant** | Must be staged via `scripts/prepare-<tool>.mjs` as a Tauri sidecar in `src-tauri/binaries/` with `@rpath` resolution and ad-hoc code-signing (`codesign`) where applicable. | Binary runs in an isolated environment without Homebrew or system package managers. |
| **C. Security & Integrity** | Scan for vulnerabilities and compute cryptographic digest | SHA-256 verification of binaries and archives; verify no leaked dynamic libraries via `otool -L` (macOS) or `ldd` (Linux); `gh api repos/<owner>/<repo>/security-advisories` for known advisories. | Staged binary checksum matches published release manifest; no unwaived HIGH findings. |
| **D. Decide & Register** | Catalog the component in the architectural registry | Add entry to `docs/OPEN_SOURCE_STACK.md` (workspace root) with local dev path, category (one of the five above), upstream repo, and architectural purpose. | Registry updated; packaging integration tests pass (`node --test tests/browser-packaging.test.mjs`). |
| **E. Upstream Track & Single-Click Check** | Track new releases and provide 1-click update checks | Add to `scripts/check-oss-updates.mjs` with `name`, `repo`, `category`, `localDevPath`, `pinnedVersion`. | Developers can run `pnpm run check:oss` to check all upstream releases across the entire stack in one click, with no web scraping. |

---

## 3. Mandatory Invariants

1. **Zero External Install:** End-users must NEVER be instructed to run `brew install`, `apt-get`, `pip install`, `cargo install`, or `npm -g` to use a desktop feature. Everything needed for runtime must be shipped in the app bundle. Any UI that currently prints such an instruction is a defect to be remediated, not an accepted pattern.
2. **Single-Action Upstream Check:** Running `pnpm run check:oss` must audit all tracked components and report available upstream releases without web scraping (official `gh api` only).
3. **No Unvetted Updates:** An upstream update is treated as a new cycle of this protocol; automated updating never bypasses verification tests.
4. **Coverage Completeness:** The script's tracked list must cover at least one entry in each of the four required types (Sidecars, Models, Libraries, Skills) unless a type is explicitly documented as unused in `docs/OPEN_SOURCE_STACK.md`.
5. **No Vulnerabilities Shipped:** Components with known, unwaived security advisories are not shipped. Waivers follow `core/Brain/PROTOCOL_SKILL_VETTING.md` rule 5 (recorded in `SOURCE.md`).

---

## 4. Verification Checklist (Pre-Approval)

Before a component is approved under this protocol, confirm ALL of the following:

- [ ] Upstream repository URL and pinned release tag/commit recorded.
- [ ] SPDX license recorded and is permissive (MIT, Apache-2.0, BSD, ISC, MPL-2.0).
- [ ] Zero external install: no `brew`/`apt`/`pip`/`cargo`/`npm -g` instruction reaches the end-user for this component.
- [ ] Binary (if any) is staged under `src-tauri/binaries/` and passes `otool -L` / `ldd` self-containment checks.
- [ ] SHA-256 digest matches the published release manifest.
- [ ] No unwaived HIGH security findings (advisory scan clean or waived with recorded reason).
- [ ] Entry added to `docs/OPEN_SOURCE_STACK.md` with category, local path, upstream repo, tracking mechanism, and architectural role.
- [ ] Entry added to `scripts/check-oss-updates.mjs` (for external components).
- [ ] Packaging integration tests pass (`node --test tests/browser-packaging.test.mjs`).
- [ ] Registered in `core/Brain/ARTIFACT_INDEX.md` if a new protocol or rule is introduced.

---

## 5. Approval Record

| Date | Component | Type | Reviewer | Decision | Notes |
|---|---|---|---|---|---|
| 2026-11-21 | Protocol + script (initial) | All | Agent (this review) | Approved | Coverage expanded to all four required types; script tracks Sidecars, Models, Libraries, Skills; zero external install invariant reinforced. |

---

## Cross-References

- Skill vetting: [`core/Brain/PROTOCOL_SKILL_VETTING.md`](PROTOCOL_SKILL_VETTING.md)
- Stack registry: `docs/OPEN_SOURCE_STACK.md` (workspace root)
- Governance rule: `.agent/rules/open-source-governance.md` (workspace root)
- Artifact index: [`core/Brain/ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md)