import os
import sys
import json
import time
import signal
import asyncio
import aiohttp

from urllib.parse import parse_qs, quote, unquote
from datetime import datetime, timezone

from utils.banner import show_banner

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"

MY_PROJECT = "Bakery Rush Miniapp"

BASE_URL = "https://zerolabnetwork.xyz/_serverFn"

TENANT_SLUG = "bakeryrushbot"

REF_CODE = "ref_6004380466"

FN_BOOTSTRAP = "a372d79872d5ac8b139ade5f5bc392a6cee2377595aafd94b3181fff8a9e530e"
FN_STATE = "31735fe2a578a743b52e9191d142ecc8532f415681a629482db72c3e3a978168"
FN_COMMUNITY = "34af145da5d0790e6c88b5ba3a267fadc6b21ae9f8271c3e6d2ef2e49e38b07b"
FN_USER = "f3249dd8c23677b8a179cd96490de1533883bef6d57b577ea5775cbf201b0ab0"
FN_START_AD = "87ef6ae8258444ecea5e8f2f582e74729b7fc2120b63cea7c81f8a7c0734ea72"
FN_CLAIM_AD = "58f3d23a5396a5e4c64cf8250b7edd386ff8ccfe5bf0f77eda05fa1a74285dfd"
FN_STORAGE_AD = "c0316c20c4c58a45c3c9971b8dde293c2650806396b86e7709ce6e4c1d1588c2"
FN_BAKE = "6ae4f1e53fe3c232b893ffd90487770b96a93263ffdb7ba2b4d14cfeb1025748"
FN_COLLECT = "875a376a7cd352939fb51711c38520c32371c306362013d1b5197e388a1ac648"
FN_SPIN = "f1a16efc6803b4837c6b1efe5c176e69f0837c02b7b20f3b70476d3189935a86"
FN_SCRATCH = "0208d25adb2a9ed04a9f1c65d250016d892419f97d7e6453a9cec9d38a5b6aaf"
FN_CHECKIN = "5aa45ef9d1f866d66a57758f3f60a74ed9b6c34e490f15197654aea70e240f5e"
FN_QUIZ = "b3744ffa0463d1cf9b7e52822f9a1a184bef1c834f1e49a992d69e67d69e2389"
FN_TASK = "1085531ad9ab92d7ee0141e6d765f3ac33f84239069f5dbf6021cfa323a0c922"
FN_TASKS = "b8f2b26d5518fba283b6f052bc9c97d93292dcb4294d26ee4d42b7bbba771b38"
FN_HUB = "60d252a4030b27c24d7c155cb71bd2b89354489d14a563fc0b9c460ae106c25f"
FN_CHECKIN_STATUS = "bcb7a23e66388e76c832536437cb1a871f8ffa6fd2ed9337a381403a57c0972a"
FN_PROVIDERS = "0921753aa4985dfc90a9c1f8b205889091c816d6bb6a2b924aedb78c632f71e0"

PURPOSE_REWARD = "reward"
PURPOSE_STORAGE = "storage_boost"

ENCODED = 10
ENCODED_LIST = 9
NUMBER = 0
PRIMITIVE = 1
SPECIAL = 2
SPECIAL_NULL = 0
SPECIAL_TRUE = 2
SPECIAL_FALSE = 3

NETWORK_FOR_KIND = {
    "adsgram_task": "adsgram",
    "adsgram": "adsgram",
    "monetag": "monetag",
    "onclicka": "onclicka",
    "custom": "custom",
    "direct_link": "direct_link",
    "ao_code": "ao_code",
}

CALL_ATTEMPTS = 3
CALL_RETRY_SECONDS = 4
ROUND_PAUSE_SECONDS = 2
RATE_LIMIT_PAUSE_SECONDS = 8
AD_PAUSE_SECONDS = 4
AD_SAFETY_ROUNDS = 30
AD_MAX_WAIT_SECONDS = 30
NAME_LIMIT = 18
NOTE_LIMIT = 30
ADDRESS_LIMIT = 16

BANNED_CODES = (
    91, 93, 124, 35, 33, 64, 36, 37, 94, 38, 42, 40, 41,
    45, 44, 58, 59, 39, 34, 96, 126, 43, 61, 60, 62, 63, 47, 92,
)
BANNED_CHARS = tuple(chr(code) for code in BANNED_CODES)

PAGE_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/152.0.0.0 Mobile Safari/537.36"
)

SERVERFN_ACCEPT = "application/json, application/x-ndjson, application/json"

LIMIT_WORDS = (
    "daily limit",
    "limit reached",
    "no ads left",
    "allowance",
)

ALREADY_WORDS = (
    "already claimed",
    "already collected",
    "already checked",
    "already completed",
    "already rewarded",
    "not ready",
)

AD_MISMATCH_WORDS = (
    "ad mismatch",
)

NOT_WATCHED_WORDS = (
    "watch the full ad",
    "watch the ad first",
    "watch the storage ad",
    "stay on the advertiser",
)

COOLDOWN_WORDS = (
    "next storage boost",
    "next question",
    "cooldown",
    "not ready",
)

AD_COOLDOWN_WORDS = (
    "please wait",
    "too fast",
    "slow down",
)

JOIN_WORDS = (
    "join the channel",
    "join every channel",
    "not a member",
    "join them all",
)

STORAGE_WORDS = (
    "storage must be",
    "storage is full",
    "not full enough",
)


def log_green(msg):
    print(f"{GREEN}{BOLD}{msg}{RESET}", flush=True)


def log_yellow(msg):
    print(f"{YELLOW}{BOLD}{msg}{RESET}", flush=True)


def log_red(msg):
    print(f"{RED}{BOLD}{msg}{RESET}", flush=True)


def signal_handler(sig, frame):
    print(flush=True)
    log_red("Script stopped by user")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def clean_text(value, fallback):
    if value is None:
        return str(fallback)
    text = str(value)
    for symbol in BANNED_CHARS:
        text = text.replace(symbol, " ")
    text = "".join(char for char in text if ord(char) < 128)
    text = " ".join(text.split())
    return text if text else str(fallback)


def shorten(value, fallback, limit):
    text = clean_text(value, fallback)
    if len(text) <= limit:
        return text
    cut = text[: limit + 1]
    space = cut.rfind(" ")
    return cut[:space].rstrip() if space > 0 else text[:limit].rstrip()


def unit_word(value, singular, plural):
    try:
        return singular if int(value) == 1 else plural
    except Exception:
        return plural


def number_of(mapping, key, fallback=0):
    try:
        value = mapping.get(key)
    except Exception:
        return fallback
    if value is None or value == "":
        return fallback
    try:
        return int(float(value))
    except Exception:
        return fallback


def number_float(mapping, key, fallback=0.0):
    try:
        value = mapping.get(key)
    except Exception:
        return fallback
    if value is None or value == "":
        return fallback
    try:
        return float(value)
    except Exception:
        return fallback


def format_amount(value):
    try:
        number = float(value)
    except Exception:
        return "0"
    if number != number or number == 0:
        return "0"
    text = f"{number:.4f}" if abs(number) >= 1 else f"{number:.8f}"
    text = text.rstrip("0").rstrip(".")
    return text or "0"


def encode_node(node, counter):
    if isinstance(node, dict):
        counter[0] += 1
        index = counter[0]
        keys = list(node.keys())
        return {
            "t": ENCODED,
            "i": index,
            "p": {
                "k": [{"t": PRIMITIVE, "s": key} for key in keys],
                "v": [encode_node(node[key], counter) for key in keys],
            },
            "o": 0,
        }
    if isinstance(node, (list, tuple)):
        counter[0] += 1
        return {
            "t": ENCODED_LIST,
            "i": counter[0],
            "a": [encode_node(item, counter) for item in node],
            "o": 0,
        }
    if isinstance(node, bool):
        return {"t": SPECIAL, "s": SPECIAL_TRUE if node else SPECIAL_FALSE}
    if isinstance(node, str):
        return {"t": PRIMITIVE, "s": node}
    if isinstance(node, (int, float)):
        return {"t": NUMBER, "s": node}
    return {"t": SPECIAL, "s": SPECIAL_NULL}


def build_request(fn_id, arguments):
    counter = [0]
    inner = encode_node({"data": arguments}, counter)
    return json.dumps({"t": inner, "f": 63, "m": []})


def decode_node(node, refs):
    if isinstance(node, list):
        return [decode_node(item, refs) for item in node]
    if not isinstance(node, dict):
        return node
    kind = node.get("t")
    if kind in (0, 1):
        return node.get("s")
    if kind == SPECIAL:
        marker = node.get("s")
        if marker == SPECIAL_TRUE:
            return True
        if marker == SPECIAL_FALSE:
            return False
        return None
    if kind == 3:
        try:
            return int(node.get("s"))
        except Exception:
            return 0
    if kind == 4:
        return refs.get(node.get("i"))
    if kind in (8, 9):
        return [decode_node(item, refs) for item in (node.get("a") or [])]
    if kind == 25:
        carrier = node.get("s")
        if isinstance(carrier, dict) and "message" in carrier:
            return {"__error": decode_node(carrier.get("message"), refs)}
        return None
    if kind in (10, 11):
        parent = node.get("p") or {}
        keys = parent.get("k") or []
        values = parent.get("v") or []
        result = {}
        for position, key in enumerate(keys):
            name = decode_node(key, refs)
            value = decode_node(values[position], refs) if position < len(values) else None
            result[str(name)] = value
        if node.get("i") is not None:
            refs[node["i"]] = result
        return result
    return None


def parse_payload(body):
    if not body:
        return {}
    stripped = body.strip()
    if not stripped.startswith("{"):
        return {}
    try:
        loaded = json.loads(stripped)
    except Exception:
        return {}
    if not isinstance(loaded, dict):
        return {}
    try:
        return decode_node(loaded, {})
    except Exception:
        return {}


def result_of(payload):
    value = payload.get("result") if isinstance(payload, dict) else None
    return value if isinstance(value, dict) else {}


def result_list(payload):
    value = payload.get("result") if isinstance(payload, dict) else None
    return value if isinstance(value, list) else []


def api_error(payload):
    if not isinstance(payload, dict):
        return ""
    value = payload.get("error")
    if isinstance(value, str) and value:
        return value
    if isinstance(value, dict):
        inner = value.get("__error")
        if inner:
            return str(inner)
    for key in ("message",):
        if payload.get(key):
            return str(payload[key])
    return ""


def error_key(payload):
    return clean_text(api_error(payload), "").lower()


def matches(key, words):
    return any(word in key for word in words)


def load_config():
    defaults = {
        "settings": {
            "sleep_seconds": 3600,
        }
    }
    if not os.path.exists("config.json"):
        return defaults
    try:
        with open("config.json") as handle:
            loaded = json.load(handle)
    except Exception:
        return defaults
    settings = loaded.get("settings")
    if not isinstance(settings, dict):
        return defaults
    merged = dict(defaults["settings"])
    merged.update(settings)
    return {"settings": merged}


def load_lines(filename, required):
    if not os.path.exists(filename):
        if required:
            log_red(f"File {clean_text(filename, 'data.txt')} was not found")
            sys.exit(1)
        return []
    lines = [line.strip() for line in open(filename).readlines() if line.strip()]
    if required and not lines:
        log_red("File data.txt is empty and holds no initData string")
        sys.exit(1)
    return lines


def parse_init_data(line):
    value = line.strip()
    if "|" in value:
        value = value.rsplit("|", 1)[0].strip()
    if "tgWebAppData=" in value:
        value = value.split("tgWebAppData=", 1)[1]
        value = value.split("&tgWebAppVersion")[0].split("&tgWebAppPlatform")[0]
        value = unquote(value)
    fields = parse_qs(value, keep_blank_values=True)
    raw_user = (fields.get("user") or [""])[0]
    if not raw_user:
        return None
    try:
        profile = json.loads(raw_user)
    except Exception:
        try:
            profile = json.loads(unquote(raw_user))
        except Exception:
            return None
    if not isinstance(profile, dict) or not profile.get("id"):
        return None
    return {
        "initData": value,
        "id": str(profile.get("id")),
        "username": str(profile.get("username") or ""),
        "firstName": str(profile.get("first_name") or ""),
        "lastName": str(profile.get("last_name") or ""),
        "startParam": str((fields.get("start_param") or [""])[0]),
        "userId": "",
        "tenantId": "",
    }


def display_name(account):
    for candidate in (account.get("firstName"), account.get("username")):
        if candidate:
            return candidate
    return "account"


def normalize_proxy(proxy_line):
    if not proxy_line:
        return None
    value = proxy_line.strip()
    if "://" in value:
        return value
    parts = value.split(":")
    if len(parts) == 4:
        host, port, user, password = parts
        return f"http://{user}:{password}@{host}:{port}"
    if len(parts) == 3:
        host, port, user = parts
        return f"http://{user}@{host}:{port}"
    return f"http://{value}"


def mask_proxy(proxy_url):
    try:
        value = proxy_url.split("://")[-1]
        after_at = value.split("@")[-1]
        host_part = after_at.split(":")[0]
        port_part = after_at.split(":")[1] if ":" in after_at else ""
        octets = host_part.split(".")
        if len(octets) == 4:
            masked_host = f"{octets[0]}*****{octets[3]}"
        elif len(host_part) > 4:
            masked_host = f"{host_part[:2]}*****{host_part[-2:]}"
        else:
            masked_host = "***"
        suffix = f":{port_part}" if port_part else ""
        return f"http://user:pass@{masked_host}{suffix}"
    except Exception:
        return "http://user:pass@***:***"


def countdown(seconds, label):
    total = int(seconds)
    if total < 1:
        return
    line = ""
    for remaining in range(total, 0, -1):
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        rest = remaining % 60
        line = f"{clean_text(label, 'item')} {hours:02d}:{minutes:02d}:{rest:02d}"
        print(f"\r{YELLOW}{BOLD}{line}{RESET}", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * (len(line) + 6) + "\r", end="", flush=True)


async def call_fn(session, proxy, fn_id, arguments, method, account=None):
    headers = {
        "accept": SERVERFN_ACCEPT,
        "origin": "https://zerolabnetwork.xyz",
        "referer": "https://zerolabnetwork.xyz/app/" + TENANT_SLUG,
        "user-agent": PAGE_AGENT,
        "x-tsr-serverfn": "true",
    }
    if account and account.get("initData"):
        headers["x-tg-init-data"] = account["initData"]
    url = BASE_URL + "/" + fn_id
    body = None
    if method == "POST":
        headers["content-type"] = "application/json"
        body = build_request(fn_id, arguments)
    else:
        query = quote(build_request(fn_id, arguments))
        url = url + "?payload=" + query
    last_status = 0
    last_body = ""
    for attempt in range(1, CALL_ATTEMPTS + 1):
        pause = CALL_RETRY_SECONDS * attempt
        try:
            request = session.request(
                method,
                url,
                data=body,
                headers=headers,
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=40),
            )
            async with request as response:
                last_status = response.status
                last_body = await response.text()
                if response.status < 500 and response.status != 429:
                    return last_status, last_body
                if response.status == 429:
                    pause = RATE_LIMIT_PAUSE_SECONDS * attempt
        except Exception:
            last_status = 0
            last_body = ""
        if attempt < CALL_ATTEMPTS:
            countdown(pause, "Retry in")


async def sign_in(session, proxy, account):
    status, body = await call_fn(
        session, proxy, FN_BOOTSTRAP,
        {
            "tenantSlug": TENANT_SLUG,
            "initData": account["initData"],
            "previewTgId": None,
            "referrerTgId": None,
            "deviceId": "",
            "fingerprint": "",
        }, "POST", account)
    payload = result_of(parse_payload(body))
    tenant = payload.get("tenant") or {}
    user = payload.get("user") or {}
    if status != 200 or not tenant or not user:
        return False
    account["userId"] = str(user.get("id") or "")
    account["tenantId"] = str(user.get("tenant_id") or tenant.get("id") or "")
    return bool(account["userId"])


async def fetch_state(session, proxy, account):
    status, body = await call_fn(session, proxy, FN_STATE,
                                 {"userId": account["userId"]}, "POST", account)
    payload = parse_payload(body)
    if status == 200 and result_of(payload):
        return result_of(payload)
    status, body = await call_fn(session, proxy, FN_USER,
                                 {"userId": account["userId"],
                                  "tenantId": account["tenantId"]}, "GET", account)
    payload = parse_payload(body)
    if status == 200 and result_of(payload):
        return result_of(payload)
    return {}


def wait_from_message(payload, fallback):
    text = api_error(payload).lower()
    digits = ""
    for char in text:
        if char.isdigit():
            digits += char
        elif digits:
            break
    if digits:
        value = int(digits)
        if 1 <= value <= AD_MAX_WAIT_SECONDS:
            return value
    return fallback


def wait_seconds(payload, fallback):
    value = number_of(payload, "minSeconds", fallback)
    if value < 1:
        value = fallback
    if value > AD_MAX_WAIT_SECONDS:
        value = AD_MAX_WAIT_SECONDS
    return value


async def run_community(session, proxy, account):
    status, body = await call_fn(session, proxy, FN_COMMUNITY,
                                 {"userId": account["userId"]}, "POST", account)
    payload = result_of(parse_payload(body))
    if status != 200 or not payload:
        log_red("Community membership could not be checked with the server")
        return
    if payload.get("ok"):
        log_green("Community membership is confirmed on this account")
        return
    log_yellow("Community membership still needs a real channel join")


async def run_bake(session, proxy, account, state):
    status, body = await call_fn(session, proxy, FN_BAKE,
                                 {"userId": account["userId"]}, "POST", account)
    payload = parse_payload(body)
    result = result_of(payload)
    if status == 200 and result:
        if result.get("started"):
            log_green("Bake cycle was started on this account")
            return
        amount = number_float(result, "collected", 0.0)
        if amount > 0:
            state["balance"] = number_float(result, "balance", state.get("balance", 0.0))
            log_green(f"Bake cycle credited {clean_text(format_amount(amount), 0)} CRMB")
            return
        wait = number_of(result, "remaining_seconds", 0)
        minutes = wait // 60 if wait > 0 else 0
        log_yellow(f"The bake cycle is still filling and the server reports "
                   f"{clean_text(minutes, 0)} {unit_word(minutes, 'minute', 'minutes')} left")
        return
    key = error_key(payload)
    if matches(key, STORAGE_WORDS):
        log_yellow("Bake storage is not full enough to collect yet")
        return
    note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
    log_red(f"Bake cycle failed because {clean_text(note, 'refused')}")


async def run_storage(session, proxy, account, state):
    status, body = await call_fn(
        session, proxy, FN_START_AD,
        {"userId": account["userId"], "providerId": None, "purpose": PURPOSE_STORAGE},
        "POST", account)
    started = result_of(parse_payload(body))
    session_id = started.get("sessionId") if started else None
    if status != 200 or not session_id:
        key = error_key(parse_payload(body))
        if matches(key, COOLDOWN_WORDS):
            note = shorten(api_error(parse_payload(body)), "the server refused it",
                           NOTE_LIMIT)
            log_yellow(f"The storage boost is not ready yet and the server reports "
                       f"{clean_text(note, 'refused')}")
            return
        note = shorten(api_error(parse_payload(body)), "the server refused it", NOTE_LIMIT)
        log_red(f"Storage boost failed because {clean_text(note, 'refused')}")
        return
    countdown(wait_seconds(started, 8), "Storage ad in")
    status, body = await call_fn(session, proxy, FN_STORAGE_AD,
                                 {"userId": account["userId"], "sessionId": session_id},
                                 "POST", account)
    payload = parse_payload(body)
    result = result_of(payload)
    if status == 200 and result:
        added = number_of(result, "added_hours", 0)
        cap = number_of(result, "cap_hours", 0)
        left = number_of(result, "extends_left", 0)
        state["cap_hours"] = cap
        log_green(f"Storage boost added {clean_text(added, 0)} "
                  f"{unit_word(added, 'hour', 'hours')} and storage is now "
                  f"{clean_text(cap, 0)} {unit_word(cap, 'hour', 'hours')}")
        log_yellow(f"Storage boosts left on this account {clean_text(left, 0)}")
        return
    key = error_key(payload)
    if matches(key, COOLDOWN_WORDS):
        note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
        log_yellow(f"The storage boost is not ready yet and the server reports "
                   f"{clean_text(note, 'refused')}")
        return
    if matches(key, STORAGE_WORDS) or matches(key, NOT_WATCHED_WORDS):
        log_yellow("The storage ad was not confirmed by the server")
        return
    note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
    log_red(f"Storage boost failed because {clean_text(note, 'refused')}")


async def fetch_providers(session, proxy, account):
    status, body = await call_fn(session, proxy, FN_PROVIDERS,
                                 {"userId": account["userId"],
                                  "tenantId": account["tenantId"]}, "GET", account)
    payload = parse_payload(body)
    items = result_list(payload)
    providers = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("active") is False:
            continue
        provider_id = item.get("id")
        if not provider_id:
            continue
        providers.append({
            "id": str(provider_id),
            "kind": str(item.get("kind") or ""),
            "label": str(item.get("label") or ""),
            "reward": number_float(item, "reward_tokens", 0.0),
            "cap": number_of(item, "daily_cap", 0),
        })
    return providers


def network_for(kind):
    return NETWORK_FOR_KIND.get(kind, kind)


async def run_ads(session, proxy, account, state):
    providers = await fetch_providers(session, proxy, account)
    if not providers:
        log_yellow("No rewarded ad was offered to this account")
        return
    blocked = 0
    for provider in providers:
        label = shorten(provider["label"], "provider", NAME_LIMIT)
        network = network_for(provider["kind"])
        for _ in range(AD_SAFETY_ROUNDS):
            status, body = await call_fn(
                session, proxy, FN_START_AD,
                {"userId": account["userId"], "providerId": provider["id"],
                 "purpose": PURPOSE_REWARD},
                "POST", account)
            started = result_of(parse_payload(body))
            session_id = started.get("sessionId") if started else None
            if status != 200 or not session_id:
                key = error_key(parse_payload(body))
                if matches(key, AD_COOLDOWN_WORDS):
                    countdown(wait_from_message(parse_payload(body), AD_PAUSE_SECONDS),
                              "Ad cooldown")
                    continue
                if matches(key, LIMIT_WORDS):
                    blocked += 1
                    log_yellow(f"Ad allowance for {clean_text(label, 'provider')} "
                               "was used up")
                else:
                    note = shorten(api_error(parse_payload(body)),
                                   "the server refused it", NOTE_LIMIT)
                    log_red(f"Ad start failed for {clean_text(label, 'provider')} "
                            f"because {clean_text(note, 'refused')}")
                break
            countdown(wait_seconds(started, 8), "Ad in")
            status, body = await call_fn(
                session, proxy, FN_CLAIM_AD,
                {"userId": account["userId"], "network": network,
                 "providerId": provider["id"], "sessionId": session_id},
                "POST", account)
            payload = parse_payload(body)
            result = result_of(payload)
            if status == 200 and result:
                reward = number_float(result, "reward", 0.0)
                balance = number_float(result, "balance", state.get("balance", 0.0))
                used = number_of(result, "used", 0)
                limit = number_of(result, "limit", 0)
                state["balance"] = balance
                log_green(f"Ad reward from {clean_text(label, 'provider')} credited "
                          f"{clean_text(format_amount(reward), 0)} CRMB")
                log_yellow(f"Ad counter now {clean_text(used, 0)} of "
                           f"{clean_text(limit, 0)} on this account")
                await asyncio.sleep(AD_PAUSE_SECONDS)
                continue
            key = error_key(payload)
            if matches(key, LIMIT_WORDS) or matches(key, AD_MISMATCH_WORDS):
                blocked += 1
                log_yellow(f"Ad allowance for {clean_text(label, 'provider')} "
                           "was used up")
                break
            if matches(key, NOT_WATCHED_WORDS):
                log_yellow(f"The ad from {clean_text(label, 'provider')} "
                           "was not confirmed by the server")
                break
            note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
            log_red(f"Ad claim failed for {clean_text(label, 'provider')} "
                    f"because {clean_text(note, 'refused')}")
            break
    if blocked:
        log_yellow(f"Ad allowance was used up for {clean_text(blocked, 0)} "
                   f"{unit_word(blocked, 'provider', 'providers')}")


async def run_spin(session, proxy, account, state):
    status, body = await call_fn(session, proxy, FN_SPIN,
                                 {"userId": account["userId"]}, "POST", account)
    payload = parse_payload(body)
    result = result_of(payload)
    if status == 200 and result.get("ok") is True:
        amount = number_float(result, "amount", 0.0)
        state["balance"] = number_float(result, "balance", state.get("balance", 0.0))
        log_green(f"Wheel spin credited {clean_text(format_amount(amount), 0)} CRMB")
        return
    key = error_key(payload)
    if result.get("ok") is False or matches(key, COOLDOWN_WORDS) or matches(key, ALREADY_WORDS):
        credits = number_of(result, "spin_credits", 0)
        log_yellow(f"The wheel spin is not ready on this account and the spin "
                   f"counter stands at {clean_text(credits, 0)}")
        return
    note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
    log_red(f"Wheel spin failed because {clean_text(note, 'refused')}")


async def run_scratch(session, proxy, account, state):
    status, body = await call_fn(session, proxy, FN_SCRATCH,
                                 {"userId": account["userId"]}, "POST", account)
    payload = parse_payload(body)
    result = result_of(payload)
    if status == 200 and result.get("ok") is True:
        amount = number_float(result, "amount", 0.0)
        state["balance"] = number_float(result, "balance", state.get("balance", 0.0))
        log_green(f"Scratch card credited {clean_text(format_amount(amount), 0)} CRMB")
        return
    key = error_key(payload)
    if result.get("ok") is False or matches(key, COOLDOWN_WORDS) or matches(key, ALREADY_WORDS):
        log_yellow("The scratch card is not ready on this account yet")
        return
    note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
    log_red(f"Scratch card failed because {clean_text(note, 'refused')}")


async def run_checkin(session, proxy, account, state):
    status, body = await call_fn(session, proxy, FN_HUB,
                                 {"userId": account["userId"]}, "POST", account)
    hub = result_of(parse_payload(body))
    checkin = hub.get("checkin") if isinstance(hub, dict) else None
    if not isinstance(checkin, dict):
        log_yellow("The daily protocol state could not be read from the server")
        return
    status, body = await call_fn(session, proxy, FN_CHECKIN,
                                 {"userId": account["userId"]}, "POST", account)
    payload = parse_payload(body)
    result = result_of(payload)
    if status == 200 and result.get("ok") is True:
        amount = number_float(result, "amount", 0.0)
        day = number_of(result, "day", 0)
        state["balance"] = number_float(result, "balance", state.get("balance", 0.0))
        log_green(f"Daily protocol reward credited "
                  f"{clean_text(format_amount(amount), 0)} CRMB")
        log_yellow(f"Daily protocol streak is now at day {clean_text(day, 0)}")
        return
    key = error_key(payload)
    if result.get("ok") is False or matches(key, ALREADY_WORDS) or matches(key, LIMIT_WORDS):
        streak = number_of(checkin, "streak", 0)
        log_yellow("The daily protocol reward was already collected today")
        log_yellow(f"The daily protocol streak stands at day {clean_text(streak, 0)}")
        return
    note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
    log_red(f"Daily protocol reward failed because {clean_text(note, 'refused')}")


async def run_quiz(session, proxy, account, state):
    status, body = await call_fn(session, proxy, FN_HUB,
                                 {"userId": account["userId"]}, "POST", account)
    hub = result_of(parse_payload(body))
    quiz = hub.get("quiz") if isinstance(hub, dict) else None
    if not isinstance(quiz, dict):
        log_yellow("The knowledge round could not be read from the server")
        return
    question = quiz.get("question") or {}
    options = question.get("options") if isinstance(question, dict) else None
    if not isinstance(options, list) or not options:
        log_yellow("The knowledge round was already answered on this account")
        return
    status, body = await call_fn(session, proxy, FN_QUIZ,
                                 {"userId": account["userId"], "choice": 0}, "POST", account)
    payload = parse_payload(body)
    result = result_of(payload)
    if status == 200 and result.get("ok") is True:
        streak = number_of(result, "streak", 0)
        if result.get("correct"):
            amount = number_float(result, "amount", 0.0)
            state["balance"] = number_float(result, "balance",
                                            state.get("balance", 0.0))
            log_green(f"Knowledge round credited "
                      f"{clean_text(format_amount(amount), 0)} CRMB")
            log_yellow(f"Knowledge streak is now {clean_text(streak, 0)} "
                       f"{unit_word(streak, 'answer', 'answers')}")
        else:
            log_yellow("The knowledge round answer was wrong and the streak reset")
        return
    key = error_key(payload)
    if result.get("ok") is False or matches(key, COOLDOWN_WORDS) or matches(key, ALREADY_WORDS):
        log_yellow("The knowledge round is not ready on this account yet")
        return
    note = shorten(api_error(payload), "the server refused it", NOTE_LIMIT)
    log_red(f"Knowledge round failed because {clean_text(note, 'refused')}")


async def run_tasks(session, proxy, account, state):
    status, body = await call_fn(session, proxy, FN_TASKS,
                                 {"userId": account["userId"],
                                  "tenantId": account["tenantId"]}, "GET", account)
    payload = parse_payload(body)
    tasks = result_of(payload).get("tasks")
    if not isinstance(tasks, list) or not tasks:
        log_yellow("No community task was offered to this account")
        return
    claimed = 0
    pending = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_id = task.get("id")
        if not task_id:
            continue
        title = shorten(task.get("title"), "task", NAME_LIMIT)
        status, body = await call_fn(
            session, proxy, FN_TASK,
            {"userId": account["userId"], "taskId": str(task_id), "isGlobal": False},
            "POST", account)
        claim = parse_payload(body)
        result = result_of(claim)
        if status == 200 and result:
            amount = number_float(result, "reward", 0.0)
            state["balance"] = number_float(result, "balance",
                                            state.get("balance", 0.0))
            claimed += 1
            log_green(f"Task reward from {clean_text(title, 'task')} credited "
                      f"{clean_text(format_amount(amount), 0)} CRMB")
            continue
        key = error_key(claim)
        if matches(key, JOIN_WORDS):
            pending += 1
            log_yellow(f"Task {clean_text(title, 'task')} still needs a real "
                       "channel join")
            continue
        if matches(key, ALREADY_WORDS) or matches(key, LIMIT_WORDS):
            log_yellow(f"Task {clean_text(title, 'task')} was already rewarded")
            continue
        note = shorten(api_error(claim), "the server refused it", NOTE_LIMIT)
        log_red(f"Task {clean_text(title, 'task')} failed because "
                f"{clean_text(note, 'refused')}")
    if claimed:
        log_green(f"Task hub credited {clean_text(claimed, 0)} "
                  f"{unit_word(claimed, 'task', 'tasks')} on this account")
    if pending:
        log_yellow(f"Task hub still waits on {clean_text(pending, 0)} "
                   f"{unit_word(pending, 'join', 'joins')} from this account")


async def run_referral(account, state):
    count = number_of(state, "referral_count", 0)
    log_yellow(f"Referral friends on this account {clean_text(count, 0)} "
               f"{unit_word(count, 'friend', 'friends')}")
    log_yellow("Invite link https://t.me/BakeryRushBot?startapp="
               f"{clean_text(REF_CODE, 'code')}")


async def process_account(line, proxy, index):
    account = parse_init_data(line)
    if not account:
        log_red(f"Credential line {clean_text(index, 1)} is not valid initData")
        return

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        if not await sign_in(session, proxy, account):
            log_red(f"Sign in failed for account number {clean_text(index, 1)}")
            return

        state = await fetch_state(session, proxy, account)
        if not state:
            log_red(f"Account state could not be read for account number "
                    f"{clean_text(index, 1)}")
            return

        name = shorten(display_name(account), "account", NAME_LIMIT)
        balance = number_float(state, "balance", 0.0)
        log_green(f"Signed in {clean_text(name, 'account')} with "
                  f"{clean_text(format_amount(balance), 0)} CRMB")

        await run_community(session, proxy, account)
        await run_checkin(session, proxy, account, state)
        await run_tasks(session, proxy, account, state)
        await run_bake(session, proxy, account, state)
        await run_storage(session, proxy, account, state)
        await run_ads(session, proxy, account, state)
        await run_spin(session, proxy, account, state)
        await run_scratch(session, proxy, account, state)
        await run_quiz(session, proxy, account, state)

        closing = await fetch_state(session, proxy, account)
        if closing:
            balance = number_float(closing, "balance", balance)
        log_yellow(f"Closing balance on this account "
                   f"{clean_text(format_amount(balance), 0)} CRMB")


async def main_async(accounts, proxies, sleep_secs):
    cycle = 1
    while True:
        log_yellow(f"Starting automation cycle number {clean_text(cycle, 0)}")

        for index, line in enumerate(accounts):
            if index > 0:
                print()

            proxy_line = proxies[index % len(proxies)] if proxies else None
            proxy_url = normalize_proxy(proxy_line) if proxy_line else None
            if proxy_url:
                log_yellow(f"Using proxy {mask_proxy(proxy_url)}")

            await process_account(line, proxy_url, index + 1)
            countdown(ROUND_PAUSE_SECONDS, "Next account in")

        log_yellow(f"Automation cycle number {clean_text(cycle, 0)} is complete")
        cycle += 1
        countdown(sleep_secs, "Next cycle starts in")
        show_banner(MY_PROJECT)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass

    show_banner(MY_PROJECT)

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    settings = load_config().get("settings", {})
    accounts = load_lines("data.txt", True)
    proxies = load_lines("proxy.txt", False)
    asyncio.run(main_async(accounts, proxies, settings["sleep_seconds"]))


if __name__ == "__main__":
    main()
