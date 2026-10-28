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
   VMOS_PAD=...        # optional default padCode; omit if the account has one phone
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
| **Read elements** | `vmos ui [--find kw]` | `idx *=clickable (x,y) label`; ~5 s |
| Tap | `vmos tap X Y` · `vmos tap --text 搜索` · `vmos tap --index 7` | `--text` = substring of text/desc/resource-id, clickable first |
| Type | `vmos text "任意 unicode"` | into the focused field — tap the field first |
| Keys | `vmos key back\|home\|enter\|delete\|search\|recent\|<code>` | `enter` submits most search boxes |
| Scroll | `vmos scroll down\|up\|left\|right [--times N]` | `down` = reveal content below |
| Swipe / long press | `vmos swipe X1 Y1 X2 Y2 [--ms 300]` · `vmos longpress X Y` | `--adb` uses `input swipe` if simulateTouch misbehaves |
| Wait for text | `vmos wait "关键词" [--timeout 20]` | polls `ui` |
| Apps | `vmos launch <pkg>` · `stop` · `restart-app` · `clean-home` · `apps [--name X]` | |
| Open link / deep link | `vmos open-url <url> [--package <pkg>]` | fastest way into a specific page |
| Install APK | `vmos install <https-url> [--package <pkg>]` → `vmos task <id>` / `vmos apps` | async, auto-installs |
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
2. **Act.** Prefer, in order: `open-url` deep link → `tap --text` → `tap X Y` from `ui` → `tap X Y` read off the screenshot.
3. **Verify.** Wait ~1–2 s (pages animate; a `ui` taken mid-transition returns the old screen or nothing), then `ui`/`shot` again and check you're where you expected. If not, re-plan — don't repeat the same tap blindly. After ~3 failed attempts at one step, take a screenshot and report back.

Dismiss blockers as they appear (`不用了` / `Not now` / `Skip` / `Allow` / `×`). Never tap
purchase / pay / delete-account / send-message buttons unless the user asked for exactly that.
Logins, captchas and 2FA: stop and ask the user.

## Recipe: search in an app and save a screenshot (e.g. TikTok)

```sh
vmos status                                   # online? what's in front?
vmos apps --name TikTok                       # installed? (pkg: com.zhiliaoapp.musically, CN: com.ss.android.ugc.aweme)
vmos launch com.zhiliaoapp.musically && sleep 4
vmos ui                                       # look for a search icon / "Search" desc
vmos shot                                     # if ui is sparse: view image, locate the 🔍 (usually top-right)
vmos tap --text Search    # or: vmos tap X Y from the image
sleep 1.5 && vmos text "lipstick" && vmos key enter
sleep 3 && vmos shot                          # view results, pick the target
vmos tap X Y && sleep 3
vmos shot -o ~/vmos-shots/tiktok-lipstick.jpg # verify it's the right page, report the path
```

Shortcut when a web/deep link exists: `vmos open-url "https://www.tiktok.com/search?q=lipstick" --package com.zhiliaoapp.musically`.

## Device-level settings (via `vmos api`, see references/api.md)

These change the phone's identity / network — confirm with the user before running, and expect
some to restart the pad:

- Proxy: `setProxy`, `smartIp` / `notSmartIp`, check with `proxyInfo`
- Location / locale: `gpsInjectInfo`, `updateTimeZone`, `updateLanguage`, `updateSIM`
- `replacePad` (one-key new device) and `reset` **wipe data**; `restart` reboots — always ask first.
- Anything that buys (`createMoneyOrder`, `buyDynamicProxy`, `cloudNumber/purchase`, …) costs money — never call without explicit instruction.

## Known limits

- Each call is a cloud round-trip: tap/type/scroll ≈ 0.3 s, `shell`/`key` ≈ 2 s, `ui` ≈ 5 s, `shot` ≈ 1–2 s.
- `shell` output is capped near 2000 chars; `ui` already works around this by paging.
- `simulateTouch` position format (`actionType` 0 down / 2 move / 1 up) is not in the public docs — it works today; if swipes stop working, use `swipe --adb`.
- Screenshot URLs expire; `shot` downloads immediately, so keep the local path, not the URL.
