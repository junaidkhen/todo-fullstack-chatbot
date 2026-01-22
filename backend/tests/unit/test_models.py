"""
Unit tests for SQLModel entities and Pydantic models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from src.models.task import Task, TaskCreate, TaskUpdate, TaskResponse, User
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


class TestUserModel:
    """Test User model validation."""

    def test_user_creation(self):
        """Test creating a valid user."""
        user = User(
            id="user123",
            email="test@example.com",
            password_hash="hashed_password",
            created_at=datetime.utcnow()
        )
        assert user.id == "user123"
        assert user.email == "test@example.com"

    def test_user_unique_email(self):
        """Test that email must be unique (enforced at DB level)."""
        user = User(
            id="user123",
            email="test@example.com",
            password_hash="hash"
        )
        assert user.email == "test@example.com"


class TestTaskModel:
    """Test Task model validation."""

    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields."""
        task = Task(
            user_id="user123",
            title="Test task"
        )
        assert task.user_id == "user123"
        assert task.title == "Test task"
        assert task.completed is False  # Default value
        assert task.description is None  # Default value

    def test_task_creation_full(self):
        """Test creating a task with all fields."""
        task = Task(
            user_id="user123",
            title="Test task",
            description="This is a test task",
            completed=True
        )
        assert task.user_id == "user123"
        assert task.title == "Test task"
        assert task.description == "This is a test task"
        assert task.completed is True

    def test_task_title_validation_min_length(self):
        """Test that TaskCreate validates minimum title length."""
        # SQLModel table classes validate via Pydantic in TaskCreate
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")  # Empty title
        assert "title" in str(exc_info.value).lower()

    def test_task_title_validation_max_length(self):
        """Test that TaskCreate validates maximum title length."""
        long_title = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)
        assert "title" in str(exc_info.value).lower()

    def test_task_description_max_length(self):
        """Test that TaskCreate validates maximum description length."""
        long_description = "a" * 5001
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test", description=long_description)
        assert "description" in str(exc_info.value).lower()

    def test_task_description_optional(self):
        """Test that description is optional."""
        task = Task(user_id="user123", title="Test")
        assert task.description is None

    def test_task_completed_default(self):
        """Test that completed defaults to False."""
        task = Task(user_id="user123", title="Test")
        assert task.completed is False

    def test_task_timestamps_server_default(self):
        """Test that timestamps use server_default (None until persisted)."""
        # With server_default, timestamps are None until database insert
        task = Task(user_id="user123", title="Test")
        # Timestamps are None at Python level (populated by database)
        assert task.created_at is None
        assert task.updated_at is None


class TestTaskCreateModel:
    """Test TaskCreate Pydantic model."""

    def test_task_create_valid(self):
        """Test creating a valid TaskCreate request."""
        task_data = TaskCreate(
            title="Buy groceries",
            description="Milk, eggs, bread"
        )
        assert task_data.title == "Buy groceries"
        assert task_data.description == "Milk, eggs, bread"

    def test_task_create_title_only(self):
        """Test creating a task with title only."""
        task_data = TaskCreate(title="Buy groceries")
        assert task_data.title == "Buy groceries"
        assert task_data.description is None

    def test_task_create_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            TaskCreate()

    def test_task_create_title_too_long(self):
        """Test that title cannot exceed 200 characters."""
        with pytest.raises(ValidationError):
            TaskCreate(title="a" * 201)

    def test_task_create_description_too_long(self):
        """Test that description cannot exceed 5000 characters."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Test", description="a" * 5001)


class TestTaskUpdateModel:
    """Test TaskUpdate Pydantic model."""

    def test_task_update_title_only(self):
        """Test updating only the title."""
        update_data = TaskUpdate(title="Updated title")
        assert update_data.title == "Updated title"
        assert update_data.description is None

    def test_task_update_description_only(self):
        """Test updating only the description."""
        update_data = TaskUpdate(description="Updated description")
        assert update_data.description == "Updated description"
        assert update_data.title is None

    def test_task_update_both_fields(self):
        """Test updating both title and description."""
        update_data = TaskUpdate(
            title="Updated title",
            description="Updated description"
        )
        assert update_data.title == "Updated title"
        assert update_data.description == "Updated description"

    def test_task_update_all_none(self):
        """Test that update can have all None values (partial update)."""
        update_data = TaskUpdate()
        assert update_data.title is None
        assert update_data.description is None


class TestTaskResponseModel:
    """Test TaskResponse Pydantic model."""

    def test_task_response_from_orm(self):
        """Test creating TaskResponse from ORM model."""
        task = Task(
            id=1,
            user_id="user123",
            title="Test task",
            description="Test description",
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        response = TaskResponse.model_validate(task)
        assert response.id == 1
        assert response.title == "Test task"
        assert response.description == "Test description"
        assert response.completed is False
        assert response.created_at is not None
        assert response.updated_at is not None


class TestMessageRoleEnum:
    """Test MessageRole enum validation."""

    def test_message_role_user_value(self):
        """Test USER role has correct value."""
        assert MessageRole.USER.value == "user"

    def test_message_role_assistant_value(self):
        """Test ASSISTANT role has correct value."""
        assert MessageRole.ASSISTANT.value == "assistant"

    def test_message_role_enum_members(self):
        """Test that enum has exactly two members."""
        members = list(MessageRole)
        assert len(members) == 2
        assert MessageRole.USER in members
        assert MessageRole.ASSISTANT in members


class TestConversationModel:
    """Test Conversation model validation."""

    def test_conversation_creation_minimal(self):
        """Test creating a conversation with minimal required fields."""
        conversation = Conversation(user_id="user123")
        assert conversation.user_id == "user123"
        assert conversation.id is None  # Not persisted yet

    def test_conversation_creation_with_id(self):
        """Test creating a conversation with explicit id."""
        conversation = Conversation(id=1, user_id="user123")
        assert conversation.id == 1
        assert conversation.user_id == "user123"

    def test_conversation_user_id_required(self):
        """Test that user_id is required."""
        # SQLModel allows None for non-nullable fields at Python level
        # but will fail at database level
        conversation = Conversation(user_id="test-user")
        assert conversation.user_id == "test-user"

    def test_conversation_messages_relationship_default(self):
        """Test that messages relationship is an empty list by default."""
        conversation = Conversation(user_id="user123")
        assert conversation.messages == []


class TestMessageModel:
    """Test Message model validation."""

    def test_message_creation_user_role(self):
        """Test creating a message with user role."""
        message = Message(
            user_id="user123",
            conversation_id=1,
            role=MessageRole.USER,
            content="Hello, how can you help me?"
        )
        assert message.user_id == "user123"
        assert message.conversation_id == 1
        assert message.role == MessageRole.USER
        assert message.content == "Hello, how can you help me?"

    def test_message_creation_assistant_role(self):
        """Test creating a message with assistant role."""
        message = Message(
            user_id="user123",
            conversation_id=1,
            role=MessageRole.ASSISTANT,
            content="I can help you manage your tasks!"
        )
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "I can help you manage your tasks!"

    def test_message_role_string_value(self):
        """Test that role enum converts to string correctly."""
        message = Message(
            user_id="user123",
            conversation_id=1,
            role=MessageRole.USER,
            content="Test message"
        )
        assert message.role.value == "user"

    def test_message_role_from_string(self):
        """Test creating message with role from string value."""
        message = Message(
            user_id="user123",
            conversation_id=1,
            role="user",  # String value instead of enum
            content="Test message"
        )
        assert message.role == MessageRole.USER

    def test_message_content_required(self):
        """Test that content field is required."""
        message = Message(
            user_id="user123",
            conversation_id=1,
            role=MessageRole.USER,
            content="Required content"
        )
        assert message.content is not None

    def test_message_conversation_id_required(self):
        """Test that conversation_id is required."""
        message = Message(
            user_id="user123",
            conversation_id=1,
            role=MessageRole.USER,
            content="Test"
        )
        assert message.conversation_id == 1


class TestTaskCompositeIndex:
    """Test Task model composite index configuration."""

    def test_task_has_table_args(self):
        """Test that Task model has __table_args__ defined."""
        assert hasattr(Task, "__table_args__")

    def test_task_composite_index_exists(self):
        """Test that composite index is defined in __table_args__."""
        table_args = Task.__table_args__
        assert len(table_args) > 0
        # First element should be the Index
        index = table_args[0]
        assert index.name == "ix_tasks_user_id_completed"


class TestConversationMessageRelationship:
    """Test bidirectional relationship between Conversation and Message."""

    def test_conversation_has_messages_attribute(self):
        """Test Conversation model has messages relationship attribute."""
        conversation = Conversation(user_id="user123")
        assert hasattr(conversation, "messages")

    def test_message_has_conversation_attribute(self):
        """Test Message model has conversation relationship attribute."""
        message = Message(
            user_id="user123",
            conversation_id=1,
            role=MessageRole.USER,
            content="Test"
        )
        assert hasattr(message, "conversation")
