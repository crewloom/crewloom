# Android Virtual Display Feasibility Spike (WP-35)

## Overview & Empirical Test Environment

This spike investigates the feasibility of leveraging Android secondary virtual and overlay displays for isolated background Computer Use automation without disrupting foreground user displays.

All commands were executed empirically on a dedicated, isolated test emulator (`emulator-5580`) booted from the `crewloom-conformance-35` AVD created in WP-34. The user-owned emulator (`emulator-5554`) was never touched.

### Device Baseline
- **Serial**: `emulator-5580`
- **SDK Level (`getprop ro.build.version.sdk`)**: `35`
- **Release Version (`getprop ro.build.version.release`)**: `15`
- **Product Model (`getprop ro.product.model`)**: `sdk_gphone64_arm64`
- **Primary Display (`displayId 0`)**: `320 x 640`, density `160 dpi`, type `INTERNAL`

---

## Step 1: Secondary Display Creation

### Command
```bash
adb -s emulator-5580 shell settings put global overlay_display_devices "1080x1920/420"
```

### Observation (`dumpsys display`)
```text
Display Devices: size=2
  DisplayDeviceInfo{"Built-in Screen": uniqueId="local:4619827259835644672", 320 x 640, modeId 1, renderFrameRate 60.000004, defaultModeId 1, density 160, touch INTERNAL, rotation 0, type INTERNAL...}
  DisplayDeviceInfo{"Overlay #1": uniqueId="overlay:1", 1080 x 1920, modeId 2, renderFrameRate 60.000004, defaultModeId 2, density 420, touch VIRTUAL, rotation 0, type OVERLAY, state ON...}
```

```text
DisplayInfo{"Overlay #1", displayId 2, displayGroupId 0, FLAG_PRESENTATION, FLAG_TRUSTED, real 1080 x 1920, largest app 1080 x 1920, smallest app 1080 x 1920... density 420, uniqueId "overlay:1"}
```

### Finding
A secondary overlay display (`Overlay #1`, 1080x1920 @ 420 dpi) is dynamically instantiated by `OverlayDisplayAdapter`.
WindowManager assigns it logical **`displayId 2`**, with touch mode `VIRTUAL` and state `ON`.
Teardown via `settings put global overlay_display_devices '""'` restores the system cleanly to `size=1`.

---

## Step 2: Launch App on Secondary Display (`am start --display <id>`)

### Command
```bash
adb -s emulator-5580 shell am start --display 2 -a android.settings.SETTINGS
```

### Output
```text
Starting: Intent { act=android.settings.SETTINGS }
```

### Verification (`dumpsys window`)
```text
mCurrentFocus=Window{6d2c8f1 u0 com.android.settings/com.android.settings.homepage.SettingsHomepageActivity}
displayId=2
```

### Finding
The stock Settings application (`com.android.settings.homepage.SettingsHomepageActivity`) successfully launched directly onto `displayId=2`. WindowManager confirmed `displayId=2` as the window container and focused display.

---

## Step 3: Input Targeting (`input -d <id>`)

### Command
```bash
adb -s emulator-5580 shell input -d 2 tap 500 500
adb -s emulator-5580 shell input -d 2 keyevent KEYCODE_NAVIGATE_NEXT
```

### Output & Return Code
```text
Exit code: 0
```

### Finding
The Android `input` CLI binary natively supports the `-d <DISPLAY_ID>` flag. Motion events (tap) and key events (keyevent) were accepted with exit code 0 when routed to logical `displayId 2`.

---

## Step 4: Screencap Targeting (`screencap -d <id>`)

### Attempt A: Logical WindowManager Display ID (`-d 2`)
```bash
adb -s emulator-5580 shell screencap -d 2 -p /sdcard/display2.png
```
**Output:**
```text
Failed to take screenshot. Status: -2
Capturing failed.
Exit code: 1
```

### Analysis of Failure
The `screencap` CLI tool connects to SurfaceFlinger. As documented in its usage output (`see "dumpsys SurfaceFlinger --display-id"`), `-d` expects a 64-bit SurfaceFlinger display token rather than a WindowManager logical ID. Logical ID `2` returns status `-2` (BAD_VALUE / NAME_NOT_FOUND).

### Attempt B: SurfaceFlinger Virtual Display ID
Inspecting `dumpsys SurfaceFlinger`:
```text
Displays (2 entries)
Display 4619827259835644672 (physical, "EMU_display_0")
Virtual Display 11529215046861944359
    name="Overlay #1"
    powerMode=On
```

Capturing using the 64-bit SurfaceFlinger Virtual Display ID:
```bash
adb -s emulator-5580 shell screencap -d 11529215046861944359 -p /sdcard/overlay.png
```
**Output:**
```text
Exit code: 0
-rw-rw---- 1 u0_a191 media_rw 35418 2026-10-26 13:37 /sdcard/overlay.png
```

### Alternative: All Active Displays (`-a`)
```bash
adb -s emulator-5580 shell screencap -a -p /sdcard/disp.png
```
**Output:**
```text
Exit code: 0
-rw-rw---- 1 u0_a191 media_rw 88173 2026-10-26 13:37 /sdcard/disp.png
```

### Finding
Direct targeting with the WindowManager logical ID `2` fails (`not feasible` with integer ID). However, targeting is **feasible with SurfaceFlinger token translation**: querying `dumpsys SurfaceFlinger` yields the 64-bit virtual display token (`11529215046861944359`), allowing single-frame capture via `screencap -d <64bit_id>`. Alternatively, `screencap -a` captures active displays.

---

## Verdict Summary Table

| Step | Operation | Target | Empirical Result | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | Create secondary display | `settings put global overlay_display_devices "1080x1920/420"` | Instantiated `Overlay #1` (`displayId 2`, 1080x1920 @ 420 dpi) in `dumpsys display` | **feasible** | Cleanly tear down via `settings put global overlay_display_devices '""'` |
| 2 | Launch app on display | `am start --display 2 -a android.settings.SETTINGS` | Launched `SettingsHomepageActivity` on `displayId=2` | **feasible** | `mCurrentFocus` and `dumpsys window` reflect `displayId=2` |
| 3 | Input dispatch | `input -d 2 tap 500 500` / `input -d 2 keyevent ...` | Events dispatched with exit code 0 | **feasible** | Android 15 `input` binary supports `-d DISPLAY_ID` |
| 4a | Screencap with logical ID | `screencap -d 2` | `Failed to take screenshot. Status: -2` | **not feasible** | SurfaceFlinger rejects integer WindowManager display IDs |
| 4b | Screencap with SF 64-bit token | `screencap -d 11529215046861944359` | Successfully generated PNG (35,418 bytes) | **device-dependent** | Requires reading the 64-bit `Virtual Display` token from `dumpsys SurfaceFlinger` |
| 4c | Screencap all active | `screencap -a -p /sdcard/disp.png` | Successfully generated PNG (88,173 bytes) | **feasible** | Standard flag across Android 10+ |

---

## Safety & Cleanup Verification

- `adb devices -l` verified before and after test: `emulator-5554` (transport_id:5) remained untouched throughout the spike.
- `emulator-5580` was cleanly stopped via `emulator.sh stop` (`OK: killing emulator, bye bye`).
- State file `.emulator-5580.state` cleaned up.
