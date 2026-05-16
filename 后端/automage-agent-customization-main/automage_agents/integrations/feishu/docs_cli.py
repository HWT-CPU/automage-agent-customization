from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeishuDocsFetchResult:
    ok: bool
    doc: str
    command: list[str]
    cache_path: str | None = None
    content: str | None = None
    raw: dict[str, Any] | None = None
    error: str | None = None
    returncode: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "doc": self.doc,
            "command": self.command,
            "cache_path": self.cache_path,
            "content": self.content,
            "raw": self.raw,
            "error": self.error,
            "returncode": self.returncode,
        }


@dataclass(slots=True)
class FeishuDocsCliClient:
    executable: str = "lark-cli"
    cache_dir: Path = Path("_cache/feishu_wiki")

    def fetch_doc(
        self,
        doc: str,
        doc_format: str = "markdown",
        detail: str = "simple",
        scope: str | None = None,
        keyword: str | None = None,
        start_block_id: str | None = None,
        end_block_id: str | None = None,
        max_depth: int | None = None,
        use_cache: bool = True,
    ) -> FeishuDocsFetchResult:
        command = self._build_fetch_command(
            doc=doc,
            doc_format=doc_format,
            detail=detail,
            scope=scope,
            keyword=keyword,
            start_block_id=start_block_id,
            end_block_id=end_block_id,
            max_depth=max_depth,
        )
        executable_command = self._resolve_command(command)
        try:
            process = subprocess.run(executable_command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        except FileNotFoundError as exc:
            return FeishuDocsFetchResult(
                ok=False,
                doc=doc,
                command=command,
                error=f"{self.executable} was not found. Install it with `npm install -g @larksuite/cli`. {exc}",
                returncode=1,
            )
        raw_output = process.stdout.strip() or process.stderr.strip()
        parsed = _parse_json(raw_output)
        if process.returncode != 0:
            return FeishuDocsFetchResult(
                ok=False,
                doc=doc,
                command=executable_command,
                raw=parsed,
                error=_extract_error(raw_output, parsed),
                returncode=process.returncode,
            )

        content = _extract_content(parsed, raw_output)
        cache_path = None
        if use_cache:
            cache_path = str(self._write_cache(doc, content, doc_format))
        return FeishuDocsFetchResult(
            ok=True,
            doc=doc,
            command=executable_command,
            cache_path=cache_path,
            content=content,
            raw=parsed,
            returncode=process.returncode,
        )

    def _build_fetch_command(
        self,
        doc: str,
        doc_format: str,
        detail: str,
        scope: str | None,
        keyword: str | None,
        start_block_id: str | None,
        end_block_id: str | None,
        max_depth: int | None,
    ) -> list[str]:
        command = [
            self.executable,
            "docs",
            "+fetch",
            "--api-version",
            "v2",
            "--doc",
            doc,
            "--doc-format",
            doc_format,
            "--detail",
            detail,
            "--format",
            "json",
        ]
        if scope:
            command.extend(["--scope", scope])
        if keyword:
            command.extend(["--keyword", keyword])
        if start_block_id:
            command.extend(["--start-block-id", start_block_id])
        if end_block_id:
            command.extend(["--end-block-id", end_block_id])
        if max_depth is not None:
            command.extend(["--max-depth", str(max_depth)])
        return command

    def _resolve_command(self, command: list[str]) -> list[str]:
        resolved = shutil.which(command[0])
        if not resolved:
            return command
        if resolved.lower().endswith(".ps1"):
            return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", resolved, *command[1:]]
        return [resolved, *command[1:]]

    def _write_cache(self, doc: str, content: str, doc_format: str) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        suffix = "md" if doc_format == "markdown" else "txt" if doc_format == "text" else "xml"
        safe_doc = "".join(character if character.isalnum() or character in {"-", "_"} else "_" for character in doc)[:120]
        path = self.cache_dir / f"{safe_doc}.{suffix}"
        path.write_text(content, encoding="utf-8")
        return path


def _parse_json(raw_output: str) -> dict[str, Any] | None:
    if not raw_output:
        return None
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return None


def _extract_content(parsed: dict[str, Any] | None, raw_output: str) -> str:
    if not parsed:
        return raw_output
    data = parsed.get("data", {})
    document = data.get("document", {}) if isinstance(data, dict) else {}
    content = document.get("content") if isinstance(document, dict) else None
    if isinstance(content, str):
        return content
    return raw_output


def _extract_error(raw_output: str, parsed: dict[str, Any] | None) -> str:
    if parsed and isinstance(parsed.get("error"), dict):
        error = parsed["error"]
        message = str(error.get("message") or error.get("type") or raw_output)
        hint = error.get("hint")
        if hint:
            return f"{message} Hint: {hint}"
        return message
    return raw_output or "lark-cli docs fetch failed"
