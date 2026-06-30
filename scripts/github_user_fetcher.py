"""
Fetches real public GitHub profiles for GitHub-linked candidates.

Usage:
    export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
    python scripts/fetch_github.py

Token needs no scopes, just a basic classic token, since we only read
public profile data.
"""

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise SystemExit(
        "GITHUB_TOKEN env var not set. Generate a classic token at "
        "github.com/settings/tokens (no scopes needed) and run:\n"
        "  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx"
    )

GITHUB_USERS = {
    "C01": "torvalds",
    "C02": "gaearon",
    "C03": "sindresorhus",
    "C05": "yyx990803",
    "C06": "addyosmani",
    "C10": "tj",
    "C12": "kentcdodds",
    "C15": "mojombo",
    "C20": "addyosmani",
}

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "sources" / "github"


def _headers() -> dict:
    return {
        "User-Agent": "eightfold-data-fetch",
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def fetch_user(username: str) -> dict:
    url = f"https://api.github.com/users/{username}"
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def fetch_repos(username: str) -> list:
    url = f"https://api.github.com/users/{username}/repos?per_page=10&sort=updated"
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for candidate_id, username in GITHUB_USERS.items():
        try:
            profile = fetch_user(username)
            time.sleep(1)
            repos = fetch_repos(username)
            languages = sorted({r["language"] for r in repos if r.get("language")})

            record = {
                "candidate_id": candidate_id,
                "login": profile.get("login"),
                "name": profile.get("name"),
                "bio": profile.get("bio"),
                "company": profile.get("company"),
                "location": profile.get("location"),
                "blog": profile.get("blog"),
                "html_url": profile.get("html_url"),
                "public_repos": profile.get("public_repos"),
                "followers": profile.get("followers"),
                "languages": languages,
                "repo_names": [r["name"] for r in repos[:5]],
            }

            out_path = OUT_DIR / f"{candidate_id}.json"
            out_path.write_text(json.dumps(record, indent=2))
            print(f"saved {candidate_id} -> {username}")
            time.sleep(1)
        except urllib.error.HTTPError as e:
            print(f"failed {candidate_id} ({username}): {e}")


if __name__ == "__main__":
    main()