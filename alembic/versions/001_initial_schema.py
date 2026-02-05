"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================
    # CORE MODULE TABLES
    # ========================================

    # Organizations table
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="both"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("settings", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("employee_code", sa.String(20), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(15), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("pin_hash", sa.String(256), nullable=True),
        sa.Column("password_hash", sa.String(256), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="worker"),
        sa.Column("department", sa.String(50), nullable=False, server_default="general"),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="ta"),
        sa.Column("voice_profile_id", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_users_org", "users", ["org_id"])
    op.create_index("idx_users_role", "users", ["role"])

    # Locations table (hierarchical)
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("qr_code", sa.String(100), unique=True, nullable=True),
        sa.Column("coordinates", postgresql.JSONB, nullable=True),
        sa.Column("area_sqm", sa.Numeric(10, 2), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("description_tamil", sa.String(500), nullable=True),
        sa.Column("extra_data", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_locations_parent", "locations", ["parent_id"])
    op.create_index("idx_locations_type", "locations", ["type"])
    op.create_index("idx_locations_org_code", "locations", ["org_id", "code"], unique=True)

    # Notifications table
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="info"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("title_tamil", sa.String(200), nullable=True),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("message_tamil", sa.Text, nullable=True),
        sa.Column("audio_url", sa.String(500), nullable=True),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_url", sa.String(500), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_notifications_user", "notifications", ["user_id", "read_at"])

    # Audio logs table
    op.create_table(
        "audio_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audio_url", sa.String(500), nullable=False),
        sa.Column("audio_format", sa.String(20), nullable=False, server_default="wav"),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("transcript_tamil", sa.Text, nullable=True),
        sa.Column("transcript_english", sa.Text, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("keywords", postgresql.JSONB, nullable=True),
        sa.Column("processing_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_audio_entity", "audio_logs", ["entity_type", "entity_id"])

    # Attachments table
    op.create_table(
        "attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(50), nullable=False, server_default="image"),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("file_size_bytes", sa.Integer, nullable=True),
        sa.Column("caption", sa.String(200), nullable=True),
        sa.Column("caption_tamil", sa.String(200), nullable=True),
        sa.Column("sequence_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_before", sa.Boolean, nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_attachments_entity", "attachments", ["entity_type", "entity_id"])

    # ========================================
    # FARM MODULE TABLES
    # ========================================

    # Crop varieties table
    op.create_table(
        "crop_varieties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("growth_type", sa.String(50), nullable=True),
        sa.Column("first_harvest_days", sa.Integer, nullable=True),
        sa.Column("subsequent_harvest_days", sa.Integer, nullable=True),
        sa.Column("lifespan_years", sa.Numeric(3, 1), nullable=True),
        sa.Column("water_requirement", sa.String(50), nullable=True),
        sa.Column("soil_type_preferred", sa.String(100), nullable=True),
        sa.Column("optimal_temperature", sa.String(50), nullable=True),
        sa.Column("nutrition_profile", postgresql.JSONB, nullable=True),
        sa.Column("icon_url", sa.String(500), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_tamil", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Fields table
    op.create_table(
        "fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("field_type", sa.String(50), nullable=False, server_default="grass_block"),
        sa.Column("area_acres", sa.Numeric(6, 2), nullable=True),
        sa.Column("soil_type", sa.String(50), nullable=True),
        sa.Column("irrigation_type", sa.String(50), nullable=True),
        sa.Column("current_crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crop_varieties.id"), nullable=True),
        sa.Column("last_sowing_date", sa.Date, nullable=True),
        sa.Column("last_harvest_date", sa.Date, nullable=True),
        sa.Column("next_harvest_date", sa.Date, nullable=True),
        sa.Column("last_fertilizer_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("extra_data", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Cultivation cycles table
    op.create_table(
        "cultivation_cycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("crop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crop_varieties.id"), nullable=False),
        sa.Column("cycle_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("sowing_date", sa.Date, nullable=False),
        sa.Column("expected_first_harvest", sa.Date, nullable=True),
        sa.Column("actual_first_harvest", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("end_reason", sa.String(200), nullable=True),
        sa.Column("total_harvests", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_yield_kg", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add current_cycle_id to fields after cultivation_cycles exists
    op.add_column("fields", sa.Column("current_cycle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cultivation_cycles.id"), nullable=True))

    # Farm tasks table
    op.create_table(
        "farm_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=True),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("title_tamil", sa.String(200), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_tamil", sa.Text, nullable=True),
        sa.Column("scheduled_date", sa.Date, nullable=False),
        sa.Column("scheduled_time", sa.Time, nullable=True),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checklist_template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("postpone_reason", sa.Text, nullable=True),
        sa.Column("postponed_to", sa.Date, nullable=True),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("feedback_tamil", sa.Text, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("has_voice_notes", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_farm_tasks_date", "farm_tasks", ["scheduled_date", "status"])
    op.create_index("idx_farm_tasks_assigned", "farm_tasks", ["assigned_to", "status"])

    # Watering schedules table
    op.create_table(
        "watering_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("frequency_days", sa.Integer, nullable=False),
        sa.Column("preferred_time", sa.Time, nullable=True),
        sa.Column("last_watered_date", sa.Date, nullable=True),
        sa.Column("next_watering_date", sa.Date, nullable=True),
        sa.Column("irrigation_method", sa.String(50), nullable=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("includes_fertilizer", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("fertilizer_type", sa.String(100), nullable=True),
        sa.Column("fertilizer_quantity", sa.String(50), nullable=True),
        sa.Column("default_assignee", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Harvests table
    op.create_table(
        "harvests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fields.id"), nullable=False),
        sa.Column("cycle_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cultivation_cycles.id"), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farm_tasks.id"), nullable=True),
        sa.Column("harvest_date", sa.Date, nullable=False),
        sa.Column("harvest_number", sa.Integer, nullable=True),
        sa.Column("yield_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("area_harvested_acres", sa.Numeric(6, 2), nullable=True),
        sa.Column("quality_rating", sa.String(20), nullable=True),
        sa.Column("moisture_content", sa.Numeric(5, 2), nullable=True),
        sa.Column("destination", sa.String(100), nullable=True),
        sa.Column("transport_vehicle", sa.String(50), nullable=True),
        sa.Column("received_by", sa.String(100), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("receipt_confirmed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("harvested_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Farm equipment table
    op.create_table(
        "farm_equipment",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="available"),
        sa.Column("current_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("purchase_date", sa.Date, nullable=True),
        sa.Column("last_maintenance_date", sa.Date, nullable=True),
        sa.Column("next_maintenance_date", sa.Date, nullable=True),
        sa.Column("specifications", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Checklist templates table
    op.create_table(
        "checklist_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("items", postgresql.JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Checklist responses table
    op.create_table(
        "checklist_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_templates.id"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("responses", postgresql.JSONB, nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ========================================
    # MAINTENANCE MODULE TABLES
    # ========================================

    # Asset categories table
    op.create_table(
        "asset_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("domain", sa.String(50), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_categories.id"), nullable=True),
        sa.Column("icon_url", sa.String(500), nullable=True),
        sa.Column("default_maintenance_days", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Assets table
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_categories.id"), nullable=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("qr_code", sa.String(100), unique=True, nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("barcode", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("model_year", sa.Integer, nullable=True),
        sa.Column("installation_date", sa.Date, nullable=True),
        sa.Column("warranty_expiry", sa.Date, nullable=True),
        sa.Column("purchase_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="operational"),
        sa.Column("criticality", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("last_maintenance_date", sa.Date, nullable=True),
        sa.Column("next_maintenance_date", sa.Date, nullable=True),
        sa.Column("maintenance_interval_days", sa.Integer, nullable=True),
        sa.Column("specifications", postgresql.JSONB, nullable=True),
        sa.Column("extra_data", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_assets_location", "assets", ["location_id"])
    op.create_index("idx_assets_status", "assets", ["status"])
    op.create_index("idx_assets_maintenance", "assets", ["next_maintenance_date"])
    op.create_index("idx_assets_org_code", "assets", ["org_id", "code"], unique=True)

    # Inventory items table
    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("sku", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(50), nullable=True),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("unit_tamil", sa.String(20), nullable=True),
        sa.Column("criticality", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("min_stock_level", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("max_stock_level", sa.Numeric(10, 2), nullable=True),
        sa.Column("reorder_point", sa.Numeric(10, 2), nullable=True),
        sa.Column("reorder_quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("lead_time_days", sa.Integer, nullable=True),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_serialized", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Stock levels table
    op.create_table(
        "stock_levels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("last_counted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_stock_levels_item", "stock_levels", ["item_id"])
    op.create_index("idx_stock_unique", "stock_levels", ["item_id", "location_id"], unique=True)

    # Inventory transactions table
    op.create_table(
        "inventory_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("transaction_type", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_inv_trans_item", "inventory_transactions", ["item_id", "created_at"])

    # Vendors table
    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("contact_person", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(15), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("city", sa.String(50), nullable=True),
        sa.Column("gst_number", sa.String(20), nullable=True),
        sa.Column("pan_number", sa.String(20), nullable=True),
        sa.Column("categories", postgresql.JSONB, nullable=True),
        sa.Column("payment_terms", sa.String(50), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_vendors_org_code", "vendors", ["org_id", "code"], unique=True)

    # Job cards table
    op.create_table(
        "job_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("job_number", sa.String(50), unique=True, nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("title_tamil", sa.String(200), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_tamil", sa.Text, nullable=True),
        sa.Column("reported_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reported_via", sa.String(50), nullable=True),
        sa.Column("audio_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution", sa.Text, nullable=True),
        sa.Column("resolution_tamil", sa.Text, nullable=True),
        sa.Column("resolution_audio_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("root_cause", sa.String(200), nullable=True),
        sa.Column("mttr_minutes", sa.Integer, nullable=True),
        sa.Column("labor_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("parts_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("total_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_job_cards_status", "job_cards", ["status", "priority"])
    op.create_index("idx_job_cards_asset", "job_cards", ["asset_id"])
    op.create_index("idx_job_cards_assigned", "job_cards", ["assigned_to", "status"])

    # Job card materials table
    op.create_table(
        "job_card_materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_card_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("job_cards.id"), nullable=False),
        sa.Column("inventory_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("issued_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Tools table
    op.create_table(
        "tools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_tamil", sa.String(100), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="available"),
        sa.Column("current_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("checked_out_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("checked_out_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_calibration_date", sa.Date, nullable=True),
        sa.Column("next_calibration_date", sa.Date, nullable=True),
        sa.Column("purchase_date", sa.Date, nullable=True),
        sa.Column("specifications", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Tool transactions table
    op.create_table(
        "tool_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("transaction_type", sa.String(50), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("to_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("job_card_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("job_cards.id"), nullable=True),
        sa.Column("condition_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Purchase requisitions table
    op.create_table(
        "purchase_requisitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("pr_number", sa.String(50), unique=True, nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("required_date", sa.Date, nullable=True),
        sa.Column("justification", sa.Text, nullable=True),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Purchase requisition items table
    op.create_table(
        "purchase_requisition_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pr_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("purchase_requisitions.id"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("estimated_unit_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Purchase orders table
    op.create_table(
        "purchase_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("po_number", sa.String(50), unique=True, nullable=False),
        sa.Column("pr_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("purchase_requisitions.id"), nullable=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("order_date", sa.Date, nullable=True),
        sa.Column("expected_delivery", sa.Date, nullable=True),
        sa.Column("delivery_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=True),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("terms", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Purchase order items table
    op.create_table(
        "purchase_order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("po_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("received_quantity", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Goods receipts table
    op.create_table(
        "goods_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("grn_number", sa.String(50), unique=True, nullable=False),
        sa.Column("po_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("received_date", sa.Date, nullable=False),
        sa.Column("received_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("invoice_number", sa.String(50), nullable=True),
        sa.Column("invoice_date", sa.Date, nullable=True),
        sa.Column("invoice_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Goods receipt items table
    op.create_table(
        "goods_receipt_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("grn_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("goods_receipts.id"), nullable=False),
        sa.Column("po_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("purchase_order_items.id"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_items.id"), nullable=False),
        sa.Column("ordered_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("received_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("accepted_quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("rejected_quantity", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("condition", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Preventive maintenance schedules table
    op.create_table(
        "preventive_maintenance_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=False),
        sa.Column("schedule_type", sa.String(50), nullable=True),
        sa.Column("frequency_days", sa.Integer, nullable=True),
        sa.Column("last_performed", sa.Date, nullable=True),
        sa.Column("next_due", sa.Date, nullable=True),
        sa.Column("task_template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_templates.id"), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_pm_schedules_due", "preventive_maintenance_schedules", ["next_due", "is_active"])


def downgrade() -> None:
    # Drop all tables in reverse order of creation
    op.drop_table("goods_receipt_items")
    op.drop_table("goods_receipts")
    op.drop_table("purchase_order_items")
    op.drop_table("purchase_orders")
    op.drop_table("purchase_requisition_items")
    op.drop_table("purchase_requisitions")
    op.drop_table("preventive_maintenance_schedules")
    op.drop_table("tool_transactions")
    op.drop_table("tools")
    op.drop_table("job_card_materials")
    op.drop_table("job_cards")
    op.drop_table("inventory_transactions")
    op.drop_table("stock_levels")
    op.drop_table("inventory_items")
    op.drop_table("assets")
    op.drop_table("asset_categories")
    op.drop_table("vendors")
    op.drop_table("checklist_responses")
    op.drop_table("checklist_templates")
    op.drop_table("farm_equipment")
    op.drop_table("harvests")
    op.drop_table("watering_schedules")
    op.drop_table("farm_tasks")
    op.drop_column("fields", "current_cycle_id")
    op.drop_table("cultivation_cycles")
    op.drop_table("fields")
    op.drop_table("crop_varieties")
    op.drop_table("attachments")
    op.drop_table("audio_logs")
    op.drop_table("notifications")
    op.drop_table("locations")
    op.drop_table("users")
    op.drop_table("organizations")
