# Scoped native AX acceptance

Crewloom includes an optional CuaDriver client for a synthetic macOS application. It is separate from the project task MCP server. The exposed tools observe one configured application window and press explicitly allowed accessibility buttons. The current acceptance target is `com.crewloom.NativeFixture`, with the title `Crewloom Native Acceptance` and the buttons `Increment` and `Reset`.

## Contract and dependencies

Inputs: one bound canonical project/task, an owner-only private policy and its unchanged manifest, an existing private CuaDriver socket, and a freshly observed button handle. Outputs: scoped AX observations, private action records and an observation after delivery. Dependencies: macOS, the optional `crewloom[mcp]` extra, CuaDriver 0.28.2, and human-granted Accessibility permission. The synthetic fixture needs Apple's Swift compiler. No model provider is required.

The client never launches the driver, requests OS permissions, uses screen coordinates, switches focus, types arbitrary text or executes a command received through MCP. It connects with `mcp --embedded --socket` and has no broad-daemon fallback. `check_permissions` always receives `prompt:false`. Missing access, malformed structured output, a foreign or missing app/window, changed binding/policy/manifest, expired handles and unresolved captured task questions refuse the action. Transport errors preserve an uncertain action and consume its handle; there is no automatic retry. Re-observation does not by itself prove the user's postcondition.

## Prepare and review

```sh
crewloom native prepare --project /absolute/project --project-id example-project --task-id acceptance-task
```

Preparation writes an owner-only manifest and policy under `.crewloom/private/native/`. Existing policies cannot be overwritten. The private Unix socket path must be below macOS's 104-byte limit; a longer project path is refused explicitly. Preparation grants no authority and does not start a process.

Read the resulting manifest. [CuaDriver bounded mode](https://cua.ai/docs/cua-driver/guides/permissions) requires human approval of the exact manifest before starting with `--approve-capability-manifest`. Do not assert approval on behalf of the human or fall back to standard mode. If macOS requires Accessibility setup, the human grants it; Crewloom does not click system permission controls. The prepared manifest limits driver tools, expires after one hour, times out when idle, allows only the synthetic application and denies desktop display access.

After that review and approval, the operator starts the bounded daemon:

```sh
open -n -g -a CuaDriver --args serve --permission-mode bounded \
  --capability-manifest /absolute/project/.crewloom/private/native/HASH/capabilities.yaml \
  --approve-capability-manifest \
  --socket /absolute/project/.crewloom/private/native/HASH/driver.sock
```

Use the exact generated paths in place of `HASH`. Build [the fixture source](../examples/native/Fixture.swift) into a private `.app` bundle with bundle ID `com.crewloom.NativeFixture`, and launch it in the background. The fixture contains only a counter and two buttons; it has no network or account operations.

```sh
crewloom native serve --project /absolute/project --project-id example-project \
  --task-id acceptance-task --policy .crewloom/private/native/HASH/policy.json
```

The stdio server exposes `crewloom_native_snapshot` and `crewloom_native_click(handle)`. Observe first, choose a returned button handle, press it once, then inspect the returned fresh state to verify the expected counter. All handles are invalidated by a new snapshot or action. Concurrent calls serialize within this connection. Application PID and exact window ownership are rediscovered before acting; opaque driver tokens remain tied to the observed window.

## Evidence boundary

Driver-independent tests prove refusal of foreign applications, modified manifests, permissive policy files, stale/consumed handles and failed refreshes; they also verify background-only arguments and observe/act/reobserve sequencing. A successfully built fixture and these tests do not prove real Accessibility control. Record real driver tool calls, observed counter changes, actual permission status and negative target cases separately before claiming native execution. This client is an AX button acceptance surface, not general desktop automation or a sandbox for arbitrary host tools.
