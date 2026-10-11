"""서버와 모드팩 상태를 확인해 status.json 을 쓴다. GitHub Actions 가 15분마다 실행한다.

이 저장소와 Actions 로그는 공개이므로 서버 주소(SERVER_HOST 비밀값)를 절대 출력하거나 파일에 쓰지 않는다.
"""
import hashlib
import json
import os
import sys
import tomllib
import urllib.request
from datetime import datetime, timezone

HOST = os.environ["SERVER_HOST"]
PACK = f"http://{HOST}:{os.environ.get('PACK_PORT') or '8080'}"
UA = {"User-Agent": "theworld-guide-status"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.read()


def server():
    d = json.loads(get(f"https://api.mcsrvstat.us/3/{HOST}"))
    if not d.get("online"):
        return {"online": False}
    p = d.get("players", {})
    return {"online": True, "version": d.get("version"), "players": p.get("online", 0), "max": p.get("max", 0)}


def pack():
    meta = tomllib.loads(get(f"{PACK}/pack.toml").decode())
    index = get(f"{PACK}/index.toml")
    get(f"{PACK}/TheWorld.zip")
    # 팩이 덜 만들어졌거나 깨졌으면 index 해시가 pack.toml 과 다르다.
    ok = hashlib.sha256(index).hexdigest() == meta["index"]["hash"]
    mods = [f["file"].removeprefix("mods/").removesuffix(".pw.toml").removesuffix(".jar")
            for f in tomllib.loads(index.decode())["files"]]
    return {"ok": ok, "minecraft": meta["versions"]["minecraft"], "neoforge": meta["versions"]["neoforge"],
            "mods": sorted(mods), "hash": meta["index"]["hash"]}


def previous():
    owner, repo = os.environ["GITHUB_REPOSITORY"].split("/")
    try:
        return json.loads(get(f"https://{owner.lower()}.github.io/{repo}/status.json"))
    except Exception:
        return {}


def safe(fn, fallback):
    try:
        return fn()
    except Exception as e:
        print(f"{fn.__name__}: {type(e).__name__}")  # 메시지에는 주소가 들어갈 수 있어 종류만 출력
        return fallback


now = datetime.now(timezone.utc).isoformat(timespec="seconds")
prev = previous()
status = {"checked_at": now, "server": safe(server, {"online": False}), "pack": safe(pack, {"ok": False})}
p, old = status["pack"], prev.get("pack", {})
if p.get("hash"):
    p["changed_at"] = old.get("changed_at") if old.get("hash") == p["hash"] else now

with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(status, f, ensure_ascii=False, indent=1)
print("server online:", status["server"]["online"], "/ pack ok:", p["ok"])
