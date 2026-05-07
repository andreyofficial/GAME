"""
Auto-update from GitHub Releases for PyInstaller one-file builds (Windows / Linux).

Set env GAME_SKIP_UPDATE=1 to disable. Requires public repo or sufficient API rate limit.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.request

GITHUB_REPO = "andreyofficial/GAME"
RELEASES_LATEST = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
ASSET_WINDOWS = "GAME_WINDOWS.exe"
ASSET_LINUX = "GAME_LINUX"
USER_AGENT = "GAME-auto-updater"


def _parse_version_tuple(tag_or_version: str) -> tuple[int, ...]:
    s = (tag_or_version or "0").strip().lstrip("vV")
    parts: list[int] = []
    for chunk in s.split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:6])


def _remote_newer(remote_tag: str, current: str) -> bool:
    return _parse_version_tuple(remote_tag) > _parse_version_tuple(current)


def _target_asset_name() -> str:
    if platform.system() == "Windows":
        return ASSET_WINDOWS
    return ASSET_LINUX


def _download(url: str, dest_path: str) -> None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    tmp = dest_path + ".partial"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dest_path)


def _is_safe_release_asset(url: str, name: str) -> bool:
    if f"github.com/{GITHUB_REPO}/releases/download/" not in url:
        return False
    return name in (ASSET_WINDOWS, ASSET_LINUX)


def check_and_apply_update(current_version: str) -> bool:
    """
    If a newer release exists, download the matching asset and schedule replace + restart.
    Returns True if the current process should exit immediately (update staged).
    """
    if os.environ.get("GAME_SKIP_UPDATE"):
        return False
    if not getattr(sys, "frozen", False):
        return False

    try:
        req = urllib.request.Request(
            RELEASES_LATEST,
            headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as err:
        print("Update check failed:", err)
        return False

    tag = str(payload.get("tag_name", "v0"))
    if not _remote_newer(tag, current_version):
        return False

    want = _target_asset_name()
    asset_url = None
    for asset in payload.get("assets") or []:
        name = str(asset.get("name", ""))
        url = str(asset.get("browser_download_url", ""))
        if name == want and _is_safe_release_asset(url, name):
            asset_url = url
            break

    if not asset_url:
        print(f"Update: no asset named {want!r} on latest release {tag}.")
        return False

    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    current_exe = os.path.abspath(sys.executable)
    new_file = os.path.join(exe_dir, want + ".download")

    try:
        print(f"Downloading update {tag} ...")
        _download(asset_url, new_file)
    except (urllib.error.URLError, OSError, TimeoutError) as err:
        print("Update download failed:", err)
        return False

    if platform.system() == "Windows":
        # Replace current exe name (typically GAME.exe) with downloaded build.
        dst = current_exe
        bat_path = os.path.join(exe_dir, "_GAME_apply_update.bat")
        bat = (
            "@echo off\r\n"
            "timeout /t 2 /nobreak >nul\r\n"
            f'move /Y "{new_file}" "{dst}"\r\n'
            f'start "" "{dst}"\r\n'
            f"del \"%~f0\"\r\n"
        )
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat)
        subprocess.Popen(
            ["cmd", "/c", bat_path],
            cwd=exe_dir,
            close_fds=True,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        return True

    sh_path = os.path.join(exe_dir, "_GAME_apply_update.sh")
    sh = (
        "#!/bin/sh\n"
        "sleep 2\n"
        f'mv -f "{new_file}" "{current_exe}"\n'
        f'chmod +x "{current_exe}"\n'
        f'exec "{current_exe}"\n'
    )
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write(sh)
    os.chmod(sh_path, 0o755)
    subprocess.Popen(
        ["/bin/sh", sh_path],
        cwd=exe_dir,
        close_fds=True,
        start_new_session=True,
    )
    return True
