import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN_CLIENTE = "admin_cliente"
    EVALUADOR = "evaluador"
    VISTA_SOLO = "vista_solo"


class EvaluationStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DocumentState(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class RfcStatus(str, Enum):
    REQUESTED = "requested"
    EVALUATED = "evaluated"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CLOSED = "closed"


class RfcRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RfcImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RfcUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RfcPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class SprintStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class BacklogItemPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# === CLIENT ===
class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    name: str = Field(index=True)
    sector: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    users: list["User"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    evaluations: list["Evaluation"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    documents: list["Document"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    rfcs: list["Rfc"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    sprints: list["Sprint"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# === USER ===
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str
    role: UserRole = Field(default=UserRole.EVALUADOR)
    client_id: Optional[str] = Field(default=None, foreign_key="clients.id", index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    client: Optional[Client] = Relationship(back_populates="users")
    sessions: list["Session"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# === SESSION ===
class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    user: Optional[User] = Relationship(back_populates="sessions")


# === CONTROL DEFINITION ===
class ControlDefinition(SQLModel, table=True):
    __tablename__ = "control_definitions"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    code: str = Field(unique=True, index=True)
    domain: str = Field(index=True)
    title: str
    description: str
    parent_control: Optional[str] = None

    responses: list["ControlResponse"] = Relationship(
        back_populates="control",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# === EVALUATION ===
class Evaluation(SQLModel, table=True):
    __tablename__ = "evaluations"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    client_id: str = Field(foreign_key="clients.id", index=True)
    name: str
    description: Optional[str] = None
    status: EvaluationStatus = Field(default=EvaluationStatus.DRAFT)
    created_by: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    client: Optional[Client] = Relationship(back_populates="evaluations")
    responses: list["ControlResponse"] = Relationship(
        back_populates="evaluation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# === CONTROL RESPONSE ===
class ControlResponse(SQLModel, table=True):
    __tablename__ = "control_responses"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    evaluation_id: str = Field(foreign_key="evaluations.id", index=True)
    control_id: str = Field(foreign_key="control_definitions.id", index=True)
    maturity: int = Field(default=0, ge=0, le=5)
    notes: Optional[str] = None
    created_by: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    evaluation: Optional[Evaluation] = Relationship(back_populates="responses")
    control: Optional[ControlDefinition] = Relationship(back_populates="responses")
    evidence_files: list["EvidenceFile"] = Relationship(
        back_populates="response",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# === EVIDENCE FILE ===
class EvidenceFile(SQLModel, table=True):
    __tablename__ = "evidence_files"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    response_id: str = Field(foreign_key="control_responses.id", index=True)
    filename: str
    filepath: str
    file_size: int
    content_type: str
    uploaded_by: str = Field(foreign_key="users.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    response: Optional[ControlResponse] = Relationship(back_populates="evidence_files")


# === DOCUMENT ===
class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    client_id: str = Field(foreign_key="clients.id", index=True)
    title: str
    document_type: str
    created_by: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    client: Optional[Client] = Relationship(back_populates="documents")
    versions: list["DocumentVersion"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# === DOCUMENT VERSION ===
class DocumentVersion(SQLModel, table=True):
    __tablename__ = "document_versions"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    document_id: str = Field(foreign_key="documents.id", index=True)
    version: str
    state: DocumentState = Field(default=DocumentState.DRAFT)
    author_id: str = Field(foreign_key="users.id")
    reviewer_id: Optional[str] = Field(default=None, foreign_key="users.id")
    approver_id: Optional[str] = Field(default=None, foreign_key="users.id")
    change_summary: str = ""
    content: str = ""
    content_hash: str = ""
    previous_version_id: Optional[str] = Field(
        default=None, foreign_key="document_versions.id"
    )
    review_deadline: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    document: Optional[Document] = Relationship(back_populates="versions")


# === RFC ===
class Rfc(SQLModel, table=True):
    __tablename__ = "rfcs"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    client_id: str = Field(foreign_key="clients.id", index=True)
    title: str
    description: str
    risk_level: RfcRiskLevel = Field(default=RfcRiskLevel.LOW)
    impact: RfcImpact = Field(default=RfcImpact.LOW)
    urgency: RfcUrgency = Field(default=RfcUrgency.LOW)
    priority: RfcPriority = Field(default=RfcPriority.P4)
    status: RfcStatus = Field(default=RfcStatus.REQUESTED)
    applicant_id: str = Field(foreign_key="users.id")
    evaluator_id: Optional[str] = Field(default=None, foreign_key="users.id")
    approver_id: Optional[str] = Field(default=None, foreign_key="users.id")
    assignee_id: Optional[str] = Field(default=None, foreign_key="users.id")
    linked_controls: str = "[]"
    linked_documents: str = "[]"
    implementation_plan: str = ""
    rollback_plan: str = ""
    test_plan: str = ""
    review_notes: str = ""
    target_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    client: Optional[Client] = Relationship(back_populates="rfcs")


# === SPRINT ===
class Sprint(SQLModel, table=True):
    __tablename__ = "sprints"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    client_id: str = Field(foreign_key="clients.id", index=True)
    name: str
    goal: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: SprintStatus = Field(default=SprintStatus.PLANNED)
    created_by: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    client: Optional[Client] = Relationship(back_populates="sprints")
    backlog_items: list["BacklogItem"] = Relationship(
        back_populates="sprint",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# === BACKLOG ITEM ===
class BacklogItem(SQLModel, table=True):
    __tablename__ = "backlog_items"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    client_id: str = Field(foreign_key="clients.id", index=True)
    sprint_id: Optional[str] = Field(default=None, foreign_key="sprints.id")
    control_id: Optional[str] = Field(
        default=None, foreign_key="control_definitions.id"
    )
    linked_rfc_id: Optional[str] = Field(default=None, foreign_key="rfcs.id")
    title: str
    description: str = ""
    priority: BacklogItemPriority = Field(default=BacklogItemPriority.MEDIUM)
    effort_hours: int = 0
    status: TaskStatus = Field(default=TaskStatus.TODO)
    assignee_id: Optional[str] = Field(default=None, foreign_key="users.id")
    created_by: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    sprint: Optional[Sprint] = Relationship(back_populates="backlog_items")
    tasks: list["SprintTask"] = Relationship(
        back_populates="backlog_item",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# === SPRINT TASK ===
class SprintTask(SQLModel, table=True):
    __tablename__ = "sprint_tasks"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    backlog_item_id: str = Field(foreign_key="backlog_items.id", index=True)
    title: str
    assignee_id: Optional[str] = Field(default=None, foreign_key="users.id")
    status: TaskStatus = Field(default=TaskStatus.TODO)
    time_spent_minutes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    backlog_item: Optional[BacklogItem] = Relationship(back_populates="tasks")


# === AUDIT LOG ===
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    user_id: Optional[str] = Field(default=None, foreign_key="users.id")
    client_id: Optional[str] = Field(default=None)
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: str = ""
    ip_address: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
