"""
a2a and ap2 Protocol Type Definitions.

This module contains all the protocol data models used for communication between
agents and the framework.
"""

from __future__ import annotations as _annotations

from typing import Annotated, Any, Literal, TypeVar, Union
from uuid import UUID

import pydantic
from pydantic import Discriminator, Field
from pydantic.alias_generators import to_camel
from typing_extensions import Required, NotRequired, TypeAlias, TypedDict


# -----------------------------------------------------------------------------
# Base Types and Enums
# -----------------------------------------------------------------------------

# TypeVars for generic types
ResultT = TypeVar("ResultT")
ErrorT = TypeVar("ErrorT")

Role: TypeAlias = Literal["agent", "user"]

TaskState: TypeAlias = Literal[
    "submitted",  # The task has been submitted and is awaiting execution.
    "working",  # The agent is actively working on the task.
    "input-required",  # The task is paused and waiting for input from the user.
    "completed",  # The task has been successfully completed.
    "canceled",  # The task has been canceled by the user.
    "failed",  # The task failed due to an error during execution.
    "rejected",  # The task was rejected by the agent and was not started.
    "auth-required",  # The task requires authentication to proceed.
    "unknown",  # The task is in an unknown or indeterminate state. <NotPartOfA2A>
    "trust-verification-required",  # The task requires trust verification to proceed. <NotPartOfA2A>
    "pending",  # The task is pending execution. <NotPartOfA2A>
    "suspended",  # The task is suspended and is not currently running. <NotPartOfA2A>
    "resumed",  # The task is resumed and is currently running. <NotPartOfA2A>
    "negotiation-bid-submitted",  # The task is submitted for negotiation. <NotPartOfA2A>
    "negotiation-bid-lost",  # The task bid was lost in negotiation. <NotPartOfA2A>
    "negotiation-bid-won",  # The task bid was won in negotiation. <NotPartOfA2A>
]

NegotiationStatus: TypeAlias = Literal[
    "proposed",  # The negotiation is proposed. <NotPartOfA2A>
    "accepted",  # The negotiation is accepted. <NotPartOfA2A>
    "rejected",  # The negotiation is rejected. <NotPartOfA2A>
    "countered",  # The negotiation is countered. <NotPartOfA2A>
]

NegotiationSessionStatus: TypeAlias = Literal[
    "initiated",  # The negotiation session is initiated. <NotPartOfA2A>
    "ongoing",  # The negotiation session is ongoing. <NotPartOfA2A>
    "completed",  # The negotiation session is completed. <NotPartOfA2A>
    "rejected",  # The negotiation session is rejected. <NotPartOfA2A>
]

TrustLevel: TypeAlias = Literal[
    "admin",  # Admin operations, minimal risk <NotPartOfA2A>
    "analyst",  # Standard operations <NotPartOfA2A>
    "auditor",  # Sensitive operations <NotPartOfA2A>
    "editor",  # Edit operations, moderate risk <NotPartOfA2A>
    "guest",  # Limited access, read-only operations <NotPartOfA2A>
    "manager",  # Management operations, elevated permissions <NotPartOfA2A>
    "operator",  # System operations, moderate risk <NotPartOfA2A>
    "super_admin",  # Highest level access, all operations permitted <NotPartOfA2A>
    "support",  # Support operations, troubleshooting access <NotPartOfA2A>
    "viewer",  # View-only access, minimal permissions <NotPartOfA2A>
]

IdentityProvider: TypeAlias = Literal[
    "keycloak",  # Keycloak identity provider <NotPartOfA2A>
    "azure_ad",  # Azure AD identity provider <NotPartOfA2A>
    "okta",  # Okta identity provider <NotPartOfA2A>
    "auth0",  # Auth0 identity provider <NotPartOfA2A>
    "custom",  # Custom identity provider <NotPartOfA2A>
]

# -----------------------------------------------------------------------------
# Content & Message Parts
# -----------------------------------------------------------------------------

@pydantic.with_config({"alias_generator": to_camel})
class TextPart(TypedDict):
    """Represents a text segment within parts."""

    kind: Required[Literal["text"]]
    """The kind of the part."""

    metadata: NotRequired[dict[str, Any]]
    """Metadata about the text part."""

    text: Required[str]
    """The text of the part."""

    embeddings: NotRequired[list[float]]
    """The embeddings of Text. <NotPartOfA2A>"""

@pydantic.with_config({"alias_generator": to_camel})
class FileWithBytes(TypedDict):
    """File representation with binary content."""

    bytes: Required[str]
    """The bytes of the file."""

    mimeType: NotRequired[str]
    """The MIME type of the file."""

    name: NotRequired[str]
    """The name of the file."""

    embeddings: NotRequired[list[float]]
    """The embeddings of File. <NotPartOfA2A>"""


@pydantic.with_config({"alias_generator": to_camel})
class FileWithUri(FileWithBytes):
    """File representation with URI reference."""

    uri: Required[str]
    """The URI of the file."""


@pydantic.with_config({"alias_generator": to_camel})
class FilePart(TextPart):
    """Represents a file segment within a message or artifact.
    
    The file content can be provided either directly as bytes or as a URI.
    """

    kind: Required[Literal["file"]]
    """The kind of the part."""

    file: Required[FileWithBytes | FileWithUri]
    """The file of the part."""

    embeddings: NotRequired[list[float]]
    """The embeddings of File. <NotPartOfA2A>"""


class DataPart(TextPart):
    """Represents a structured data segment (e.g., JSON) within a message or artifact."""

    kind: Required[Literal["data"]]
    """The kind of the part."""

    data: Required[dict[str, Any]]
    """The data of the part."""

    embeddings: NotRequired[list[float]]
    """The embeddings of Data. <NotPartOfA2A>"""


Part = Annotated[Union[TextPart, FilePart, DataPart], Field(discriminator="kind")]

# -----------------------------------------------------------------------------
# Artifacts
# -----------------------------------------------------------------------------

@pydantic.with_config({"alias_generator": to_camel})
class Artifact(TypedDict):
    """Represents the final output generated by an agent after completing a task.

    Artifacts are immutable data structures that contain the results of agent execution.
    They can contain multiple parts (text, files, structured data) and are uniquely
    identified for tracking and retrieval.

    A single task may produce multiple artifacts when the output naturally
    separates into distinct deliverables (e.g., frontend + backend code).
    """

    artifact_id: Required[UUID]
    """Unique identifier for the artifact."""

    name: NotRequired[str]
    """Human Readable name of the artifact."""

    description: NotRequired[str]
    """A description of the artifact."""

    metadata: NotRequired[dict[str, Any]]
    """Metadata about the artifact."""

    parts: NotRequired[list[Part]]
    """The parts that make up the artifact."""

    append: NotRequired[bool]
    """Whether to append this artifact to an existing one."""

    last_chunk: NotRequired[bool]
    """Whether this is the last chunk of the artifact."""

    extensions: NotRequired[list[str]]
    """Array of extensions."""



@pydantic.with_config({"alias_generator": to_camel})
class Message(TypedDict):
    """Communication content exchanged between agents, users, and systems.

    Messages represent all non-result communication in the Pebbling protocol.
    Unlike Artifacts (which contain task outputs), Messages carry operational
    content like instructions, status updates, context, and metadata.

    Message Types:
    - User Instructions: Task requests with context and files
    - Agent Communication: Status updates, thoughts, coordination
    - System Messages: Errors, warnings, protocol information
    - Context Sharing: Background information, references, metadata

    Multi-part Structure:
    Messages can contain multiple parts to organize different content types:
    - Text parts for instructions or descriptions
    - File parts for context documents or references
    - Data parts for structured metadata or parameters

    Flow Pattern:
    Client → Message (request) → Agent → Message (status) → Artifact (result)
    """

    message_id: Required[UUID]
    """Identifier created by the message creator."""
    
    context_id: Required[UUID]
    """The context the message is associated with."""
    
    task_id: Required[UUID]
    """Identifier of task the message is related to."""
    
    reference_task_ids: NotRequired[list[UUID]]
    """List of identifiers of tasks that this message is related to."""
    
    kind: Required[Literal["message"]]
    """The type of the message."""

    metadata: NotRequired[dict[str, Any]]
    """Metadata associated with the message."""

    parts: Required[list[Part]]
    """The parts of the message."""

    role: Required[Literal['user', 'agent', 'system']]
    """The role of the message."""

    extensions: NotRequired[list[str]]
    """Array of extensions."""


# -----------------------------------------------------------------------------
# Security Schemes
# -----------------------------------------------------------------------------


@pydantic.with_config({"alias_generator": to_camel})
class HTTPAuthSecurityScheme(TypedDict):
    """HTTP security scheme."""

    type: Required[Literal["http"]]
    """The type of the security scheme."""
    
    scheme: Required[str]
    """The scheme of the security scheme."""
    
    bearer_format: NotRequired[str]
    """The bearer format of the security scheme."""
    
    description: NotRequired[str]
    """The description of the security scheme."""


@pydantic.with_config({"alias_generator": to_camel})
class APIKeySecurityScheme(TypedDict):
    """API Key security scheme."""

    type: Required[Literal["apiKey"]]
    """The type of the security scheme."""
    
    name: Required[str]
    """The name of the security scheme."""
    
    in_: Required[Literal["query", "header", "cookie"]]
    """The location of the security scheme."""
    
    description: NotRequired[str]
    """The description of the security scheme."""


@pydantic.with_config({"alias_generator": to_camel})
class OAuth2SecurityScheme(TypedDict):
    """OAuth2 security scheme."""

    type: Required[Literal["oauth2"]]
    """The type of the security scheme."""
    
    flows: Required[dict[str, Any]]
    """The flows of the security scheme."""
    
    description: NotRequired[str]
    """The description of the security scheme."""


@pydantic.with_config({"alias_generator": to_camel})
class OpenIdConnectSecurityScheme(TypedDict):
    """OpenID Connect security scheme."""

    type: Required[Literal["openIdConnect"]]
    """The type of the security scheme."""
    
    open_id_connect_url: Required[str]
    """The OpenID Connect URL of the security scheme."""
    
    description: NotRequired[str]
    """The description of the security scheme."""


@pydantic.with_config({"alias_generator": to_camel})
class MutualTLSSecurityScheme(TypedDict):
    """Mutual TLS security scheme."""

    type: Required[Literal["mutualTLS"]]
    """The type of the security scheme."""
    
    description: NotRequired[str]
    """The description of the security scheme."""


SecurityScheme = Annotated[
    Union[
        HTTPAuthSecurityScheme,
        APIKeySecurityScheme,
        OAuth2SecurityScheme,
        OpenIdConnectSecurityScheme,
        MutualTLSSecurityScheme,
    ],
    Discriminator("type"),
]


# -----------------------------------------------------------------------------
# Push Notification Configuration
# -----------------------------------------------------------------------------


@pydantic.with_config({"alias_generator": to_camel})
class PushNotificationConfig(TypedDict):
    """Configuration for push notifications.

    When the server needs to notify the client of an update outside of a connected session.
    """

    id: Required[UUID]
    """The ID of the push notification configuration."""
    
    url: Required[str]
    """The URL of the push notification configuration."""
    
    token: NotRequired[str]
    """The token of the push notification configuration."""
    
    authentication: NotRequired[SecurityScheme]
    """The authentication of the push notification configuration."""


@pydantic.with_config({"alias_generator": to_camel})
class PushNotificationAuthenticationInfo(TypedDict):
    """Authentication information for push notifications."""

    schemes: list[str]
    """A list of supported authentication schemes (e.g., 'Basic', 'Bearer')."""
    
    credentials: NotRequired[str]
    """Optional credentials required by the push notification endpoint."""


@pydantic.with_config({"alias_generator": to_camel})
class TaskPushNotificationConfig(TypedDict):
    """Configuration for task push notifications."""

    id: Required[UUID]
    """The ID of the task push notification configuration."""
    
    push_notification_config: Required[PushNotificationConfig]
    """The push notification configuration of the task push notification configuration."""


# -----------------------------------------------------------------------------
# Task
# -----------------------------------------------------------------------------

@pydantic.with_config({"alias_generator": to_camel})
class TaskStatus(TypedDict):
    """Status information for a task."""

    message: NotRequired[Message]
    state: Required[TaskState]
    timestamp: Required[str] = Field(
        examples=["2025-10-10T10:00:00Z"], description="ISO datetime value of when the status was updated."
    )


@pydantic.with_config({"alias_generator": to_camel})
class Task(TypedDict):
    """Stateful execution unit that coordinates client-agent interaction to achieve a goal.

    Tasks serve as the primary coordination mechanism in the Pebbling protocol,
    managing the complete lifecycle from request to completion. They maintain
    conversation history, track execution state, and collect generated artifacts.

    Core Responsibilities:
    - Message Exchange: Facilitate communication between clients and agents
    - State Management: Track task progress and execution status
    - Artifact Collection: Gather and organize agent-generated outputs
    - History Tracking: Maintain complete conversation and decision trail

    Task Lifecycle:
    1. Creation: Client initiates task with initial message/requirements
    2. Processing: Agent processes messages and updates status
    3. Communication: Bidirectional message exchange as needed
    4. Artifact Generation: Agent produces deliverable outputs
    5. Completion: Final status update and artifact delivery

    Key Properties:
    - Client-Initiated: Always created by clients, never by agents
    - Agent-Controlled: Status and progress determined by executing agent
    - Stateful: Maintains complete execution context and history
    - Traceable: Unique ID enables task tracking and reference

    Task Relationships:
    - Contains: Multiple messages (conversation history)
    - Produces: Multiple artifacts (execution results)
    - References: Other tasks via reference_task_ids for coordination
    - Belongs to: Specific context for session management
    """

    id: Required[UUID]
    """The ID of the task."""
    
    context_id: Required[UUID]
    """The ID of the context the task is associated with."""
    
    kind: Required[Literal["task"]]
    """The type of the task."""
    
    status: Required[TaskStatus]
    """The status of the task."""

    artifacts: NotRequired[list[Artifact]]
    """The artifacts of the task."""
    
    history: NotRequired[list[Message]]
    """The history of the task."""
    
    metadata: NotRequired[dict[str, Any]]
    """The metadata of the task."""


@pydantic.with_config({"alias_generator": to_camel})
class TaskStatusUpdateEvent(TypedDict):
    """Event sent by the agent to notify the client of a change in a task's status.

    This is typically used in streaming or subscription models.
    """

    task_id: Required[UUID]
    """The ID of the task."""
    
    context_id: Required[UUID]
    """The ID of the context the task is associated with."""
    
    final: Required[bool]
    """Indicates if this is the final status update."""
    
    kind: Required[Literal["status-update"]]
    """The type of the event."""
    
    metadata: NotRequired[dict[str, Any]]
    """Additional metadata."""
    
    status: Required[TaskStatus]
    """The status of the task."""
    


@pydantic.with_config({"alias_generator": to_camel})
class TaskArtifactUpdateEvent(TypedDict):
    """Event sent by the agent to notify the client that an artifact has been generated or updated.
    
    This is typically used in streaming models.
    """

    task_id: Required[UUID]
    """The ID of the task."""
    
    append: NotRequired[bool]
    """Indicates if this is an append operation."""
    
    artifact: Required[Artifact]
    """The artifact that has been generated or updated."""
    
    context_id: Required[UUID]
    """The ID of the context the task is associated with."""
    
    kind: Required[Literal["artifact-update"]]
    """The type of the event."""
    
    last_chunk: NotRequired[bool]
    """Indicates if this is the last chunk of the artifact."""
    
    metadata: NotRequired[dict[str, Any]]
    """Additional metadata."""
    

@pydantic.with_config({"alias_generator": to_camel})
class TaskSendParams(TypedDict):
    """Internal parameters for task execution within the framework. <NotPartOfA2A>"""

    task_id: Required[UUID]
    """The ID of the task."""
    
    context_id: Required[UUID]
    """The ID of the context the task is associated with."""
    
    message: NotRequired[Message]
    """The message to send."""
    
    history_length: NotRequired[int]
    """The length of the history."""
    
    metadata: NotRequired[dict[str, Any]]
    """Additional metadata."""


@pydantic.with_config({"alias_generator": to_camel})
class TaskIdParams(TypedDict):
    """Defines parameters containing a task ID, used for simple task operations."""

    task_id: Required[UUID]
    """The ID of the task."""
    
    metadata: NotRequired[dict[str, Any]]
    """Additional metadata."""


@pydantic.with_config({"alias_generator": to_camel})
class TaskQueryParams(TaskIdParams):
    """Defines parameters for querying a task, with an option to limit history length."""

    history_length: NotRequired[int]
    """The length of the history."""


@pydantic.with_config({"alias_generator": to_camel})
class ListTasksParams(TypedDict):
    """Defines parameters for listing tasks. <NotPartOfA2A>"""

    history_length: NotRequired[int]
    """The length of the history."""
    
    metadata: NotRequired[dict[str, Any]]
    """Additional metadata."""


@pydantic.with_config({"alias_generator": to_camel})
class TaskFeedbackParams(TypedDict):
    """Defines parameters for providing feedback on a task. <NotPartOfA2A>"""

    task_id: Required[UUID]
    """The ID of the task."""
    
    feedback: Required[str]
    """The feedback to provide."""
    
    rating: NotRequired[int]  # Optional rating 1(lowest)-5(highest)
    """The rating to provide."""
    
    metadata: NotRequired[dict[str, Any]]
    """Additional metadata."""

    