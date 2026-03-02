import json
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastmcp import FastMCP

framework_mgmt = import_module("compliance_oracle.tools.framework_mgmt")
register_framework_tools = framework_mgmt.register_framework_tools


@pytest.mark.asyncio
async def test_get_guidance_returns_error_when_control_not_found() -> None:
    mcp = FastMCP("test-server")
    manager = MagicMock()
    manager.get_control_details = AsyncMock(return_value=None)

    with patch(
        "compliance_oracle.tools.framework_mgmt.FrameworkManager",
        return_value=manager,
    ):
        register_framework_tools(mcp)
        tool = cast(Any, await mcp.get_tool("get_guidance"))
        result = await tool.fn(control_id="PR.AC-99", framework="nist-csf-2.0")

    assert result["error"] == "Control PR.AC-99 not found in nist-csf-2.0"


@pytest.mark.asyncio
async def test_get_framework_gap_passes_all_arguments() -> None:
    mcp = FastMCP("test-server")
    mapper = MagicMock()
    expected = MagicMock()
    mapper.analyze_gap = AsyncMock(return_value=expected)

    with patch(
        "compliance_oracle.tools.framework_mgmt.FrameworkMapper",
        return_value=mapper,
    ):
        register_framework_tools(mcp)
        tool = cast(Any, await mcp.get_tool("get_framework_gap"))
        result = await tool.fn(
            current_framework="nist-csf-2.0",
            target_framework="nist-800-53-r5",
            use_documented_state=False,
            project_path="/tmp/project",
        )

    assert result is expected
    mapper.analyze_gap.assert_awaited_once_with(
        current_framework="nist-csf-2.0",
        target_framework="nist-800-53-r5",
        use_documented_state=False,
        project_path="/tmp/project",
    )


@pytest.mark.asyncio
async def test_manage_framework_list_action() -> None:
    mcp = FastMCP("test-server")
    manager = MagicMock()
    expected = {"action": "list", "status": "success"}

    with (
        patch(
            "compliance_oracle.tools.framework_mgmt.FrameworkManager",
            return_value=manager,
        ),
        patch(
            "compliance_oracle.tools.framework_mgmt._list_frameworks",
            new=AsyncMock(return_value=expected),
        ) as list_frameworks,
    ):
        register_framework_tools(mcp)
        tool = cast(Any, await mcp.get_tool("manage_framework"))
        result = await tool.fn(action="list")

    assert result == expected
    list_frameworks.assert_awaited_once_with(manager)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("action", "framework", "source", "helper_name", "expected"),
    [
        (
            "download",
            "nist-csf-2.0",
            "official",
            "_download_framework",
            {"action": "download", "status": "success"},
        ),
        (
            "update",
            "nist-csf-2.0",
            "official",
            "_update_framework",
            {"action": "update", "status": "success"},
        ),
        (
            "remove",
            "nist-csf-2.0",
            None,
            "_remove_framework",
            {"action": "remove", "status": "success"},
        ),
        (
            "validate",
            "nist-csf-2.0",
            None,
            "_validate_framework",
            {"action": "validate", "status": "success"},
        ),
    ],
)
async def test_manage_framework_dispatches_actions(
    action: str,
    framework: str,
    source: str | None,
    helper_name: str,
    expected: dict[str, str],
) -> None:
    mcp = FastMCP("test-server")
    manager = MagicMock()

    helper = AsyncMock(return_value=expected)
    with (
        patch(
            "compliance_oracle.tools.framework_mgmt.FrameworkManager",
            return_value=manager,
        ),
        patch(f"compliance_oracle.tools.framework_mgmt.{helper_name}", new=helper),
    ):
        register_framework_tools(mcp)
        tool = cast(Any, await mcp.get_tool("manage_framework"))
        result = await tool.fn(action=action, framework=framework, source=source)

    assert result == expected
    if action in {"download", "update"}:
        helper.assert_awaited_once_with(framework, source)
    else:
        helper.assert_awaited_once_with(framework, manager)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("action", "message"),
    [
        ("download", "framework parameter required for download action"),
        ("update", "framework parameter required for update action"),
        ("remove", "framework parameter required for remove action"),
        ("validate", "framework parameter required for validate action"),
    ],
)
async def test_manage_framework_requires_framework_for_specific_actions(
    action: str,
    message: str,
) -> None:
    mcp = FastMCP("test-server")

    with patch("compliance_oracle.tools.framework_mgmt.FrameworkManager"):
        register_framework_tools(mcp)
        tool = cast(Any, await mcp.get_tool("manage_framework"))
        result = await tool.fn(action=action)

    assert result == {"action": action, "status": "error", "message": message}


@pytest.mark.asyncio
async def test_manage_framework_rejects_unknown_action() -> None:
    mcp = FastMCP("test-server")

    with patch("compliance_oracle.tools.framework_mgmt.FrameworkManager"):
        register_framework_tools(mcp)
        tool = cast(Any, await mcp.get_tool("manage_framework"))
        result = await tool.fn(action="invalid-action")

    assert result["action"] == "invalid-action"
    assert result["status"] == "error"
    assert result["message"].startswith("Unknown action: invalid-action")


@pytest.mark.asyncio
async def test_list_frameworks_splits_installed_and_available() -> None:
    active = SimpleNamespace(
        id="nist-csf-2.0",
        name="CSF",
        version="2.0",
        control_count=106,
        status=SimpleNamespace(value="active"),
    )
    available = SimpleNamespace(
        id="nist-800-53-r5",
        name="800-53",
        version="5.1.1",
        control_count=1000,
        status=SimpleNamespace(value="available"),
    )
    manager = MagicMock()
    manager.list_frameworks = AsyncMock(return_value=[active, available])

    result = await cast(Any, framework_mgmt._list_frameworks)(manager)

    assert result["status"] == "success"
    assert result["total_installed"] == 1
    assert result["total_available"] == 1
    assert result["installed_frameworks"][0]["id"] == "nist-csf-2.0"
    assert result["available_frameworks"][0]["id"] == "nist-800-53-r5"


@pytest.mark.asyncio
async def test_download_framework_rejects_unknown_framework() -> None:
    result = await cast(Any, framework_mgmt._download_framework)("iso-27001")

    assert result["action"] == "download"
    assert result["status"] == "error"
    assert "not available" in result["message"]


@pytest.mark.asyncio
async def test_download_framework_success_writes_file(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    response = MagicMock()
    response.text = '{"response":{}}'
    response.raise_for_status = MagicMock()
    client = MagicMock()
    client.get = AsyncMock(return_value=response)

    client_cm = MagicMock()
    client_cm.__aenter__ = AsyncMock(return_value=client)
    client_cm.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)),
        patch("compliance_oracle.tools.framework_mgmt.httpx.AsyncClient", return_value=client_cm),
    ):
        result = await cast(Any, framework_mgmt._download_framework)("nist-csf-2.0")

    output_file = tmp_path / "data" / "frameworks" / "nist-csf-2.0.json"
    assert result["status"] == "success"
    assert result["path"] == str(output_file)
    assert output_file.exists()
    assert output_file.read_text() == '{"response":{}}'


@pytest.mark.asyncio
async def test_download_framework_handles_http_error(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    response = MagicMock()
    response.raise_for_status = MagicMock(side_effect=httpx.HTTPError("bad status"))
    client = MagicMock()
    client.get = AsyncMock(return_value=response)

    client_cm = MagicMock()
    client_cm.__aenter__ = AsyncMock(return_value=client)
    client_cm.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)),
        patch("compliance_oracle.tools.framework_mgmt.httpx.AsyncClient", return_value=client_cm),
    ):
        result = await cast(Any, framework_mgmt._download_framework)("nist-csf-2.0")

    assert result["status"] == "error"
    assert result["message"] == "Failed to download nist-csf-2.0: bad status"


@pytest.mark.asyncio
async def test_download_framework_handles_unexpected_error(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    client = MagicMock()
    client.get = AsyncMock(side_effect=RuntimeError("boom"))

    client_cm = MagicMock()
    client_cm.__aenter__ = AsyncMock(return_value=client)
    client_cm.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)),
        patch("compliance_oracle.tools.framework_mgmt.httpx.AsyncClient", return_value=client_cm),
    ):
        result = await cast(Any, framework_mgmt._download_framework)("nist-csf-2.0")

    assert result["status"] == "error"
    assert result["message"] == "Unexpected error downloading nist-csf-2.0: boom"


@pytest.mark.asyncio
async def test_update_framework_converts_download_result() -> None:
    with patch(
        "compliance_oracle.tools.framework_mgmt._download_framework",
        new=AsyncMock(
            return_value={
                "action": "download",
                "framework": "nist-csf-2.0",
                "status": "success",
                "message": "Framework nist-csf-2.0 downloaded successfully",
            }
        ),
    ):
        result = await cast(Any, framework_mgmt._update_framework)("nist-csf-2.0")

    assert result["action"] == "update"
    assert result["status"] == "success"
    assert result["message"] == "Framework nist-csf-2.0 updated successfully"


@pytest.mark.asyncio
async def test_remove_framework_not_installed(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
        result = await cast(Any, framework_mgmt._remove_framework)(
            "nist-csf-2.0", manager=MagicMock()
        )

    assert result == {
        "action": "remove",
        "framework": "nist-csf-2.0",
        "status": "error",
        "message": "Framework nist-csf-2.0 not installed",
    }


@pytest.mark.asyncio
async def test_remove_framework_success_clears_index(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    framework_dir = tmp_path / "data" / "frameworks"
    framework_dir.mkdir(parents=True)
    framework_file = framework_dir / "nist-csf-2.0.json"
    _ = framework_file.write_text("{}")
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    searcher = MagicMock()
    searcher.clear_index = AsyncMock(return_value=None)

    with (
        patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)),
        patch("compliance_oracle.tools.framework_mgmt.ControlSearcher", return_value=searcher),
    ):
        result = await cast(Any, framework_mgmt._remove_framework)(
            "nist-csf-2.0", manager=MagicMock()
        )

    assert result["status"] == "success"
    assert not framework_file.exists()
    searcher.clear_index.assert_awaited_once_with("nist-csf-2.0")


@pytest.mark.asyncio
async def test_remove_framework_handles_unexpected_error(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    framework_dir = tmp_path / "data" / "frameworks"
    framework_json_dir = framework_dir / "nist-csf-2.0.json"
    framework_json_dir.mkdir(parents=True)
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
        result = await cast(Any, framework_mgmt._remove_framework)(
            "nist-csf-2.0", manager=MagicMock()
        )

    assert result["status"] == "error"
    assert result["message"].startswith("Failed to remove nist-csf-2.0")


@pytest.mark.asyncio
async def test_validate_framework_not_found(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
        result = await cast(Any, framework_mgmt._validate_framework)(
            "nist-csf-2.0", manager=MagicMock()
        )

    assert result == {
        "action": "validate",
        "framework": "nist-csf-2.0",
        "status": "error",
        "message": "Framework nist-csf-2.0 not found",
    }


@pytest.mark.asyncio
async def test_validate_framework_returns_warning_for_empty_controls(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    framework_dir = tmp_path / "data" / "frameworks"
    framework_dir.mkdir(parents=True)
    framework_file = framework_dir / "nist-csf-2.0.json"
    _ = framework_file.write_text(json.dumps({"response": {"elements": {"elements": []}}}))
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    manager = MagicMock()
    manager._count_controls.return_value = 0

    with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
        result = await cast(Any, framework_mgmt._validate_framework)(
            "nist-csf-2.0", manager=manager
        )

    assert result["status"] == "warning"
    assert result["control_count"] == 0


@pytest.mark.asyncio
async def test_validate_framework_success(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    framework_dir = tmp_path / "data" / "frameworks"
    framework_dir.mkdir(parents=True)
    framework_file = framework_dir / "nist-csf-2.0.json"
    _ = framework_file.write_text(json.dumps({"response": {"elements": {"elements": [1]}}}))
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    manager = MagicMock()
    manager._count_controls.return_value = 1

    with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
        result = await cast(Any, framework_mgmt._validate_framework)(
            "nist-csf-2.0", manager=manager
        )

    assert result["status"] == "success"
    assert result["control_count"] == 1


@pytest.mark.asyncio
async def test_validate_framework_invalid_json(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    framework_dir = tmp_path / "data" / "frameworks"
    framework_dir.mkdir(parents=True)
    framework_file = framework_dir / "nist-csf-2.0.json"
    _ = framework_file.write_text("{not-json")
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
        result = await cast(Any, framework_mgmt._validate_framework)(
            "nist-csf-2.0", manager=MagicMock()
        )

    assert result["status"] == "error"
    assert "has invalid JSON" in result["message"]


@pytest.mark.asyncio
async def test_validate_framework_handles_unexpected_error(tmp_path: Path) -> None:
    module_file = tmp_path / "a" / "b" / "c" / "framework_mgmt.py"
    framework_dir = tmp_path / "data" / "frameworks"
    framework_dir.mkdir(parents=True)
    framework_file = framework_dir / "nist-csf-2.0.json"
    _ = framework_file.write_text(json.dumps({"response": {"elements": {"elements": [1]}}}))
    module_file.parent.mkdir(parents=True)
    _ = module_file.write_text("# test")

    manager = MagicMock()
    manager._count_controls.side_effect = RuntimeError("count failed")

    with patch("compliance_oracle.tools.framework_mgmt.__file__", str(module_file)):
        result = await cast(Any, framework_mgmt._validate_framework)(
            "nist-csf-2.0", manager=manager
        )

    assert result["status"] == "error"
    assert result["message"] == "Failed to validate nist-csf-2.0: count failed"
