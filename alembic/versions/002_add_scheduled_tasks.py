"""Add scheduled tasks and day schedules tables

Revision ID: 002_scheduled_tasks
Revises: 001_initial
Create Date: 2024-02-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_scheduled_tasks"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Day schedules table
    op.create_table(
        "day_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("schedule_date", sa.Date, nullable=False, index=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("notes_tamil", sa.Text, nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_day_schedules_org_date", "day_schedules", ["org_id", "schedule_date"], unique=True)

    # Scheduled tasks table
    op.create_table(
        "scheduled_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("schedule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("day_schedules.id"), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_tamil", sa.Text, nullable=False),
        sa.Column("scheduled_time", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=True),
        sa.Column("field_name", sa.String(100), nullable=True),
        sa.Column("field_name_tamil", sa.String(100), nullable=True),
        sa.Column("crop_name", sa.String(100), nullable=True),
        sa.Column("crop_name_tamil", sa.String(100), nullable=True),
        sa.Column("assigned_worker_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_worker_name", sa.String(100), nullable=True),
        sa.Column("assigned_worker_name_tamil", sa.String(100), nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("status", sa.String(50), nullable=False, server_default="scheduled"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("notes_tamil", sa.Text, nullable=True),
        sa.Column("voice_note_url", sa.String(500), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("has_issues", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("issue_type", sa.String(50), nullable=True),
        sa.Column("issue_description", sa.Text, nullable=True),
        sa.Column("issue_description_tamil", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_scheduled_tasks_org_time", "scheduled_tasks", ["org_id", "scheduled_time"])
    op.create_index("idx_scheduled_tasks_worker", "scheduled_tasks", ["assigned_worker_id", "scheduled_time"])
    op.create_index("idx_scheduled_tasks_schedule", "scheduled_tasks", ["schedule_id"])

    # Task updates table
    op.create_table(
        "task_updates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scheduled_tasks.id"), nullable=False),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("worker_name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("notes_tamil", sa.Text, nullable=True),
        sa.Column("voice_note_url", sa.String(500), nullable=True),
        sa.Column("issue_type", sa.String(50), nullable=True),
        sa.Column("issue_description", sa.Text, nullable=True),
        sa.Column("issue_description_tamil", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_task_updates_task", "task_updates", ["task_id", "timestamp"])


def downgrade() -> None:
    op.drop_table("task_updates")
    op.drop_table("scheduled_tasks")
    op.drop_table("day_schedules")
