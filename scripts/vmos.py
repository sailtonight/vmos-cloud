#!/usr/bin/env python3
"""VMOS Cloud phone CLI — drives a cloud phone purely through the VMOS OpenAPI (no ADB port needed).

    python3 vmos.py devices
    python3 vmos.py shot
    python3 vmos.py ui
    python3 vmos.py tap 360 1085          # or: tap --text "保持未登录状态"
    python3 vmos.py text "TikTok 美妆"
    python3 vmos.py key enter

Credentials: ~/.config/vmos/credentials (KEY=VALUE lines) or env vars, env wins:
    VMOS_AK=...   VMOS_SK=...   VMOS_PAD=<default padCode, optional>

Python 3.8+ stdlib only.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API_HOST = "https://api.vmoscloud.com"
API_PREFIX = "/vcpcloud/api/padApi/"
CRED_FILE = os.path.expanduser(os.environ.get("VMOS_CRED_FILE", "~/.config/vmos/credentials"))
CACHE_DIR = os.path.expanduser("~/.cache/vmos")
SHOT_DIR = os.path.expanduser(os.environ.get("VMOS_SHOT_DIR", "~/vmos-shots"))

# asyncCmd truncates taskResult at ~2000 chars; page long output by lines.
UI_PAGE_LINES = 30
KEYS = {"back": 4, "home": 3, "enter": 66, "recent": 187, "menu": 82, "delete": 67, "del": 67,
        "search": 84, "tab": 61, "power": 26, "volup": 24, "voldown": 25, "escape": 111}


class VmosError(Exception):
    pass


# ---------- config & transport ----------

def load_config():
    cfg = {}
    if os.path.exists(CRED_FILE):
        with open(CRED_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("VMOS_AK", "VMOS_SK", "VMOS_PAD"):
        if os.environ.get(k):
            cfg[k] = os.environ[k]
    return cfg


def call(api, body=None, method="POST"):
    """Signed OpenAPI call. X-Sign = sha256(SK + ts + path + bodyOrQuery)."""
    cfg = load_config()
    ak, sk = cfg.get("VMOS_AK"), cfg.get("VMOS_SK")
    if not ak or not sk:
        raise VmosError(f"missing VMOS_AK / VMOS_SK — put them in {CRED_FILE} (see SKILL.md Setup)")
    path = API_PREFIX + api.lstrip("/")
    ts = str(int(time.time()))
    if method == "GET":
        query = "&".join(f"{k}={v}" for k, v in (body or {}).items())
        data, url, signed = None, API_HOST + path + (f"?{query}" if query else ""), query
    else:
        signed = json.dumps(body if body is not None else {}, separators=(",", ":"), ensure_ascii=False)
        data, url = signed.encode("utf-8"), API_HOST + path
    sign = hashlib.sha256((sk + ts + path + signed).encode("utf-8")).hexdigest()
    req = urllib.request.Request(url, data=data, method=method, headers={
        "X-Access-Key": ak, "X-Timestamp": ts, "X-Sign": sign, "Content-Type": "application/json"})
    # Retry only connection-level failures (DNS / TCP / TLS handshake): the request never reached
    # the server, so retrying can't double-tap. Read timeouts are not retried.
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            raise VmosError(f"HTTP {e.code} from {api}: {e.read()[:300]!r}")
        except urllib.error.URLError as e:
            if attempt == 2 or isinstance(e.reason, TimeoutError):
                raise VmosError(f"network error calling {api}: {e.reason}")
            time.sleep(1 + attempt)
        except TimeoutError:
            raise VmosError(f"timeout calling {api} (request may have been applied — observe before retrying)")
    if resp.get("code") != 200:
        raise VmosError(f"{api} failed: code={resp.get('code')} msg={resp.get('msg')}")
    return resp


def first(data):
    return data[0] if isinstance(data, list) and data else data


class Phone:
    def __init__(self, pad):
        self.pad = pad

    def api(self, name, body=None):
        resp = call(name, {"padCodes": [self.pad], **(body or {})})
        d = first(resp.get("data"))
        if isinstance(d, dict) and d.get("vmStatus") in (0, "0"):
            raise VmosError(f"{self.pad} is offline (vmStatus=0)")
        if isinstance(d, dict) and d.get("errMsg"):
            raise VmosError(f"{name}: {d['errMsg']}")
        return resp

    # ----- shell -----
    def shell(self, cmd, timeout=60):
        d = first(self.api("asyncCmd", {"scriptContent": cmd})["data"])
        tid = d["taskId"]
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.5)
            r = first(call("executeScriptInfo", {"taskIds": [tid]})["data"])
            st = r.get("taskStatus") or 0
            if st == 3:
                return r.get("taskResult") or ""
            if st < 0:
                raise VmosError(f"shell task {tid} failed (status {st}): {r.get('errorMsg')}")
        raise VmosError(f"shell task {tid} timed out after {timeout}s")

    # ----- screen geometry (cached) -----
    def size(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache = os.path.join(CACHE_DIR, f"{self.pad}.json")
        if os.path.exists(cache):
            with open(cache) as f:
                return tuple(json.load(f)["size"])
        out = self.shell("wm size")
        m = re.findall(r"(\d+)x(\d+)", out)
        w, h = map(int, m[-1]) if m else (720, 1280)  # last line = override size if set
        with open(cache, "w") as f:
            json.dump({"size": [w, h]}, f)
        return w, h

    def touch(self, positions):
        w, h = self.size()
        return self.api("simulateTouch", {"width": w, "height": h, "positions": positions})

    # ----- observe -----
    def screenshot(self, out=None):
        d = first(self.api("screenshot", {"rotation": 0, "broadcast": False})["data"])
        url = d.get("accessUrl")
        if not url:
            raise VmosError(f"screenshot returned no accessUrl: {d}")
        if not out:
            os.makedirs(SHOT_DIR, exist_ok=True)
            out = os.path.join(SHOT_DIR, f"{self.pad}-{time.strftime('%Y%m%d-%H%M%S')}.jpg")
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        for attempt in range(3):
            try:
                urllib.request.urlretrieve(url, out)
                return out
            except urllib.error.URLError as e:
                if attempt == 2:
                    raise VmosError(f"screenshot download failed: {e.reason}")
                time.sleep(1 + attempt)

    def ui(self, include_all=False):
        """Compact accessibility tree, built on-device to dodge the 2000-char output limit."""
        keep = "" if include_all else " | grep -v '^||false|'"
        script = (
            "uiautomator dump /sdcard/.vmos_ui.xml >/dev/null 2>&1; "
            "sed 's/<node /\\n<node /g' /sdcard/.vmos_ui.xml | "
            "sed -nE 's/.* text=\"([^\"]*)\".* resource-id=\"([^\"]*)\".* content-desc=\"([^\"]*)\".* "
            "clickable=\"([a-z]*)\".* bounds=\"\\[([0-9]+),([0-9]+)\\]\\[([0-9]+),([0-9]+)\\]\".*/"
            "\\1|\\3|\\4|\\5,\\6,\\7,\\8|\\2/p'" + keep + " > /sdcard/.vmos_ui.txt; "
            "wc -l < /sdcard/.vmos_ui.txt"
        )
        total = int((self.shell(script).strip() or "0").split()[0])
        lines = []
        for start in range(1, total + 1, UI_PAGE_LINES):
            chunk = self.shell(f"sed -n '{start},{start + UI_PAGE_LINES - 1}p' /sdcard/.vmos_ui.txt")
            lines += chunk.splitlines()
        w, h = self.size()
        els = []
        for ln in lines:
            parts = ln.rsplit("|", 3)
            if len(parts) != 4:
                continue
            label, click, b, rid = parts
            text, _, desc = label.partition("|")
            try:
                x1, y1, x2, y2 = map(int, b.split(","))
            except ValueError:
                continue
            visible = x2 > x1 and y2 > y1 and x1 < w and y1 < h and x2 > 0 and y2 > 0
            if not include_all and not visible:
                continue
            els.append({"i": len(els), "text": text, "desc": desc, "id": rid.split("/")[-1],
                        "click": click == "true", "x": (x1 + x2) // 2, "y": (y1 + y2) // 2,
                        "bounds": [x1, y1, x2, y2]})
        return els

    def focus(self):
        out = self.shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp' | head -2")
        m = re.search(r"u0 ([\w.]+)/([\w.$]+)", out)
        return {"package": m.group(1), "activity": m.group(2)} if m else {"raw": out.strip()}

    # ----- act -----
    def tap(self, x, y):
        return self.touch([{"actionType": 0, "x": x, "y": y}, {"actionType": 1, "x": x, "y": y}])

    def long_press(self, x, y, ms=800):
        return self.shell(f"input swipe {x} {y} {x} {y} {ms}")

    def swipe(self, x1, y1, x2, y2, ms=300, adb=False):
        if adb:
            return self.shell(f"input swipe {x1} {y1} {x2} {y2} {ms}")
        steps = 12
        pos = [{"actionType": 0, "x": x1, "y": y1}]
        for i in range(1, steps + 1):
            pos.append({"actionType": 2, "x": x1 + (x2 - x1) * i // steps, "y": y1 + (y2 - y1) * i // steps,
                        "nextPositionWaitTime": max(ms // steps, 5)})
        pos.append({"actionType": 1, "x": x2, "y": y2})
        return self.touch(pos)

    def scroll(self, direction, ms=300):
        w, h = self.size()
        cx, top, bot, left, right = w // 2, int(h * 0.3), int(h * 0.75), int(w * 0.15), int(w * 0.85)
        vec = {"down": (cx, bot, cx, top), "up": (cx, top, cx, bot),
               "left": (right, h // 2, left, h // 2), "right": (left, h // 2, right, h // 2)}[direction]
        return self.swipe(*vec, ms=ms)


# ---------- helpers ----------

def find(els, needle, exact=False, clickable_first=True):
    def hit(e):
        hay = (e["text"], e["desc"], e["id"])
        return needle in hay if exact else any(needle.lower() in s.lower() for s in hay if s)
    hits = [e for e in els if hit(e)]
    if clickable_first:
        hits.sort(key=lambda e: (not e["click"], e["i"]))
    return hits


def fmt_el(e):
    label = e["text"] or ""
    if e["desc"] and e["desc"] != label:
        label = f"{label} [desc:{e['desc']}]" if label else f"[desc:{e['desc']}]"
    if not label and e["id"]:
        label = f"#{e['id']}"
    return f"{e['i']:>3} {'*' if e['click'] else ' '} ({e['x']},{e['y']}) {label}"


def out(obj, as_json):
    if as_json or not isinstance(obj, str):
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        print(obj)


def resolve_pad(args):
    pad = args.pad or load_config().get("VMOS_PAD")
    if pad:
        return pad
    pads = call("infos", {"page": 1, "rows": 2})["data"]["pageData"]
    if len(pads) == 1:
        return pads[0]["padCode"]
    raise VmosError("several pads on this account — pass --pad <padCode> or set VMOS_PAD (see `devices`)")


def positive_seconds(value):
    seconds = int(value)
    if seconds <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return seconds


def verify_text(ph, value, timeout):
    """Observe only; never resend input when the accessibility tree is stale."""
    time.sleep(1.5)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if any(e["text"] == value for e in ph.ui()):
            return
        time.sleep(1)
    raise VmosError("input sent, but exact text was not observed in UI; take a `shot` and "
                    "check the field before retrying (text was not resent)")


def wait_app(ph, package, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        d = first(ph.api("listInstalledApp")["data"])
        for app in (d or {}).get("apps") or []:
            if app.get("packageName") == package:
                return app
        time.sleep(2)
    raise VmosError(f"{package!r} not observed in installed apps within {timeout}s; "
                    "installation may still be running — check its task or take a `shot`")


# ---------- commands ----------

def cmd_config(args):
    cfg = load_config()
    out({"cred_file": CRED_FILE, "cred_file_exists": os.path.exists(CRED_FILE),
         "VMOS_AK": (cfg["VMOS_AK"][:4] + "…") if cfg.get("VMOS_AK") else "missing",
         "VMOS_SK": "set" if cfg.get("VMOS_SK") else "missing",
         "VMOS_PAD": cfg.get("VMOS_PAD") or "(auto: only pad on account)",
         "shot_dir": SHOT_DIR}, True)


def cmd_devices(args):
    rows = call("infos", {"page": 1, "rows": 100})["data"]["pageData"]
    if args.json:
        return out(rows, True)
    for r in rows:
        print(f"{r['padCode']}  status={r.get('padStatus')}  type={r.get('padType')}  "
              f"android={r.get('imageVersion')}  grade={r.get('padGrade')}  adb={r.get('adbOpenStatus')}")


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--pad", default=argparse.SUPPRESS,
                        help="padCode (default: VMOS_PAD, else the only pad on the account)")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="raw JSON output")
    p = argparse.ArgumentParser(prog="vmos", description="Drive a VMOS Cloud phone via OpenAPI.", parents=[common])
    sub = p.add_subparsers(dest="cmd", required=True)
    _add = sub.add_parser
    sub.add_parser = lambda *a, **k: _add(*a, parents=[common], **k)

    sub.add_parser("config", help="show credential / default pad status")
    sub.add_parser("devices", help="list pads (padStatus 10 = running)")
    sub.add_parser("status", help="pad detail + foreground app + screen size")

    s = sub.add_parser("shot", help="screenshot → local jpg path")
    s.add_argument("-o", "--out")

    s = sub.add_parser("ui", help="list on-screen elements: idx *clickable (x,y) label")
    s.add_argument("--all", action="store_true", help="include unlabeled/offscreen nodes")
    s.add_argument("--find", help="only elements whose text/desc/id contains this")

    s = sub.add_parser("tap", help="tap X Y, or --text / --index from `ui`")
    s.add_argument("xy", nargs="*", type=int)
    s.add_argument("--text")
    s.add_argument("--exact", action="store_true")
    s.add_argument("--index", type=int)

    s = sub.add_parser("longpress")
    s.add_argument("x", type=int)
    s.add_argument("y", type=int)
    s.add_argument("--ms", type=int, default=800)

    s = sub.add_parser("swipe", help="swipe X1 Y1 X2 Y2")
    s.add_argument("coords", nargs=4, type=int)
    s.add_argument("--ms", type=int, default=300)
    s.add_argument("--adb", action="store_true", help="use `input swipe` instead of simulateTouch")

    s = sub.add_parser("scroll", help="scroll content: down = see what's below")
    s.add_argument("direction", choices=["down", "up", "left", "right"])
    s.add_argument("--times", type=int, default=1)

    s = sub.add_parser("text", help="type into the focused field (unicode OK)")
    s.add_argument("value")
    s.add_argument("--verify", action="store_true", help="wait for exact text in UI; never resend input")
    s.add_argument("--timeout", type=positive_seconds, default=20, help="verification polling budget (seconds)")

    s = sub.add_parser("key", help="back|home|enter|recent|delete|search|<keycode>")
    s.add_argument("name")

    s = sub.add_parser("launch", help="start app by package")
    s.add_argument("package")
    s = sub.add_parser("stop", help="force-stop app")
    s.add_argument("package")
    s = sub.add_parser("restart-app")
    s.add_argument("package")
    sub.add_parser("clean-home", help="kill app processes and return to launcher")
    s = sub.add_parser("open-url", help="open a URL / deep link via VIEW intent")
    s.add_argument("url")
    s.add_argument("--package", help="force a handler app, e.g. com.zhiliaoapp.musically")

    s = sub.add_parser("apps", help="installed apps")
    s.add_argument("--name")
    s = sub.add_parser("wait-app", help="wait until an exact package appears in installed apps")
    s.add_argument("package")
    s.add_argument("--timeout", type=positive_seconds, default=120)
    s = sub.add_parser("install", help="download APK from URL and auto-install (async)")
    s.add_argument("url")
    s.add_argument("--package")
    s = sub.add_parser("uninstall")
    s.add_argument("package")

    s = sub.add_parser("shell", help="run a shell command on the phone (output ≤2000 chars)")
    s.add_argument("command")
    s.add_argument("--timeout", type=int, default=60)

    s = sub.add_parser("wait", help="poll until text appears on screen")
    s.add_argument("text")
    s.add_argument("--timeout", type=int, default=20)

    s = sub.add_parser("task", help="async task detail (install/upload/restart…)")
    s.add_argument("task_id", type=int)

    s = sub.add_parser("api", help="raw OpenAPI call: api <name> '<json body>' (padCodes auto-added with --with-pad)")
    s.add_argument("name")
    s.add_argument("body", nargs="?", default="{}")
    s.add_argument("--get", action="store_true")
    s.add_argument("--with-pad", action="store_true")

    args = p.parse_args()
    args.pad = getattr(args, "pad", None)
    args.json = getattr(args, "json", False)
    try:
        run(args)
    except VmosError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def run(args):
    if args.cmd == "config":
        return cmd_config(args)
    if args.cmd == "devices":
        return cmd_devices(args)
    if args.cmd == "api":
        body = json.loads(args.body)
        if args.with_pad:
            body.setdefault("padCodes", [resolve_pad(args)])
        return out(call(args.name, body, "GET" if args.get else "POST"), True)

    ph = Phone(resolve_pad(args))
    c = args.cmd
    if c == "status":
        info = call("infos", {"page": 1, "rows": 10, "padCodes": [ph.pad]})["data"]["pageData"]
        w, h = ph.size()
        out({"pad": first(info), "screen": [w, h], "foreground": ph.focus()}, True)
    elif c == "shot":
        print(ph.screenshot(args.out))
    elif c == "ui":
        els = ph.ui(include_all=args.all)
        if args.find:
            els = find(els, args.find, clickable_first=False)
        if args.json:
            return out(els, True)
        print(f"# {len(els)} elements; * = clickable; tap with `tap X Y` or `tap --index N`")
        for e in els:
            print(fmt_el(e))
        if not els and not args.find:
            print("# empty tree — app likely uses custom-drawn views or is mid-transition; take a `shot`")
    elif c == "tap":
        if args.text or args.index is not None:
            els = ph.ui()
            if args.index is not None:
                hits = [e for e in els if e["i"] == args.index]
            else:
                hits = find(els, args.text, exact=True)
                if not hits and not args.exact:
                    hits = find(els, args.text)
            if not hits:
                raise VmosError(f"no on-screen element matches {args.text or args.index!r} — run `ui` or `shot`")
            e = hits[0]
            ph.tap(e["x"], e["y"])
            print(f"tapped {fmt_el(e).strip()}" + (f"  (+{len(hits) - 1} other matches)" if len(hits) > 1 else ""))
        elif len(args.xy) == 2:
            ph.tap(*args.xy)
            print(f"tapped ({args.xy[0]},{args.xy[1]})")
        else:
            raise VmosError("tap needs X Y, --text or --index")
    elif c == "longpress":
        ph.long_press(args.x, args.y, args.ms)
        print("ok")
    elif c == "swipe":
        ph.swipe(*args.coords, ms=args.ms, adb=args.adb)
        print("ok")
    elif c == "scroll":
        for i in range(args.times):
            ph.scroll(args.direction)
            if i + 1 < args.times:
                time.sleep(0.8)
        print("ok")
    elif c == "text":
        ph.api("inputText", {"text": args.value})
        if args.verify:
            verify_text(ph, args.value, args.timeout)
            print("input sent; exact text observed in UI (confirm target field if ambiguous)")
        else:
            print("ok (input sent; field contents not verified)")
    elif c == "key":
        code = KEYS.get(args.name.lower()) or (int(args.name) if args.name.isdigit() else None)
        if code is None:
            raise VmosError(f"unknown key {args.name!r}; known: {', '.join(KEYS)} or a numeric keycode")
        ph.shell(f"input keyevent {code}")
        print("ok")
    elif c in ("launch", "stop", "restart-app"):
        api = {"launch": "startApp", "stop": "stopApp", "restart-app": "restartApp"}[c]
        ph.api(api, {"pkgName": args.package})
        print("ok")
    elif c == "clean-home":
        ph.api("cleanAppHome")
        print("ok")
    elif c == "open-url":
        url = args.url.replace("'", "'\\''")
        pkg = f" {args.package}" if args.package else ""
        print(ph.shell(f"am start -a android.intent.action.VIEW -d '{url}'{pkg}").strip() or "ok")
    elif c == "apps":
        body = {"appName": args.name} if args.name else {}
        d = first(ph.api("listInstalledApp", body)["data"])
        apps = (d or {}).get("apps") or []
        if args.json:
            return out(apps, True)
        for a in apps:
            print(f"{a.get('packageName')}  {a.get('appName')}  v{a.get('versionName')}  state={a.get('appState')}")
    elif c == "wait-app":
        app = wait_app(ph, args.package, args.timeout)
        out(app, args.json)
    elif c == "install":
        body = {"url": args.url, "autoInstall": 1}
        if args.package:
            body["packageName"] = args.package
        out(ph.api("uploadFileV3", body)["data"], True)
        print("# async — check with `task <taskId>` or `wait-app <package>`", file=sys.stderr)
    elif c == "uninstall":
        out(call("uninstallApp", {"padCodeList": [ph.pad], "apkPackageList": [args.package]})["data"], True)
    elif c == "shell":
        print(ph.shell(args.command, timeout=args.timeout), end="")
    elif c == "wait":
        deadline = time.time() + args.timeout
        while time.time() < deadline:
            hits = find(ph.ui(), args.text)
            if hits:
                print(f"found {fmt_el(hits[0]).strip()}")
                return
            time.sleep(1)
        raise VmosError(f"{args.text!r} did not appear within {args.timeout}s")
    elif c == "task":
        out(call("padTaskDetail", {"taskIds": [args.task_id], "taskId": args.task_id})["data"], True)


if __name__ == "__main__":
    main()
