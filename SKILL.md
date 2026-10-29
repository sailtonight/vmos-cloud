---
name: vmos-cloud
description: >
  Operate a VMOS Cloud phone (云手机 / 云机 / cloud Android) through the VMOS OpenAPI — no ADB
  port needed. Use whenever the user wants something done on their cloud phone: open an app
  (TikTok, Instagram, Chrome…), tap / swipe / type, search inside an app, take or save a
  screenshot, read what's on screen, install / uninstall APKs, check whether the phone is online,
  or change device-level settings (proxy, GPS, timezone, language, one-key new device).
  Triggers: 云手机、云机、手机上操作、打开 TikTok、在手机里搜索、截图保存、VMOS、padCode.
---

# VMOS Cloud phone

Everything goes through the bundled CLI (Python 3.8+ stdlib, nothing to install):

```sh
python3 <this-skill-dir>/scripts/vmos.py <command> [args]
```

Below, `vmos` = that command. Errors go to stderr as `error: …` with exit code 1.

## Setup — check before the first call of a session

Run `vmos config`. If `VMOS_AK` / `VMOS_SK` say `missing`, stop and walk the user through:

1. VMOS Cloud console (https://cloud.vmoscloud.com) → **Developer → API** → copy AccessKeyID + SecretAccessKey.
2. Save them (never paste keys into chat, never hard-code them in a skill or repo):
   ```sh
   mkdir -p ~/.config/vmos && cat > ~/.config/vmos/credentials <<'EOF'
   VMOS_AK=...
   VMOS_SK=...
   # Optional default padCode; omit if the account has one phone
   VMOS_PAD=...
   EOF
   chmod 600 ~/.config/vmos/credentials
   ```

Env vars `VMOS_AK` / `VMOS_SK` / `VMOS_PAD` override the file. `--pad <padCode>` overrides per call.

## Commands

| Goal | Command | Notes |
|---|---|---|
| Phones on the account | `vmos devices` | `status=10` = running; `adb=0` is fine, not needed |
| Online? foreground app? | `vmos status` | screen size + current package/activity |
| **See the screen** | `vmos shot [-o path]` | prints a local `.jpg` path → read the image file to view it |
| **Read elements** | `vmos ui [--find kw]` | `idx *=clickable (x,y) label`; often 5–20 s |
| Tap | `vmos tap X Y` · `vmos tap --text 搜索` · `vmos tap --index 7` | `--text` prefers exact text/desc/id, then substring; use `--exact` to disable fallback |
| Type | `vmos text "任意 unicode" [--verify] [--timeout 20]` | focus first; verification observes exact UI text without resending |
| Keys | `vmos key back\|home\|enter\|delete\|search\|recent\|<code>` | `enter` submits most search boxes |
| Scroll | `vmos scroll down\|up\|left\|right [--times N]` | `down` = reveal content below |
| Swipe / long press | `vmos swipe X1 Y1 X2 Y2 [--ms 300]` · `vmos longpress X Y` | `--adb` uses `input swipe` if simulateTouch misbehaves |
| Wait for text | `vmos wait "关键词" [--timeout 20]` | polls `ui` |
| Apps | `vmos launch <pkg>` · `stop` · `restart-app` · `clean-home` · `apps [--name X]` | |
| Open link / deep link | `vmos open-url <url> [--package <pkg>]` | fastest way into a specific page |
| Install APK | `vmos install <https-url> [--package <pkg>]` → `vmos task <id>` / `vmos apps` | async, auto-installs |
| Wait for installation | `vmos wait-app <pkg> [--timeout 120]` | polls installed apps by exact package; works with market installs too |
| Shell | `vmos shell "<cmd>"` | output truncated ~2000 chars — filter on device (`grep`, `head`) |
| Anything else | `vmos api <name> '<json>' [--with-pad] [--get]` | see `references/api.md` |

Coordinates are in the screenshot's pixel space (720×1280 on current pads), so a point read off
`shot` or `ui` can be tapped directly.

## How to drive the phone: observe → act → verify

Never assume what's on screen — apps restore their last page, show first-run dialogs, permission
prompts, login walls, ads. One action, then look again.

1. **Observe.** `vmos ui` first (cheap structured text). Use `vmos shot` + look at the image when:
   - `ui` is empty / has only a few unlabeled nodes (custom-drawn views — common in TikTok, games, video players),
   - the content is a WebView / web page (offscreen nodes get bogus bounds like `(0,0)` or pinned to the toolbar),
   - you need visual judgement (icons with no label, which video thumbnail, colours, is a popup covering it).
2. **Act.** Prefer, in order: `open-url` deep link → `tap --text "button label" --exact` → `tap X Y` from `ui` → `tap X Y` read off the screenshot.
3. **Verify.** Wait ~1–2 s (pages animate; a `ui` taken mid-transition returns the old screen or nothing), then `ui`/`shot` again and check you're where you expected. If UI still shows the old page, take a screenshot before another action: the tree can lag even after a successful tap or swipe. Do not repeat the same tap blindly. After ~3 failed attempts at one step, take a screenshot and report back.

Dismiss optional onboarding with `不用了` / `Not now` / `Skip` / `×`. For ordinary browsing, skip interest selection and decline optional notifications; allow permissions only when needed for the requested task. Never tap
purchase / pay / delete-account / send-message buttons unless the user asked for exactly that.
Logins, captchas and 2FA: stop and ask the user.

## Input: focus → type once → verify

After opening a search page, wait 1–2 s and inspect `ui`/`shot` to confirm the input field is ready.
Tap the field if necessary. Then use `vmos text "lipstick 美妆 123" --verify`.
`ok` from the input API only acknowledges the request. `--verify` waits for an exact text value
in the accessibility tree; it does not prove focus, replacement, or successful submission.
If text is masked, appended to existing content, missing from the tree, or also appears in a
suggestion, inspect a screenshot of the actual field. Clear existing text via the observed UI
when replacement is intended. On verification failure, inspect before retrying; never blindly
send the same text twice. Submit only after checking the field.

## Install and verify

Use a trusted APK URL with `install`, or the phone's existing app market. After starting the
installation, poll `wait-app <package>` (or `apps --name ...` if the package is unknown).
Do not infer failure from the absence of an “Open” button: the market may stay on its download
screen after installation finishes. A timeout means installation is unconfirmed, not cancelled.
`wait-app` checks package presence, not completion of an upgrade to an already installed app;
for upgrades, inspect the task and installed version. Finally launch the package and inspect
its first screen. Installation, launch, and usable browsing are separate checks.

## Recipe: search in TikTok and save a screenshot

Run `apps --name TikTok` and use the returned package for launch/deep links:
`com.zhiliaoapp.musically` or Asia's `com.ss.android.ugc.trill`.
`com.ss.android.ugc.aweme` is Douyin, a separate app; do not substitute it for TikTok.

```sh
vmos status
vmos apps --name TikTok
vmos launch <installed-package>
sleep 2
vmos ui                       # observe onboarding or the search control
vmos shot                     # inspect if UI is sparse or stale
vmos tap --text Search --exact # only if observed; otherwise use observed coordinates
sleep 2
vmos ui                       # confirm the search input is ready; tap if needed
vmos text "lipstick" --verify
# If verification fails, inspect the field with shot before proceeding.
vmos key enter
sleep 2
vmos shot -o ~/vmos-shots/tiktok-lipstick.jpg
```

When a deep link is useful, try `vmos open-url "https://www.tiktok.com/search?q=lipstick" --package <installed-package>`,
then verify the resulting page. First-run dialogs may intercept it.

## Device-level settings (via `vmos api`, see references/api.md)

These change the phone's identity / network — confirm with the user before running, and expect
some to restart the pad:

- Proxy: `setProxy`, `smartIp` / `notSmartIp`, check with `proxyInfo`
- Location / locale: `gpsInjectInfo`, `updateTimeZone`, `updateLanguage`, `updateSIM`
- `replacePad` (one-key new device) and `reset` **wipe data**; `restart` reboots — always ask first.
- Anything that buys (`createMoneyOrder`, `buyDynamicProxy`, `cloudNumber/purchase`, …) costs money — never call without explicit instruction.

## Known limits

- Each call is a cloud round-trip: tap/type/scroll ≈ 0.3 s, `shell`/`key` ≈ 2 s, `ui` often 5–20 s, `shot` ≈ 1–2 s.
- `shell` output is capped near 2000 chars; `ui` already works around this by paging.
- `simulateTouch` position format (`actionType` 0 down / 2 move / 1 up) is not in the public docs — it works today; if swipes stop working, use `swipe --adb`.
- Screenshot URLs expire; `shot` downloads immediately, so keep the local path, not the URL.

Polling timeouts are budgets between observations; an in-flight cloud call or UI dump can finish after the deadline.
