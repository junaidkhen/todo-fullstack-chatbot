"""Unit tests for Gemini function calling tool declarations.

These tests verify:
- Tool declarations conform to Gemini SDK schema (SC-001)
- All tools have user_id as required parameter (SC-002, FR-002)
- Parameter types and schemas match specification
- Tool return structure validation
"""

import pytest
from src.gemini.tools import get_task_tools


class TestGeminiToolDeclarations:
    """Test suite for Gemini tool declarations."""

    # T036: Test get_task_tools returns valid Tool object with exactly 5 declarations
    def test_get_task_tools_returns_tool_object(self):
        """Tool object should be returned with proper structure."""
        tool = get_task_tools()
        assert tool is not None
        assert hasattr(tool, "function_declarations")

    def test_exactly_five_tools_declared(self):
        """Spec requires exactly 5 tools (FR-001)."""
        tool = get_task_tools()
        assert len(tool.function_declarations) == 5

    def test_tool_names_are_correct(self):
        """All required tool names should be present."""
        tool = get_task_tools()
        names = {fd.name for fd in tool.function_declarations}
        expected = {"add_task", "list_tasks", "complete_task", "delete_task", "update_task"}
        assert names == expected

    # T037: Test all 5 tools have user_id as required parameter
    def test_all_tools_have_user_id_property(self):
        """Every tool must have user_id in properties."""
        tool = get_task_tools()
        for fd in tool.function_declarations:
            schema = fd.parameters_json_schema
            assert "user_id" in schema["properties"], f"{fd.name} missing user_id property"

    def test_all_tools_have_user_id_required(self):
        """Every tool must require user_id parameter (FR-002)."""
        tool = get_task_tools()
        for fd in tool.function_declarations:
            schema = fd.parameters_json_schema
            assert "user_id" in schema["required"], f"{fd.name} user_id not in required"

    def test_user_id_is_string_type(self):
        """user_id should be typed as string."""
        tool = get_task_tools()
        for fd in tool.function_declarations:
            schema = fd.parameters_json_schema
            user_id_prop = schema["properties"]["user_id"]
            assert user_id_prop["type"] == "string", f"{fd.name} user_id should be string"


class TestAddTaskParameters:
    """Test add_task tool parameters (T038)."""

    def test_add_task_has_title_parameter(self):
        """add_task should have title parameter."""
        tool = get_task_tools()
        add_task = next(fd for fd in tool.function_declarations if fd.name == "add_task")
        schema = add_task.parameters_json_schema
        assert "title" in schema["properties"]

    def test_add_task_has_description_parameter(self):
        """add_task should have description parameter."""
        tool = get_task_tools()
        add_task = next(fd for fd in tool.function_declarations if fd.name == "add_task")
        schema = add_task.parameters_json_schema
        assert "description" in schema["properties"]

    def test_add_task_required_parameters(self):
        """add_task should require user_id and title only."""
        tool = get_task_tools()
        add_task = next(fd for fd in tool.function_declarations if fd.name == "add_task")
        schema = add_task.parameters_json_schema
        assert set(schema["required"]) == {"user_id", "title"}

    def test_add_task_description_is_optional(self):
        """add_task description should not be required."""
        tool = get_task_tools()
        add_task = next(fd for fd in tool.function_declarations if fd.name == "add_task")
        schema = add_task.parameters_json_schema
        assert "description" not in schema["required"]


class TestListTasksParameters:
    """Test list_tasks tool parameters (T039)."""

    def test_list_tasks_has_status_parameter(self):
        """list_tasks should have status parameter."""
        tool = get_task_tools()
        list_tasks = next(fd for fd in tool.function_declarations if fd.name == "list_tasks")
        schema = list_tasks.parameters_json_schema
        assert "status" in schema["properties"]

    def test_list_tasks_status_enum_values(self):
        """list_tasks status should have correct enum values (FR-009)."""
        tool = get_task_tools()
        list_tasks = next(fd for fd in tool.function_declarations if fd.name == "list_tasks")
        schema = list_tasks.parameters_json_schema
        status_prop = schema["properties"]["status"]
        assert status_prop["enum"] == ["all", "pending", "completed"]

    def test_list_tasks_status_is_optional(self):
        """list_tasks status should not be required (defaults to all)."""
        tool = get_task_tools()
        list_tasks = next(fd for fd in tool.function_declarations if fd.name == "list_tasks")
        schema = list_tasks.parameters_json_schema
        assert "status" not in schema["required"]

    def test_list_tasks_required_parameters(self):
        """list_tasks should only require user_id."""
        tool = get_task_tools()
        list_tasks = next(fd for fd in tool.function_declarations if fd.name == "list_tasks")
        schema = list_tasks.parameters_json_schema
        assert set(schema["required"]) == {"user_id"}


class TestTaskIdParameters:
    """Test complete_task, delete_task, update_task have integer task_id (T040)."""

    @pytest.mark.parametrize("tool_name", ["complete_task", "delete_task", "update_task"])
    def test_task_id_is_integer(self, tool_name):
        """task_id should be typed as integer for complete, delete, update (FR-012)."""
        tool = get_task_tools()
        fd = next(f for f in tool.function_declarations if f.name == tool_name)
        schema = fd.parameters_json_schema
        assert schema["properties"]["task_id"]["type"] == "integer", \
            f"{tool_name} task_id should be integer"

    @pytest.mark.parametrize("tool_name", ["complete_task", "delete_task", "update_task"])
    def test_task_id_is_required(self, tool_name):
        """task_id should be required for complete, delete, update."""
        tool = get_task_tools()
        fd = next(f for f in tool.function_declarations if f.name == tool_name)
        schema = fd.parameters_json_schema
        assert "task_id" in schema["required"], f"{tool_name} should require task_id"


class TestUpdateTaskParameters:
    """Test update_task has optional title and description (T041)."""

    def test_update_task_has_title_parameter(self):
        """update_task should have title parameter."""
        tool = get_task_tools()
        update_task = next(fd for fd in tool.function_declarations if fd.name == "update_task")
        schema = update_task.parameters_json_schema
        assert "title" in schema["properties"]

    def test_update_task_has_description_parameter(self):
        """update_task should have description parameter."""
        tool = get_task_tools()
        update_task = next(fd for fd in tool.function_declarations if fd.name == "update_task")
        schema = update_task.parameters_json_schema
        assert "description" in schema["properties"]

    def test_update_task_title_is_optional(self):
        """update_task title should not be required (FR-011)."""
        tool = get_task_tools()
        update_task = next(fd for fd in tool.function_declarations if fd.name == "update_task")
        schema = update_task.parameters_json_schema
        assert "title" not in schema["required"]

    def test_update_task_description_is_optional(self):
        """update_task description should not be required (FR-011)."""
        tool = get_task_tools()
        update_task = next(fd for fd in tool.function_declarations if fd.name == "update_task")
        schema = update_task.parameters_json_schema
        assert "description" not in schema["required"]

    def test_update_task_required_parameters(self):
        """update_task should require user_id and task_id only."""
        tool = get_task_tools()
        update_task = next(fd for fd in tool.function_declarations if fd.name == "update_task")
        schema = update_task.parameters_json_schema
        assert set(schema["required"]) == {"user_id", "task_id"}


class TestToolDescriptions:
    """Test all tools have meaningful descriptions."""

    def test_all_tools_have_descriptions(self):
        """Every tool should have a description for Gemini intent detection."""
        tool = get_task_tools()
        for fd in tool.function_declarations:
            assert fd.description is not None and len(fd.description) > 10, \
                f"{fd.name} should have a meaningful description"

    def test_add_task_description_mentions_create(self):
        """add_task description should mention creation intent."""
        tool = get_task_tools()
        add_task = next(fd for fd in tool.function_declarations if fd.name == "add_task")
        description = add_task.description.lower()
        assert any(word in description for word in ["create", "add", "new"]), \
            "add_task description should mention create/add/new"

    def test_list_tasks_description_mentions_view(self):
        """list_tasks description should mention viewing intent."""
        tool = get_task_tools()
        list_tasks = next(fd for fd in tool.function_declarations if fd.name == "list_tasks")
        description = list_tasks.description.lower()
        assert any(word in description for word in ["see", "view", "show", "list"]), \
            "list_tasks description should mention see/view/show/list"

    def test_complete_task_description_mentions_done(self):
        """complete_task description should mention completion intent."""
        tool = get_task_tools()
        complete_task = next(fd for fd in tool.function_declarations if fd.name == "complete_task")
        description = complete_task.description.lower()
        assert any(word in description for word in ["finished", "completed", "done"]), \
            "complete_task description should mention finished/completed/done"

    def test_delete_task_description_mentions_remove(self):
        """delete_task description should mention deletion intent."""
        tool = get_task_tools()
        delete_task = next(fd for fd in tool.function_declarations if fd.name == "delete_task")
        description = delete_task.description.lower()
        assert any(word in description for word in ["remove", "delete", "rid"]), \
            "delete_task description should mention remove/delete"

    def test_update_task_description_mentions_change(self):
        """update_task description should mention modification intent."""
        tool = get_task_tools()
        update_task = next(fd for fd in tool.function_declarations if fd.name == "update_task")
        description = update_task.description.lower()
        assert any(word in description for word in ["change", "edit", "update", "modify", "rename"]), \
            "update_task description should mention change/edit/update/modify"
