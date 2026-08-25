from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote, urlparse

import requests


class RemoteSourceError(RuntimeError):
    pass


def _allowed_hosts() -> set[str]:
    raw = os.getenv("AJC_ALLOWED_REMOTE_HOSTS", "")
    return {host.strip().lower() for host in raw.split(",") if host.strip()}


def _validate_https(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise RemoteSourceError("Only absolute HTTPS URLs are accepted")
    allowed = _allowed_hosts()
    if not allowed or parsed.hostname.lower() not in allowed:
        raise RemoteSourceError(f"Remote host is not allow-listed: {parsed.hostname}")
    return url


def download_export(url: str, destination: Path, *, headers: dict[str, str] | None = None) -> Path:
    """Download an explicitly configured export without following redirects."""
    _validate_https(url)
    response = requests.get(
        url,
        headers=headers or {},
        timeout=(5, 30),
        allow_redirects=False,
        stream=True,
    )
    if 300 <= response.status_code < 400:
        raise RemoteSourceError("Redirects are disabled for export downloads")
    response.raise_for_status()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    total = 0
    try:
        with temporary.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > 50 * 1024 * 1024:
                    raise RemoteSourceError("Remote export exceeds the public safety limit")
                handle.write(chunk)
        temporary.replace(destination)
    finally:
        response.close()
        if temporary.exists():
            temporary.unlink()
    return destination


def sync_configured_exports(destination_dir: Path) -> list[Path]:
    """Optional public connector shell. Exact production endpoints are intentionally absent."""
    downloaded: list[Path] = []

    quest_urls = [url.strip() for url in os.getenv("QUEST_EXPORT_URLS", "").split(",") if url.strip()]
    for index, url in enumerate(quest_urls, start=1):
        downloaded.append(download_export(url, destination_dir / f"quest_export_{index:02d}.csv"))

    nocrm_url = os.getenv("NOCRM_EXPORT_URL", "").strip()
    nocrm_key = os.getenv("NOCRM_API_KEY", "").strip()
    if nocrm_url:
        headers = {"X-API-KEY": nocrm_key} if nocrm_key else {}
        downloaded.append(download_export(nocrm_url, destination_dir / "nocrm_export.bin", headers=headers))

    between_url = os.getenv("BEETWEEN_EXPORT_URL", "").strip()
    between_token = os.getenv("BEETWEEN_BEARER_TOKEN", "").strip()
    if between_url:
        headers = {"Authorization": f"Bearer {between_token}"} if between_token else {}
        downloaded.append(download_export(between_url, destination_dir / "beetween_export.bin", headers=headers))

    return downloaded


def _graph_access_token() -> str:
    tenant_id = os.environ["MS_GRAPH_TENANT_ID"]
    client_id = os.environ["MS_GRAPH_CLIENT_ID"]
    client_secret = os.environ["MS_GRAPH_CLIENT_SECRET"]
    token_url = f"https://login.microsoftonline.com/{quote(tenant_id, safe='')}/oauth2/v2.0/token"
    response = requests.post(
        token_url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
        timeout=(5, 30),
        allow_redirects=False,
    )
    if 300 <= response.status_code < 400:
        raise RemoteSourceError("Redirects are disabled for Microsoft token requests")
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RemoteSourceError("Microsoft Graph did not return an access token")
    return token


def upload_file_to_onedrive(local_path: Path, remote_folder: str) -> None:
    """Optional sanitized equivalent of the historical OneDrive publication step."""
    user_principal = os.environ["MS_GRAPH_USER_PRINCIPAL_NAME"]
    token = _graph_access_token()
    remote = "/".join(part for part in [remote_folder.strip("/"), local_path.name] if part)
    url = (
        "https://graph.microsoft.com/v1.0/users/"
        f"{quote(user_principal, safe='@.')}/drive/root:/{quote(remote, safe='/')}:/content"
    )
    with local_path.open("rb") as handle:
        response = requests.put(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
            data=handle,
            timeout=(5, 60),
            allow_redirects=False,
        )
    if 300 <= response.status_code < 400:
        raise RemoteSourceError("Redirects are disabled for Microsoft Graph uploads")
    response.raise_for_status()
