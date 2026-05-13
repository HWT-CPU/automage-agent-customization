from __future__ import annotations

from pathlib import Path


FORWARDER_PATH = Path("delivery/openclaw-bridge/automage_openclaw_forwarder.mjs")
README_PATH = Path("delivery/openclaw-bridge/README.md")
PLUGIN_PACKAGE_PATH = Path("delivery/openclaw-bridge/plugin/package.json")
PLUGIN_ENTRY_PATH = Path("delivery/openclaw-bridge/plugin/index.mjs")
PLUGIN_MANIFEST_PATH = Path("delivery/openclaw-bridge/plugin/openclaw.plugin.json")
GATEWAY_READY_SCRIPT_PATH = Path("scripts/check_real_openclaw_gateway_ready.py")
PLUGIN_TOOL_RUNTIME_SCRIPT_PATH = Path("scripts/check_openclaw_plugin_tool_runtime.py")


def test_openclaw_forwarder_delivery_files_exist() -> None:
    assert FORWARDER_PATH.exists()
    assert README_PATH.exists()
    assert PLUGIN_PACKAGE_PATH.exists()
    assert PLUGIN_ENTRY_PATH.exists()
    assert PLUGIN_MANIFEST_PATH.exists()
    assert GATEWAY_READY_SCRIPT_PATH.exists()
    assert PLUGIN_TOOL_RUNTIME_SCRIPT_PATH.exists()


def test_openclaw_forwarder_exports_expected_functions() -> None:
    source = FORWARDER_PATH.read_text(encoding="utf-8")
    assert "export function normalizeOpenClawMessage" in source
    assert "export async function forwardOpenClawEvent" in source
    assert "export async function handleOpenClawMessage" in source
    assert "/openclaw/events" in source
    assert "AUTOMAGE_OPENCLAW_BRIDGE_URL" in source


def test_openclaw_forwarder_does_not_embed_secrets() -> None:
    source = FORWARDER_PATH.read_text(encoding="utf-8")
    forbidden = ["OPENAI_API_KEY=", "CLOSEAI_API_KEY=", "api.closeai-asia.com", "Bearer sk-"]
    for token in forbidden:
        assert token not in source


def test_openclaw_forwarder_readme_documents_wsl2_smoke() -> None:
    content = README_PATH.read_text(encoding="utf-8")
    assert "node /mnt/d/Auto-mage2/delivery/openclaw-bridge/automage_openclaw_forwarder.mjs" in content
    assert "handleOpenClawMessage" in content
    assert "http://127.0.0.1:8000" in content


def test_openclaw_plugin_template_exports_common_lifecycle_names() -> None:
    source = PLUGIN_ENTRY_PATH.read_text(encoding="utf-8")
    assert "export async function onMessage" in source
    assert "export async function handleMessage" in source
    assert "export async function run" in source
    assert "export async function invoke" in source
    assert "export function register" in source
    assert "export async function activate" in source
    assert "api.registerTool" in source
    assert "automage_openclaw_event" in source
    assert "handleOpenClawMessage" in source


def test_openclaw_plugin_package_declares_openclaw_metadata() -> None:
    content = PLUGIN_PACKAGE_PATH.read_text(encoding="utf-8")
    assert '"name": "automage-openclaw-bridge"' in content
    assert '"type": "module"' in content
    assert '"openclaw"' in content
    assert '"entry": "./index.mjs"' in content
    assert '"extensions"' in content
    assert '"tools"' in PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8")
    assert '"automage_openclaw_event"' in PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8")


def test_gateway_ready_script_checks_skill_and_tool_contract() -> None:
    source = GATEWAY_READY_SCRIPT_PATH.read_text(encoding="utf-8")
    assert 'PLUGIN_ID = "automage-openclaw-bridge"' in source
    assert 'SKILL_NAME = "automage-knowledge"' in source
    assert 'TOOL_NAME = "automage_openclaw_event"' in source
    assert "必须调用 automage_openclaw_event 工具" in source
    assert "agent_tool_calls" in source
    assert "_find_tool_summary" in source
    assert '["skills", "info", SKILL_NAME]' in source
    assert "model_provider_balance_or_auth_blocked" in source


def test_plugin_tool_runtime_script_executes_registered_tool() -> None:
    source = PLUGIN_TOOL_RUNTIME_SCRIPT_PATH.read_text(encoding="utf-8")
    assert 'TOOL_NAME = "automage_openclaw_event"' in source
    assert "resolvePluginTools" in source
    assert "tool.execute" in source
    assert "AUTOMAGE_OPENCLAW_BRIDGE_URL" in source
