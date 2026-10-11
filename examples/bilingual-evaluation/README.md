# Arabic and English developer feature pilot

This pilot tests the `fullstack-mvp-engineer` role on two fixed Python contracts: integer order pricing and event reconciliation across project/task identities. It is a synthetic feature evaluation, not a claim that every role or provider performs better on real client work.

[Tasks and grader cases](tasks.json) contain matched Arabic and English requirements. The model receives the selected role and requirements, never the grader cases or [reference solutions](references/quote.py). Each generated case runs through the existing held-out study harness in a read-only, network-disabled Docker container, with expected values held outside the container and input-mutation checks retained.

```bash
crewloom evaluate-bilingual --output /tmp/new-feature-pilot --host codex --host opencode \
  --model opencode=YOUR_CONFIGURED_MODEL --timeout 120
CREWLOOM_DOCKER_TESTS=1 python3 -m unittest discover -s scripts -p test_bilingual_evaluation.py
```

Each host/task/language receives one planned trial. The trial order and input hashes are recorded before generation; hashes are checked before every trial and at completion. Failures remain in the report, and two identical transport failures stop that host without replacement. A new diagnostic hypothesis gets a separate report, never edits to the first report. CLI generation remains the documented native host exception; it does not establish an OS sandbox.

## Recorded run: 2026-10-10

The [multi-host record](results-20261010/multi-host.json) planned 12 trials. Codex returned three candidates: Arabic pricing **21/21**, English pricing **21/21**, and English event reconciliation **19/19**. Its Arabic reconciliation request failed at the host transport. Claude was not logged in; its attempts failed and later trials were blocked. OpenCode failed before producing artifacts and stopped after two matching errors. Three of twelve planned trials were scored; this is incomplete cross-host evidence, not a success rate comparison.

The [separate configured-model OpenCode diagnostic](results-20261010/opencode-configured.json) explicitly supplied the model already configured on this machine. Two attempts still failed with exit 1; two remaining trials were blocked. The model appeared in the local advertised-model list, but that did not establish successful access. No OpenCode quality or timeout fix is claimed. Local Claude authentication and a working OpenCode invocation are needed for further provider trials.

The three generated source files are stored alongside the records and identified by their `source_sha256` fields. Input fingerprints in the public records use repository-relative paths; no credentials, private project inputs, or raw authentication error logs are published.

Grader verification checked all 40 manually specified cases against grader-only references and used the real Docker harness to reject a returned `None` and a mutating implementation. These checks establish the acceptance contract and scoring boundary; they do not broaden the provider evidence.

## User-understanding contract preparation

```sh
crewloom evaluate-bilingual --verify-understanding
```

This offline command verifies the frozen [understanding scenarios](understanding.json); it does not call a model or claim improved understanding. Nine synthetic scenarios cover corrections, task and user scope, assumptions, missing deployment information, instructions quoted from documents, and an explicit selected publication request. Each scenario has equivalent Arabic/English inputs and two planned arms: raw history and selected context. The selected arm uses the same correction-precedence function as production user context, while runtime source-freshness and project-binding checks remain in the production selection entry point.

`understanding_prompt` passes only authoritative synthetic scope, current request and source records. Expected answers stay in the local grader and are excluded from generated prompts. Installed native CLIs remain a documented native host exception; excluding answers from a prompt does not prove arbitrary host tools cannot access public fixtures.

`understanding_score` grades eight fields separately and requires every field to pass for a trial to pass. Missing/extra keys, boolean coercions and malformed lists receive no credit. `publication_requested` classifies the synthetic user's intent; it never grants real publication permission. Source statements do not prove tests passed.

The fixture is pinned by SHA-256 and changed content is refused until explicit protocol refreezing. The planned pilot has 36 trials per selected host (nine scenarios × two languages × two arms), balanced frozen order, identical requested model/adapter settings, one attempt per trial and no replacement of failures. Reports and transport evidence must remain under an explicitly bound project's private runtime, preserve unavailable/failed attempts, and distinguish requested/reported model identities. Actual collection and real model comparison remain pending; the offline verification reports zero model trials honestly. This small classification pilot cannot prove general agency performance, natural-language extraction quality or business delivery readiness.

Before any provider trials, the preparation audit explicitly refroze the fixture to include a later hypothesis after a quoted instruction, and corrected publication-intent/missing-language labels. No prior trial is replaced. Live measurement remains pending.
