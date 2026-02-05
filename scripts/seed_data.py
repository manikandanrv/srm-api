"""
Seed data script for SRM Operations Management System.

Run this script to populate the database with initial data:
    python scripts/seed_data.py

Requires:
    - Database to exist and migrations to be applied
    - Environment variables configured (or .env file)
"""

import asyncio
import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import bcrypt
import pytz
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def hash_pin(pin: str) -> str:
    """Hash a PIN using bcrypt."""
    return bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# ========================================
# SEED DATA
# ========================================

# Organization
ORG_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
ORGANIZATION = {
    "id": ORG_ID,
    "name": "Sri Ramanasramam",
    "name_tamil": "ஸ்ரீ ரமணாசிரமம்",
    "code": "SRA",
    "type": "both",
    "description": "Sri Ramanasramam Operations Management",
    "settings": {"timezone": "Asia/Kolkata", "currency": "INR"},
}

# Users with different roles
USERS = [
    # Admin
    {
        "id": uuid.UUID("22222222-1111-1111-1111-111111111111"),
        "employee_code": "ADMIN001",
        "name": "System Admin",
        "name_tamil": "நிர்வாகி",
        "phone": "9876543210",
        "email": "admin@sriramana.org",
        "role": "admin",
        "department": "general",
        "pin": "1234",
        "password": "admin123",
    },
    # Management
    {
        "id": uuid.UUID("22222222-1112-1111-1111-111111111111"),
        "employee_code": "MGR001",
        "name": "Selvam",
        "name_tamil": "செல்வம்",
        "phone": "9876543200",
        "email": "selvam@sriramana.org",
        "role": "manager",
        "department": "farm",
        "pin": "0000",
        "password": "manager123",
    },
    # Farm Supervisor
    {
        "id": uuid.UUID("22222222-2222-1111-1111-111111111111"),
        "employee_code": "SUP001",
        "name": "Muthu Kumar",
        "name_tamil": "முத்து குமார்",
        "phone": "9876543211",
        "role": "supervisor",
        "department": "farm",
        "pin": "1111",
    },
    # Farm Workers (matching mock data: Raja, Murugan, Kannan, Lakshmi)
    {
        "id": uuid.UUID("22222222-3333-1111-1111-111111111111"),
        "employee_code": "W001",
        "name": "Raja",
        "name_tamil": "ராஜா",
        "phone": "9876543210",
        "role": "worker",
        "department": "farm",
        "pin": "2222",
    },
    {
        "id": uuid.UUID("22222222-4444-1111-1111-111111111111"),
        "employee_code": "W002",
        "name": "Murugan",
        "name_tamil": "முருகன்",
        "phone": "9876543211",
        "role": "worker",
        "department": "farm",
        "pin": "3333",
    },
    {
        "id": uuid.UUID("22222222-4445-1111-1111-111111111111"),
        "employee_code": "W003",
        "name": "Kannan",
        "name_tamil": "கண்ணன்",
        "phone": "9876543212",
        "role": "worker",
        "department": "farm",
        "pin": "4444",
    },
    {
        "id": uuid.UUID("22222222-4446-1111-1111-111111111111"),
        "employee_code": "W004",
        "name": "Lakshmi",
        "name_tamil": "லக்ஷ்மி",
        "phone": "9876543213",
        "role": "worker",
        "department": "farm",
        "pin": "5555",
    },
    # Additional Farm Workers
    {
        "id": uuid.UUID("22222222-4447-1111-1111-111111111111"),
        "employee_code": "W005",
        "name": "Senthil",
        "name_tamil": "செந்தில்",
        "phone": "9876543214",
        "role": "worker",
        "department": "farm",
        "pin": "6666",
    },
    {
        "id": uuid.UUID("22222222-4448-1111-1111-111111111111"),
        "employee_code": "W006",
        "name": "Ravi",
        "name_tamil": "ரவி",
        "phone": "9876543215",
        "role": "worker",
        "department": "farm",
        "pin": "7777",
    },
    # Maintenance Supervisor
    {
        "id": uuid.UUID("22222222-5555-1111-1111-111111111111"),
        "employee_code": "MAINT001",
        "name": "Krishnan",
        "name_tamil": "கிருஷ்ணன்",
        "phone": "9876543220",
        "role": "supervisor",
        "department": "general",
        "pin": "8888",
    },
    # Electrical Technician
    {
        "id": uuid.UUID("22222222-6666-1111-1111-111111111111"),
        "employee_code": "ELEC001",
        "name": "Suresh",
        "name_tamil": "சுரேஷ்",
        "phone": "9876543221",
        "role": "worker",
        "department": "electrical",
        "pin": "9999",
    },
    # Plumbing Technician
    {
        "id": uuid.UUID("22222222-7777-1111-1111-111111111111"),
        "employee_code": "PLUMB001",
        "name": "Ganesan",
        "name_tamil": "கணேசன்",
        "phone": "9876543222",
        "role": "worker",
        "department": "plumbing",
        "pin": "1010",
    },
]

# Guest Houses (from requirements document)
GUEST_HOUSES = [
    {
        "id": uuid.UUID("33333333-0001-1111-1111-111111111111"),
        "code": "GH-001",
        "name": "Ashram Main Precinct",
        "name_tamil": "ஆசிரம முக்கிய வளாகம்",
        "type": "guest_house",
        "room_count": 25,
        "extra_data": {"utility_profile": "Centralized solar hot water, heritage electrical wiring"},
    },
    {
        "id": uuid.UUID("33333333-0002-1111-1111-111111111111"),
        "code": "GH-002",
        "name": "Morvi Guest House",
        "name_tamil": "மோர்வி விருந்தினர் இல்லம்",
        "type": "guest_house",
        "room_count": 40,
        "extra_data": {"utility_profile": "Decentralized plumbing, modern modular switches"},
    },
    {
        "id": uuid.UUID("33333333-0003-1111-1111-111111111111"),
        "code": "GH-003",
        "name": "Ramana Towers",
        "name_tamil": "ரமண டவர்ஸ்",
        "type": "guest_house",
        "room_count": 30,
        "extra_data": {"utility_profile": "High-pressure plumbing systems, AC infrastructure"},
    },
    {
        "id": uuid.UUID("33333333-0004-1111-1111-111111111111"),
        "code": "GH-004",
        "name": "Vedapatasala Quarters",
        "name_tamil": "வேதபாடசாலை குடியிருப்பு",
        "type": "guest_house",
        "room_count": 15,
        "extra_data": {"utility_profile": "Basic utilities, robust drainage requirements"},
    },
    {
        "id": uuid.UUID("33333333-0005-1111-1111-111111111111"),
        "code": "GH-005",
        "name": "Peripheral Sites A",
        "name_tamil": "புற வளாகம் A",
        "type": "guest_house",
        "room_count": 20,
        "extra_data": {"utility_profile": "Borewell dependent, standalone pump controls"},
    },
]

# Farm locations
FARM_LOCATIONS = [
    {
        "id": uuid.UUID("33333333-1001-1111-1111-111111111111"),
        "code": "NPP-FARM",
        "name": "Nallavanpalem Farm",
        "name_tamil": "நல்லவன்பாளேம் பண்ணை",
        "type": "farm",
        "area_sqm": Decimal("40468.6"),  # ~10 acres
    },
]

# Farm fields/blocks (matching mock data)
FARM_FIELDS = [
    {
        "id": uuid.UUID("44444444-0001-1111-1111-111111111111"),
        "code": "F001",
        "name": "North Field",
        "name_tamil": "வடக்கு வயல்",
        "field_type": "grass_block",
        "area_acres": Decimal("5.5"),
        "soil_type": "red_loam",
        "irrigation_type": "canal",
        "current_crop": "Paddy",
        "current_crop_tamil": "நெல்",
    },
    {
        "id": uuid.UUID("44444444-0002-1111-1111-111111111111"),
        "code": "F002",
        "name": "South Field",
        "name_tamil": "தெற்கு வயல்",
        "field_type": "grass_block",
        "area_acres": Decimal("3.2"),
        "soil_type": "red_loam",
        "irrigation_type": "canal",
        "current_crop": "Sugarcane",
        "current_crop_tamil": "கரும்பு",
    },
    {
        "id": uuid.UUID("44444444-0003-1111-1111-111111111111"),
        "code": "F003",
        "name": "East Garden",
        "name_tamil": "கிழக்கு தோட்டம்",
        "field_type": "mixed",
        "area_acres": Decimal("2.0"),
        "soil_type": "sandy_loam",
        "irrigation_type": "drip",
        "current_crop": "Vegetables",
        "current_crop_tamil": "காய்கறிகள்",
    },
    {
        "id": uuid.UUID("44444444-0004-1111-1111-111111111111"),
        "code": "F004",
        "name": "Coconut Grove",
        "name_tamil": "தென்னந்தோப்பு",
        "field_type": "horticulture",
        "area_acres": Decimal("4.0"),
        "soil_type": "sandy_loam",
        "irrigation_type": "drip",
        "current_crop": "Coconut",
        "current_crop_tamil": "தேங்காய்",
    },
    {
        "id": uuid.UUID("44444444-0005-1111-1111-111111111111"),
        "code": "F005",
        "name": "Banana Plantation",
        "name_tamil": "வாழைத் தோட்டம்",
        "field_type": "horticulture",
        "area_acres": Decimal("1.5"),
        "soil_type": "alluvial",
        "irrigation_type": "drip",
        "current_crop": "Banana",
        "current_crop_tamil": "வாழைப்பழம்",
    },
    {
        "id": uuid.UUID("44444444-0006-1111-1111-111111111111"),
        "code": "GRASS-01",
        "name": "Super Napier Block",
        "name_tamil": "சூப்பர் நேப்பியர் தொகுதி",
        "field_type": "grass_block",
        "area_acres": Decimal("1.5"),
        "soil_type": "red_loam",
        "irrigation_type": "canal",
        "current_crop": "Super Napier",
        "current_crop_tamil": "சூப்பர் நேப்பியர்",
    },
    {
        "id": uuid.UUID("44444444-0007-1111-1111-111111111111"),
        "code": "GRASS-02",
        "name": "CO-5 Block",
        "name_tamil": "CO-5 தொகுதி",
        "field_type": "grass_block",
        "area_acres": Decimal("1.0"),
        "soil_type": "red_loam",
        "irrigation_type": "canal",
        "current_crop": "CO-5 Grass",
        "current_crop_tamil": "CO-5 புல்",
    },
]

# Crop varieties (from requirements)
CROP_VARIETIES = [
    {
        "id": uuid.UUID("55555555-0001-1111-1111-111111111111"),
        "code": "SUPER_NAPIER",
        "name": "Super Napier",
        "name_tamil": "சூப்பர் நேப்பியர்",
        "category": "multi_cut_grass",
        "growth_type": "long_term",
        "first_harvest_days": 75,
        "subsequent_harvest_days": 45,
        "lifespan_years": Decimal("5.0"),
        "water_requirement": "high",
        "nutrition_profile": {"protein_pct": 10, "fiber_pct": 32},
    },
    {
        "id": uuid.UUID("55555555-0002-1111-1111-111111111111"),
        "code": "CO4",
        "name": "CO-4 Grass",
        "name_tamil": "CO-4 புல்",
        "category": "multi_cut_grass",
        "growth_type": "long_term",
        "first_harvest_days": 90,
        "subsequent_harvest_days": 45,
        "lifespan_years": Decimal("4.0"),
        "water_requirement": "medium",
    },
    {
        "id": uuid.UUID("55555555-0003-1111-1111-111111111111"),
        "code": "CO5",
        "name": "CO-5 Grass",
        "name_tamil": "CO-5 புல்",
        "category": "multi_cut_grass",
        "growth_type": "long_term",
        "first_harvest_days": 90,
        "subsequent_harvest_days": 45,
        "lifespan_years": Decimal("4.0"),
        "water_requirement": "medium",
    },
    {
        "id": uuid.UUID("55555555-0004-1111-1111-111111111111"),
        "code": "HYBRID_NAPIER",
        "name": "Hybrid Napier",
        "name_tamil": "கலப்பின நேப்பியர்",
        "category": "multi_cut_grass",
        "growth_type": "long_term",
        "first_harvest_days": 75,
        "subsequent_harvest_days": 45,
        "lifespan_years": Decimal("3.0"),
        "water_requirement": "high",
    },
    {
        "id": uuid.UUID("55555555-0005-1111-1111-111111111111"),
        "code": "COWPEA",
        "name": "Cowpea",
        "name_tamil": "காராமணி",
        "category": "single_cut_legume",
        "growth_type": "short_term",
        "first_harvest_days": 60,
        "water_requirement": "medium",
        "nutrition_profile": {"protein_pct": 24, "fiber_pct": 10},
    },
    {
        "id": uuid.UUID("55555555-0006-1111-1111-111111111111"),
        "code": "HEDGE_LUCERNE",
        "name": "Hedge Lucerne",
        "name_tamil": "வேலிமசால்",
        "category": "single_cut_legume",
        "growth_type": "short_term",
        "first_harvest_days": 75,
        "water_requirement": "low",
        "nutrition_profile": {"protein_pct": 20, "fiber_pct": 15},
    },
    {
        "id": uuid.UUID("55555555-0007-1111-1111-111111111111"),
        "code": "AFRICAN_MAIZE",
        "name": "African Tall Maize",
        "name_tamil": "ஆப்பிரிக்க சோளம்",
        "category": "single_cut_legume",
        "growth_type": "short_term",
        "first_harvest_days": 80,
        "water_requirement": "high",
    },
    {
        "id": uuid.UUID("55555555-0008-1111-1111-111111111111"),
        "code": "AZOLLA",
        "name": "Azolla",
        "name_tamil": "அசோலா",
        "category": "cover_crop",
        "growth_type": "short_term",
        "first_harvest_days": 7,
        "subsequent_harvest_days": 7,
        "water_requirement": "high",
        "nutrition_profile": {"protein_pct": 25, "fiber_pct": 8},
    },
]

# Asset categories (from requirements)
ASSET_CATEGORIES = [
    # Plumbing
    {"id": uuid.UUID("66666666-0001-1111-1111-111111111111"), "code": "WATER_SUPPLY", "name": "Water Supply", "name_tamil": "நீர் வழங்கல்", "domain": "plumbing", "default_maintenance_days": 180},
    {"id": uuid.UUID("66666666-0002-1111-1111-111111111111"), "code": "STORAGE_HEATING", "name": "Storage & Heating", "name_tamil": "சேமிப்பு & வெப்பமாக்கல்", "domain": "plumbing", "default_maintenance_days": 90},
    {"id": uuid.UUID("66666666-0003-1111-1111-111111111111"), "code": "SANITARY", "name": "Sanitary Fixtures", "name_tamil": "சுகாதார பொருத்துதல்கள்", "domain": "plumbing", "default_maintenance_days": 365},
    {"id": uuid.UUID("66666666-0004-1111-1111-111111111111"), "code": "DISTRIBUTION", "name": "Distribution", "name_tamil": "விநியோகம்", "domain": "plumbing", "default_maintenance_days": 365},
    # Electrical
    {"id": uuid.UUID("66666666-0005-1111-1111-111111111111"), "code": "DIST_BOARD", "name": "Distribution Boards", "name_tamil": "மின் பலகைகள்", "domain": "electrical", "default_maintenance_days": 365},
    {"id": uuid.UUID("66666666-0006-1111-1111-111111111111"), "code": "ENVIRONMENTAL", "name": "Environmental", "name_tamil": "சுற்றுச்சூழல்", "domain": "electrical", "default_maintenance_days": 180},
    {"id": uuid.UUID("66666666-0007-1111-1111-111111111111"), "code": "LIGHTING", "name": "Lighting", "name_tamil": "விளக்குகள்", "domain": "electrical", "default_maintenance_days": 365},
    {"id": uuid.UUID("66666666-0008-1111-1111-111111111111"), "code": "CONNECTIVITY", "name": "Connectivity", "name_tamil": "இணைப்பு", "domain": "electrical", "default_maintenance_days": 365},
]

# Inventory items (consumables from requirements)
INVENTORY_ITEMS = [
    # Plumbing consumables
    {"id": uuid.UUID("77777777-0001-1111-1111-111111111111"), "sku": "PLB-001", "name": "Teflon Tape", "name_tamil": "டெஃப்லான் டேப்", "category": "plumbing", "unit": "roll", "unit_tamil": "சுருள்", "criticality": "high", "min_stock_level": 20, "reorder_point": 10, "unit_price": Decimal("15.00")},
    {"id": uuid.UUID("77777777-0002-1111-1111-111111111111"), "sku": "PLB-002", "name": "Rubber Washer", "name_tamil": "ரப்பர் வாஷர்", "category": "plumbing", "unit": "piece", "unit_tamil": "துண்டு", "criticality": "high", "min_stock_level": 50, "reorder_point": 25, "unit_price": Decimal("5.00")},
    {"id": uuid.UUID("77777777-0003-1111-1111-111111111111"), "sku": "PLB-003", "name": "PVC Solvent", "name_tamil": "PVC கரைப்பான்", "category": "plumbing", "unit": "tin", "unit_tamil": "டின்", "criticality": "high", "min_stock_level": 5, "reorder_point": 2, "unit_price": Decimal("120.00")},
    {"id": uuid.UUID("77777777-0004-1111-1111-111111111111"), "sku": "PLB-004", "name": "Silicone Sealant", "name_tamil": "சிலிகான் சீலண்ட்", "category": "plumbing", "unit": "tube", "unit_tamil": "குழாய்", "criticality": "high", "min_stock_level": 10, "reorder_point": 5, "unit_price": Decimal("180.00")},
    {"id": uuid.UUID("77777777-0005-1111-1111-111111111111"), "sku": "PLB-005", "name": "CPVC Pipe 1/2\"", "name_tamil": "CPVC குழாய் 1/2\"", "category": "plumbing", "unit": "meter", "unit_tamil": "மீட்டர்", "criticality": "medium", "min_stock_level": 20, "reorder_point": 10, "unit_price": Decimal("45.00")},
    {"id": uuid.UUID("77777777-0006-1111-1111-111111111111"), "sku": "PLB-006", "name": "CPVC Elbow 1/2\"", "name_tamil": "CPVC எல்போ 1/2\"", "category": "plumbing", "unit": "piece", "unit_tamil": "துண்டு", "criticality": "medium", "min_stock_level": 20, "reorder_point": 10, "unit_price": Decimal("12.00")},
    # Electrical consumables
    {"id": uuid.UUID("77777777-0011-1111-1111-111111111111"), "sku": "ELC-001", "name": "PVC Tape Red", "name_tamil": "PVC டேப் சிவப்பு", "category": "electrical", "unit": "roll", "unit_tamil": "சுருள்", "criticality": "high", "min_stock_level": 20, "reorder_point": 10, "unit_price": Decimal("25.00")},
    {"id": uuid.UUID("77777777-0012-1111-1111-111111111111"), "sku": "ELC-002", "name": "PVC Tape Black", "name_tamil": "PVC டேப் கருப்பு", "category": "electrical", "unit": "roll", "unit_tamil": "சுருள்", "criticality": "high", "min_stock_level": 20, "reorder_point": 10, "unit_price": Decimal("25.00")},
    {"id": uuid.UUID("77777777-0013-1111-1111-111111111111"), "sku": "ELC-003", "name": "Wire Lug 2.5mm", "name_tamil": "வயர் லக் 2.5mm", "category": "electrical", "unit": "pack", "unit_tamil": "பேக்", "criticality": "high", "min_stock_level": 10, "reorder_point": 5, "unit_price": Decimal("35.00")},
    {"id": uuid.UUID("77777777-0014-1111-1111-111111111111"), "sku": "ELC-004", "name": "Copper Wire 1.5sqmm", "name_tamil": "தாமிர கம்பி 1.5sqmm", "category": "electrical", "unit": "meter", "unit_tamil": "மீட்டர்", "criticality": "medium", "min_stock_level": 50, "reorder_point": 25, "unit_price": Decimal("18.00")},
    {"id": uuid.UUID("77777777-0015-1111-1111-111111111111"), "sku": "ELC-005", "name": "Fan Capacitor 2.5mfd", "name_tamil": "விசிறி கப்பாசிட்டர் 2.5mfd", "category": "electrical", "unit": "piece", "unit_tamil": "துண்டு", "criticality": "medium", "min_stock_level": 10, "reorder_point": 5, "unit_price": Decimal("65.00")},
    {"id": uuid.UUID("77777777-0016-1111-1111-111111111111"), "sku": "ELC-006", "name": "LED Bulb 9W", "name_tamil": "LED பல்ப் 9W", "category": "electrical", "unit": "piece", "unit_tamil": "துண்டு", "criticality": "medium", "min_stock_level": 20, "reorder_point": 10, "unit_price": Decimal("85.00")},
    # Hardware
    {"id": uuid.UUID("77777777-0021-1111-1111-111111111111"), "sku": "HW-001", "name": "Screws Assorted", "name_tamil": "திருகுகள் கலவை", "category": "hardware", "unit": "box", "unit_tamil": "பெட்டி", "criticality": "low", "min_stock_level": 5, "reorder_point": 2, "unit_price": Decimal("150.00")},
    {"id": uuid.UUID("77777777-0022-1111-1111-111111111111"), "sku": "HW-002", "name": "Wall Plugs (Gitti)", "name_tamil": "சுவர் பிளக்", "category": "hardware", "unit": "pack", "unit_tamil": "பேக்", "criticality": "low", "min_stock_level": 10, "reorder_point": 5, "unit_price": Decimal("40.00")},
    {"id": uuid.UUID("77777777-0023-1111-1111-111111111111"), "sku": "HW-003", "name": "M-Seal", "name_tamil": "M-சீல்", "category": "hardware", "unit": "pack", "unit_tamil": "பேக்", "criticality": "medium", "min_stock_level": 10, "reorder_point": 5, "unit_price": Decimal("75.00")},
]

# Checklist templates (from requirements - watering checklist)
CHECKLIST_TEMPLATES = [
    {
        "id": uuid.UUID("88888888-0001-1111-1111-111111111111"),
        "module": "farm",
        "task_type": "watering",
        "name": "Field Watering Checklist",
        "name_tamil": "வயல் பாசன சரிபார்ப்பு பட்டியல்",
        "items": [
            {"step": 1, "text": "Check the ground - verify soil moisture and previous watering dates", "text_tamil": "தரையை சரிபார்க்கவும் - மண் ஈரப்பதம் மற்றும் முந்தைய பாசன தேதிகளை சரிபார்க்கவும்", "is_required": True},
            {"step": 2, "text": "Check the pipes - ensure all delivery pipe caps are tight and no leaks", "text_tamil": "குழாய்களை சரிபார்க்கவும் - அனைத்து குழாய் மூடிகள் இறுக்கமாக உள்ளதா, கசிவு இல்லை என்பதை உறுதி செய்யவும்", "is_required": True},
            {"step": 3, "text": "Clear the path - remove trash/mud blocking trenches", "text_tamil": "பாதையை சுத்தம் செய்யவும் - அகழிகளை அடைக்கும் குப்பை/சேற்றை அகற்றவும்", "is_required": True},
            {"step": 4, "text": "Set the gates - open main canal entry, close last gate", "text_tamil": "வாயில்களை அமைக்கவும் - முக்கிய கால்வாய் நுழைவை திறக்கவும், கடைசி வாயிலை மூடவும்", "is_required": True},
            {"step": 5, "text": "Power check - confirm no scheduled power cuts", "text_tamil": "மின்சார சோதனை - திட்டமிடப்பட்ட மின்வெட்டு இல்லை என்பதை உறுதிப்படுத்தவும்", "is_required": True},
        ],
    },
    {
        "id": uuid.UUID("88888888-0002-1111-1111-111111111111"),
        "module": "farm",
        "task_type": "watering",
        "name": "Fertilizer Mixing Checklist",
        "name_tamil": "உரம் கலக்கும் சரிபார்ப்பு பட்டியல்",
        "items": [
            {"step": 1, "text": "Ensure fertilizer is prepared in advance in sufficient quantity", "text_tamil": "உரம் போதுமான அளவில் முன்கூட்டியே தயாரிக்கப்பட்டிருப்பதை உறுதி செய்யவும்", "is_required": True},
            {"step": 2, "text": "Place fertilizer drum at start of water channel", "text_tamil": "உர டிரம்மை நீர் வாய்க்காலின் தொடக்கத்தில் வைக்கவும்", "is_required": True},
            {"step": 3, "text": "Carry required number of cans to fill the solution", "text_tamil": "கரைசலை நிரப்ப தேவையான எண்ணிக்கையிலான கேன்களை எடுத்துச் செல்லவும்", "is_required": True},
            {"step": 4, "text": "Pre-mix the solution before water starts", "text_tamil": "நீர் தொடங்குவதற்கு முன் கரைசலை கலக்கவும்", "is_required": True},
            {"step": 5, "text": "Test the delivery tube and valve - not clogged", "text_tamil": "டெலிவரி குழாய் மற்றும் வால்வை சோதிக்கவும் - அடைப்பு இல்லை", "is_required": True},
            {"step": 6, "text": "Keep spare fertilizer solution nearby", "text_tamil": "உபரி உர கரைசலை அருகில் வைக்கவும்", "is_required": False},
        ],
    },
    {
        "id": uuid.UUID("88888888-0003-1111-1111-111111111111"),
        "module": "farm",
        "task_type": "watering",
        "name": "Watering Completion Checklist",
        "name_tamil": "பாசன முடிவு சரிபார்ப்பு பட்டியல்",
        "items": [
            {"step": 1, "text": "Verify water reaches last row, turn off motor immediately", "text_tamil": "நீர் கடைசி வரிசையை அடைகிறதா சரிபார்க்கவும், உடனடியாக மோட்டாரை அணைக்கவும்", "is_required": True},
            {"step": 2, "text": "Clean the hose - wash and coil neatly", "text_tamil": "குழாயை சுத்தம் செய்யவும் - கழுவி நேர்த்தியாக சுருட்டவும்", "is_required": True},
            {"step": 3, "text": "Store all equipment - clean drums, cans, tools", "text_tamil": "அனைத்து உபகரணங்களையும் சேமிக்கவும் - டிரம்கள், கேன்கள், கருவிகளை சுத்தம் செய்யவும்", "is_required": True},
            {"step": 4, "text": "Report to supervisor - finish time, problems, suggestions", "text_tamil": "மேற்பார்வையாளரிடம் தெரிவிக்கவும் - முடிவு நேரம், சிக்கல்கள், பரிந்துரைகள்", "is_required": True},
            {"step": 5, "text": "Reset valves for other farm areas", "text_tamil": "மற்ற பண்ணை பகுதிகளுக்கு வால்வுகளை மீட்டமைக்கவும்", "is_required": True},
        ],
    },
]


# Sample day schedules and tasks
# These will be created dynamically based on today's date
def get_sample_schedules_and_tasks():
    """Generate sample schedules for today and tomorrow."""
    tz = pytz.timezone('Asia/Kolkata')
    today = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    # Worker IDs
    RAJA_ID = uuid.UUID("22222222-3333-1111-1111-111111111111")
    MURUGAN_ID = uuid.UUID("22222222-4444-1111-1111-111111111111")
    KANNAN_ID = uuid.UUID("22222222-4445-1111-1111-111111111111")
    LAKSHMI_ID = uuid.UUID("22222222-4446-1111-1111-111111111111")

    # Field IDs
    NORTH_FIELD_ID = uuid.UUID("44444444-0001-1111-1111-111111111111")
    SOUTH_FIELD_ID = uuid.UUID("44444444-0002-1111-1111-111111111111")
    EAST_GARDEN_ID = uuid.UUID("44444444-0003-1111-1111-111111111111")
    COCONUT_GROVE_ID = uuid.UUID("44444444-0004-1111-1111-111111111111")
    BANANA_PLANTATION_ID = uuid.UUID("44444444-0005-1111-1111-111111111111")

    # Manager ID (creates schedules)
    SELVAM_ID = uuid.UUID("22222222-1112-1111-1111-111111111111")

    # Schedule IDs
    TODAY_SCHEDULE_ID = uuid.UUID("99999999-0001-1111-1111-111111111111")
    TOMORROW_SCHEDULE_ID = uuid.UUID("99999999-0002-1111-1111-111111111111")

    schedules = [
        {
            "id": TODAY_SCHEDULE_ID,
            "schedule_date": today.date(),
            "notes": "Regular daily tasks",
            "notes_tamil": "இன்றைய வழக்கமான வேலைகள்",
            "created_by_id": SELVAM_ID,
            "is_published": True,
        },
        {
            "id": TOMORROW_SCHEDULE_ID,
            "schedule_date": tomorrow.date(),
            "notes": "Tomorrow's schedule - pipeline repair is important",
            "notes_tamil": "நாளை அட்டவணை - குழாய் பழுது பார்ப்பு முக்கியம்",
            "created_by_id": SELVAM_ID,
            "is_published": True,
        },
    ]

    # Today's tasks
    tasks = [
        # Task 1: Completed - Watering grass
        {
            "id": uuid.UUID("88888888-1001-1111-1111-111111111111"),
            "schedule_id": TODAY_SCHEDULE_ID,
            "description": "Water the grass",
            "description_tamil": "புல்வெளிக்கு தண்ணீர் பாய்ச்சுதல்",
            "scheduled_time": today.replace(hour=7, minute=0),
            "category": "watering",
            "field_id": NORTH_FIELD_ID,
            "field_name": "North Field",
            "field_name_tamil": "வடக்கு வயல்",
            "crop_name": "Grass",
            "crop_name_tamil": "புல்",
            "assigned_worker_id": RAJA_ID,
            "assigned_worker_name": "Raja",
            "assigned_worker_name_tamil": "ராஜா",
            "status": "completed",
            "priority": "normal",
            "completed_at": today.replace(hour=7, minute=45),
        },
        # Task 2: Completed - Fertilizer
        {
            "id": uuid.UUID("88888888-1002-1111-1111-111111111111"),
            "schedule_id": TODAY_SCHEDULE_ID,
            "description": "Mix fertilizer and send via channel",
            "description_tamil": "உரம் கலந்து வாய்க்கால் வழியே அனுப்புதல்",
            "scheduled_time": today.replace(hour=8, minute=0),
            "category": "fertilizer",
            "field_id": SOUTH_FIELD_ID,
            "field_name": "South Field",
            "field_name_tamil": "தெற்கு வயல்",
            "crop_name": "Sugarcane",
            "crop_name_tamil": "கரும்பு",
            "assigned_worker_id": MURUGAN_ID,
            "assigned_worker_name": "Murugan",
            "assigned_worker_name_tamil": "முருகன்",
            "status": "completed",
            "priority": "high",
            "completed_at": today.replace(hour=9, minute=30),
            "notes_tamil": "50 கிலோ உரம் பயன்படுத்தப்பட்டது",
        },
        # Task 3: Has Issues - Pump line check
        {
            "id": uuid.UUID("88888888-1003-1111-1111-111111111111"),
            "schedule_id": TODAY_SCHEDULE_ID,
            "description": "Check pump line from motor to last gate",
            "description_tamil": "மோட்டாரிலிருந்து கடைசி கேட் வரை பம்ப் லைன் சரிபார்க்கவும்",
            "scheduled_time": today.replace(hour=10, minute=0),
            "category": "maintenance",
            "field_name": "All Fields",
            "field_name_tamil": "அனைத்து வயல்கள்",
            "assigned_worker_id": RAJA_ID,
            "assigned_worker_name": "Raja",
            "assigned_worker_name_tamil": "ராஜா",
            "status": "has_issues",
            "priority": "urgent",
            "has_issues": True,
            "issue_type": "equipment_failure",
            "issue_description": "Pipeline broken, need plumber",
            "issue_description_tamil": "குழாய் உடைந்துள்ளது, பிளம்பர் வேண்டும்",
        },
        # Task 4: In Progress - Pesticide spray
        {
            "id": uuid.UUID("88888888-1004-1111-1111-111111111111"),
            "schedule_id": TODAY_SCHEDULE_ID,
            "description": "Spray pesticide on vegetables",
            "description_tamil": "காய்கறிகளுக்கு பூச்சிக்கொல்லி தெளிக்கவும்",
            "scheduled_time": today.replace(hour=11, minute=0),
            "category": "pesticide",
            "field_id": EAST_GARDEN_ID,
            "field_name": "East Garden",
            "field_name_tamil": "கிழக்கு தோட்டம்",
            "crop_name": "Vegetables",
            "crop_name_tamil": "காய்கறிகள்",
            "assigned_worker_id": KANNAN_ID,
            "assigned_worker_name": "Kannan",
            "assigned_worker_name_tamil": "கண்ணன்",
            "status": "in_progress",
            "priority": "normal",
        },
        # Task 5: Scheduled - Harvest bananas
        {
            "id": uuid.UUID("88888888-1005-1111-1111-111111111111"),
            "schedule_id": TODAY_SCHEDULE_ID,
            "description": "Harvest ripe bananas",
            "description_tamil": "பழுத்த வாழைப்பழங்களை அறுவடை செய்யவும்",
            "scheduled_time": today.replace(hour=14, minute=0),
            "category": "harvesting",
            "field_id": BANANA_PLANTATION_ID,
            "field_name": "Banana Plantation",
            "field_name_tamil": "வாழைத் தோட்டம்",
            "crop_name": "Banana",
            "crop_name_tamil": "வாழைப்பழம்",
            "assigned_worker_id": LAKSHMI_ID,
            "assigned_worker_name": "Lakshmi",
            "assigned_worker_name_tamil": "லக்ஷ்மி",
            "status": "scheduled",
            "priority": "normal",
        },
        # Task 6: Scheduled - Water coconut trees
        {
            "id": uuid.UUID("88888888-1006-1111-1111-111111111111"),
            "schedule_id": TODAY_SCHEDULE_ID,
            "description": "Water coconut trees",
            "description_tamil": "தென்னை மரங்களுக்கு தண்ணீர் ஊற்றவும்",
            "scheduled_time": today.replace(hour=16, minute=0),
            "category": "watering",
            "field_id": COCONUT_GROVE_ID,
            "field_name": "Coconut Grove",
            "field_name_tamil": "தென்னந்தோப்பு",
            "crop_name": "Coconut",
            "crop_name_tamil": "தேங்காய்",
            "assigned_worker_id": MURUGAN_ID,
            "assigned_worker_name": "Murugan",
            "assigned_worker_name_tamil": "முருகன்",
            "status": "scheduled",
            "priority": "normal",
        },
        # Tomorrow's tasks
        {
            "id": uuid.UUID("88888888-2001-1111-1111-111111111111"),
            "schedule_id": TOMORROW_SCHEDULE_ID,
            "description": "Morning watering - North Field",
            "description_tamil": "காலை நீர்ப்பாசனம் - வடக்கு வயல்",
            "scheduled_time": tomorrow.replace(hour=6, minute=30),
            "category": "watering",
            "field_id": NORTH_FIELD_ID,
            "field_name": "North Field",
            "field_name_tamil": "வடக்கு வயல்",
            "crop_name": "Paddy",
            "crop_name_tamil": "நெல்",
            "assigned_worker_id": RAJA_ID,
            "assigned_worker_name": "Raja",
            "assigned_worker_name_tamil": "ராஜா",
            "status": "scheduled",
            "priority": "high",
        },
        {
            "id": uuid.UUID("88888888-2002-1111-1111-111111111111"),
            "schedule_id": TOMORROW_SCHEDULE_ID,
            "description": "Apply organic fertilizer",
            "description_tamil": "இயற்கை உரம் இடுதல்",
            "scheduled_time": tomorrow.replace(hour=8, minute=0),
            "category": "fertilizer",
            "field_id": EAST_GARDEN_ID,
            "field_name": "East Garden",
            "field_name_tamil": "கிழக்கு தோட்டம்",
            "crop_name": "Vegetables",
            "crop_name_tamil": "காய்கறிகள்",
            "assigned_worker_id": KANNAN_ID,
            "assigned_worker_name": "Kannan",
            "assigned_worker_name_tamil": "கண்ணன்",
            "status": "scheduled",
            "priority": "normal",
        },
        {
            "id": uuid.UUID("88888888-2003-1111-1111-111111111111"),
            "schedule_id": TOMORROW_SCHEDULE_ID,
            "description": "Repair broken pipeline",
            "description_tamil": "உடைந்த குழாயை சரி செய்யவும்",
            "scheduled_time": tomorrow.replace(hour=9, minute=0),
            "category": "maintenance",
            "field_id": NORTH_FIELD_ID,
            "field_name": "North Field",
            "field_name_tamil": "வடக்கு வயல்",
            "assigned_worker_id": RAJA_ID,
            "assigned_worker_name": "Raja",
            "assigned_worker_name_tamil": "ராஜா",
            "status": "scheduled",
            "priority": "urgent",
            "notes_tamil": "பிளம்பர் வருவார், உதவி செய்யவும்",
        },
        {
            "id": uuid.UUID("88888888-2004-1111-1111-111111111111"),
            "schedule_id": TOMORROW_SCHEDULE_ID,
            "description": "Inspect sugarcane growth",
            "description_tamil": "கரும்பு வளர்ச்சியை ஆய்வு செய்யவும்",
            "scheduled_time": tomorrow.replace(hour=10, minute=30),
            "category": "inspection",
            "field_id": SOUTH_FIELD_ID,
            "field_name": "South Field",
            "field_name_tamil": "தெற்கு வயல்",
            "crop_name": "Sugarcane",
            "crop_name_tamil": "கரும்பு",
            "assigned_worker_id": MURUGAN_ID,
            "assigned_worker_name": "Murugan",
            "assigned_worker_name_tamil": "முருகன்",
            "status": "scheduled",
            "priority": "normal",
        },
        {
            "id": uuid.UUID("88888888-2005-1111-1111-111111111111"),
            "schedule_id": TOMORROW_SCHEDULE_ID,
            "description": "Transport harvested bananas",
            "description_tamil": "அறுவடை செய்த வாழைப்பழங்களை கொண்டு செல்லவும்",
            "scheduled_time": tomorrow.replace(hour=14, minute=0),
            "category": "transport",
            "field_id": BANANA_PLANTATION_ID,
            "field_name": "Banana Plantation",
            "field_name_tamil": "வாழைத் தோட்டம்",
            "crop_name": "Banana",
            "crop_name_tamil": "வாழைப்பழம்",
            "assigned_worker_id": LAKSHMI_ID,
            "assigned_worker_name": "Lakshmi",
            "assigned_worker_name_tamil": "லக்ஷ்மி",
            "status": "scheduled",
            "priority": "normal",
        },
    ]

    # Task updates (responses/completions)
    task_updates = [
        {
            "id": uuid.UUID("77777777-0001-1111-1111-111111111111"),
            "task_id": uuid.UUID("88888888-1001-1111-1111-111111111111"),
            "worker_id": RAJA_ID,
            "worker_name": "ராஜா",
            "status": "completed",
            "timestamp": today.replace(hour=7, minute=45),
            "notes_tamil": "வேலை முடிந்தது",
        },
        {
            "id": uuid.UUID("77777777-0002-1111-1111-111111111111"),
            "task_id": uuid.UUID("88888888-1002-1111-1111-111111111111"),
            "worker_id": MURUGAN_ID,
            "worker_name": "முருகன்",
            "status": "completed",
            "timestamp": today.replace(hour=9, minute=30),
            "notes_tamil": "50 கிலோ உரம் பயன்படுத்தப்பட்டது",
        },
        {
            "id": uuid.UUID("77777777-0003-1111-1111-111111111111"),
            "task_id": uuid.UUID("88888888-1003-1111-1111-111111111111"),
            "worker_id": RAJA_ID,
            "worker_name": "ராஜா",
            "status": "has_issues",
            "timestamp": today.replace(hour=10, minute=45),
            "notes_tamil": "குழாய் உடைந்துள்ளது, பிளம்பர் வேண்டும்",
            "issue_type": "equipment_failure",
            "issue_description_tamil": "வடக்கு வயலுக்கு போகும் குழாய் உடைந்துள்ளது. பழுது பார்க்க வேண்டும்.",
        },
    ]

    return schedules, tasks, task_updates


async def seed_database(db_url: str, force: bool = False):
    """Seed the database with initial data."""
    engine = create_async_engine(db_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n" + "=" * 60)
        print("SEEDING DATABASE")
        print("=" * 60)

        # Check if data already exists
        result = await session.execute(text("SELECT COUNT(*) FROM organizations"))
        count = result.scalar()
        if count > 0:
            if not force:
                print("\nDatabase already seeded. Use --force to reseed.")
                return
            else:
                print("\nForce mode: Clearing existing data...")
                # Delete in correct order to respect foreign key constraints
                await session.execute(text("DELETE FROM task_updates"))
                await session.execute(text("DELETE FROM scheduled_tasks"))
                await session.execute(text("DELETE FROM day_schedules"))
                await session.execute(text("DELETE FROM checklist_templates"))
                await session.execute(text("DELETE FROM inventory_items"))
                await session.execute(text("DELETE FROM asset_categories"))
                await session.execute(text("DELETE FROM fields"))
                await session.execute(text("DELETE FROM crop_varieties"))
                await session.execute(text("DELETE FROM locations"))
                await session.execute(text("DELETE FROM users"))
                await session.execute(text("DELETE FROM organizations"))
                await session.commit()
                print("   Existing data cleared.")

        # 1. Seed Organization
        print("\n1. Seeding Organization...")
        await session.execute(
            text("""
                INSERT INTO organizations (id, name, name_tamil, code, type, description, settings)
                VALUES (:id, :name, :name_tamil, :code, :type, :description, :settings)
            """),
            {**ORGANIZATION, "settings": str(ORGANIZATION["settings"]).replace("'", '"')},
        )

        # 2. Seed Users
        print("2. Seeding Users...")
        for user in USERS:
            pin_hash = hash_pin(user.get("pin", "0000"))
            password_hash = hash_password(user["password"]) if "password" in user else None
            await session.execute(
                text("""
                    INSERT INTO users (id, org_id, employee_code, name, name_tamil, phone, email, role, department, pin_hash, password_hash)
                    VALUES (:id, :org_id, :employee_code, :name, :name_tamil, :phone, :email, :role, :department, :pin_hash, :password_hash)
                """),
                {
                    "id": user["id"],
                    "org_id": ORG_ID,
                    "employee_code": user["employee_code"],
                    "name": user["name"],
                    "name_tamil": user.get("name_tamil"),
                    "phone": user.get("phone"),
                    "email": user.get("email"),
                    "role": user["role"],
                    "department": user["department"],
                    "pin_hash": pin_hash,
                    "password_hash": password_hash,
                },
            )
        print(f"   Created {len(USERS)} users")

        # 3. Seed Guest Houses (Locations)
        print("3. Seeding Guest Houses...")
        for gh in GUEST_HOUSES:
            qr_code = f"LOC-{gh['code']}"
            await session.execute(
                text("""
                    INSERT INTO locations (id, org_id, code, name, name_tamil, type, qr_code, extra_data)
                    VALUES (:id, :org_id, :code, :name, :name_tamil, :type, :qr_code, :extra_data)
                """),
                {
                    "id": gh["id"],
                    "org_id": ORG_ID,
                    "code": gh["code"],
                    "name": gh["name"],
                    "name_tamil": gh.get("name_tamil"),
                    "type": gh["type"],
                    "qr_code": qr_code,
                    "extra_data": str(gh.get("extra_data", {})).replace("'", '"'),
                },
            )

            # Create rooms for each guest house
            for room_num in range(1, gh["room_count"] + 1):
                room_id = uuid.uuid4()
                room_code = f"{gh['code']}-R{room_num:03d}"
                await session.execute(
                    text("""
                        INSERT INTO locations (id, org_id, parent_id, code, name, name_tamil, type, qr_code)
                        VALUES (:id, :org_id, :parent_id, :code, :name, :name_tamil, :type, :qr_code)
                    """),
                    {
                        "id": room_id,
                        "org_id": ORG_ID,
                        "parent_id": gh["id"],
                        "code": room_code,
                        "name": f"Room {room_num}",
                        "name_tamil": f"அறை {room_num}",
                        "type": "room",
                        "qr_code": f"LOC-{room_code}",
                    },
                )
        print(f"   Created {len(GUEST_HOUSES)} guest houses with rooms")

        # 4. Seed Farm Location
        print("4. Seeding Farm Location...")
        for farm in FARM_LOCATIONS:
            await session.execute(
                text("""
                    INSERT INTO locations (id, org_id, code, name, name_tamil, type, area_sqm, qr_code)
                    VALUES (:id, :org_id, :code, :name, :name_tamil, :type, :area_sqm, :qr_code)
                """),
                {
                    "id": farm["id"],
                    "org_id": ORG_ID,
                    "code": farm["code"],
                    "name": farm["name"],
                    "name_tamil": farm.get("name_tamil"),
                    "type": farm["type"],
                    "area_sqm": farm.get("area_sqm"),
                    "qr_code": f"LOC-{farm['code']}",
                },
            )

        # 5. Seed Crop Varieties
        print("5. Seeding Crop Varieties...")
        for crop in CROP_VARIETIES:
            await session.execute(
                text("""
                    INSERT INTO crop_varieties (id, code, name, name_tamil, category, growth_type, first_harvest_days, subsequent_harvest_days, lifespan_years, water_requirement, nutrition_profile)
                    VALUES (:id, :code, :name, :name_tamil, :category, :growth_type, :first_harvest_days, :subsequent_harvest_days, :lifespan_years, :water_requirement, :nutrition_profile)
                """),
                {
                    "id": crop["id"],
                    "code": crop["code"],
                    "name": crop["name"],
                    "name_tamil": crop.get("name_tamil"),
                    "category": crop["category"],
                    "growth_type": crop.get("growth_type"),
                    "first_harvest_days": crop.get("first_harvest_days"),
                    "subsequent_harvest_days": crop.get("subsequent_harvest_days"),
                    "lifespan_years": crop.get("lifespan_years"),
                    "water_requirement": crop.get("water_requirement"),
                    "nutrition_profile": str(crop.get("nutrition_profile", {})).replace("'", '"') if crop.get("nutrition_profile") else None,
                },
            )
        print(f"   Created {len(CROP_VARIETIES)} crop varieties")

        # 6. Seed Farm Fields
        print("6. Seeding Farm Fields...")
        farm_location_id = FARM_LOCATIONS[0]["id"]
        for field in FARM_FIELDS:
            # Create location for field
            field_loc_id = uuid.uuid4()
            await session.execute(
                text("""
                    INSERT INTO locations (id, org_id, parent_id, code, name, name_tamil, type, qr_code)
                    VALUES (:id, :org_id, :parent_id, :code, :name, :name_tamil, :type, :qr_code)
                """),
                {
                    "id": field_loc_id,
                    "org_id": ORG_ID,
                    "parent_id": farm_location_id,
                    "code": field["code"],
                    "name": field["name"],
                    "name_tamil": field.get("name_tamil"),
                    "type": "block",
                    "qr_code": f"LOC-{field['code']}",
                },
            )

            # Create field record
            await session.execute(
                text("""
                    INSERT INTO fields (id, location_id, code, name, name_tamil, field_type, area_acres, soil_type, irrigation_type)
                    VALUES (:id, :location_id, :code, :name, :name_tamil, :field_type, :area_acres, :soil_type, :irrigation_type)
                """),
                {
                    "id": field["id"],
                    "location_id": field_loc_id,
                    "code": field["code"],
                    "name": field["name"],
                    "name_tamil": field.get("name_tamil"),
                    "field_type": field["field_type"],
                    "area_acres": field.get("area_acres"),
                    "soil_type": field.get("soil_type"),
                    "irrigation_type": field.get("irrigation_type"),
                },
            )
        print(f"   Created {len(FARM_FIELDS)} farm fields")

        # 7. Seed Asset Categories
        print("7. Seeding Asset Categories...")
        for cat in ASSET_CATEGORIES:
            await session.execute(
                text("""
                    INSERT INTO asset_categories (id, code, name, name_tamil, domain, default_maintenance_days)
                    VALUES (:id, :code, :name, :name_tamil, :domain, :default_maintenance_days)
                """),
                cat,
            )
        print(f"   Created {len(ASSET_CATEGORIES)} asset categories")

        # 8. Seed Inventory Items
        print("8. Seeding Inventory Items...")
        for item in INVENTORY_ITEMS:
            await session.execute(
                text("""
                    INSERT INTO inventory_items (id, org_id, sku, name, name_tamil, category, unit, unit_tamil, criticality, min_stock_level, reorder_point, unit_price)
                    VALUES (:id, :org_id, :sku, :name, :name_tamil, :category, :unit, :unit_tamil, :criticality, :min_stock_level, :reorder_point, :unit_price)
                """),
                {**item, "org_id": ORG_ID},
            )
        print(f"   Created {len(INVENTORY_ITEMS)} inventory items")

        # 9. Seed Checklist Templates
        print("9. Seeding Checklist Templates...")
        for template in CHECKLIST_TEMPLATES:
            import json
            await session.execute(
                text("""
                    INSERT INTO checklist_templates (id, org_id, module, task_type, name, name_tamil, items)
                    VALUES (:id, :org_id, :module, :task_type, :name, :name_tamil, :items)
                """),
                {
                    "id": template["id"],
                    "org_id": ORG_ID,
                    "module": template["module"],
                    "task_type": template["task_type"],
                    "name": template["name"],
                    "name_tamil": template.get("name_tamil"),
                    "items": json.dumps(template["items"]),
                },
            )
        print(f"   Created {len(CHECKLIST_TEMPLATES)} checklist templates")

        # 10. Seed Day Schedules and Tasks
        print("10. Seeding Day Schedules and Tasks...")
        try:
            schedules, tasks, task_updates = get_sample_schedules_and_tasks()

            for schedule in schedules:
                await session.execute(
                    text("""
                        INSERT INTO day_schedules (id, org_id, schedule_date, notes, notes_tamil, created_by_id, is_published)
                        VALUES (:id, :org_id, :schedule_date, :notes, :notes_tamil, :created_by_id, :is_published)
                    """),
                    {**schedule, "org_id": ORG_ID},
                )
            print(f"   Created {len(schedules)} day schedules")

            for task in tasks:
                await session.execute(
                    text("""
                        INSERT INTO scheduled_tasks (
                            id, org_id, schedule_id, description, description_tamil, scheduled_time,
                            category, field_id, field_name, field_name_tamil, crop_name, crop_name_tamil,
                            assigned_worker_id, assigned_worker_name, assigned_worker_name_tamil,
                            status, priority, notes_tamil, completed_at, has_issues, issue_type,
                            issue_description, issue_description_tamil
                        )
                        VALUES (
                            :id, :org_id, :schedule_id, :description, :description_tamil, :scheduled_time,
                            :category, :field_id, :field_name, :field_name_tamil, :crop_name, :crop_name_tamil,
                            :assigned_worker_id, :assigned_worker_name, :assigned_worker_name_tamil,
                            :status, :priority, :notes_tamil, :completed_at, :has_issues, :issue_type,
                            :issue_description, :issue_description_tamil
                        )
                    """),
                    {
                        "id": task["id"],
                        "org_id": ORG_ID,
                        "schedule_id": task.get("schedule_id"),
                        "description": task.get("description"),
                        "description_tamil": task["description_tamil"],
                        "scheduled_time": task["scheduled_time"],
                        "category": task["category"],
                        "field_id": task.get("field_id"),
                        "field_name": task.get("field_name"),
                        "field_name_tamil": task.get("field_name_tamil"),
                        "crop_name": task.get("crop_name"),
                        "crop_name_tamil": task.get("crop_name_tamil"),
                        "assigned_worker_id": task.get("assigned_worker_id"),
                        "assigned_worker_name": task.get("assigned_worker_name"),
                        "assigned_worker_name_tamil": task.get("assigned_worker_name_tamil"),
                        "status": task.get("status", "scheduled"),
                        "priority": task.get("priority", "normal"),
                        "notes_tamil": task.get("notes_tamil"),
                        "completed_at": task.get("completed_at"),
                        "has_issues": task.get("has_issues", False),
                        "issue_type": task.get("issue_type"),
                        "issue_description": task.get("issue_description"),
                        "issue_description_tamil": task.get("issue_description_tamil"),
                    },
                )
            print(f"   Created {len(tasks)} scheduled tasks")

            for update in task_updates:
                await session.execute(
                    text("""
                        INSERT INTO task_updates (
                            id, task_id, worker_id, worker_name, status, timestamp,
                            notes_tamil, issue_type, issue_description_tamil
                        )
                        VALUES (
                            :id, :task_id, :worker_id, :worker_name, :status, :timestamp,
                            :notes_tamil, :issue_type, :issue_description_tamil
                        )
                    """),
                    {
                        "id": update["id"],
                        "task_id": update["task_id"],
                        "worker_id": update["worker_id"],
                        "worker_name": update["worker_name"],
                        "status": update["status"],
                        "timestamp": update["timestamp"],
                        "notes_tamil": update.get("notes_tamil"),
                        "issue_type": update.get("issue_type"),
                        "issue_description_tamil": update.get("issue_description_tamil"),
                    },
                )
            print(f"   Created {len(task_updates)} task updates")
        except Exception as e:
            print(f"   Warning: Could not seed schedules/tasks (table may not exist): {e}")

        await session.commit()

        print("\n" + "=" * 60)
        print("SEED DATA COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nTest Credentials:")
        print("-" * 40)
        print("Admin:       ADMIN001 / PIN: 1234 / Password: admin123")
        print("Manager:     MGR001   / PIN: 0000 / Password: manager123")
        print("Supervisor:  SUP001   / PIN: 1111")
        print("Worker Raja: W001     / PIN: 2222")
        print("Worker Murugan: W002  / PIN: 3333")
        print("Worker Kannan: W003   / PIN: 4444")
        print("Worker Lakshmi: W004  / PIN: 5555")
        print("Maint Sup:   MAINT001 / PIN: 8888")
        print("Electrician: ELEC001  / PIN: 9999")
        print("Plumber:     PLUMB001 / PIN: 1010")
        print("=" * 60 + "\n")


async def main():
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description="Seed the database with initial data")
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force reseed by deleting existing data first"
    )
    args = parser.parse_args()

    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:admin@localhost:5432/srm_maintenance"
    )

    print(f"Connecting to: {db_url.split('@')[1] if '@' in db_url else db_url}")

    try:
        await seed_database(db_url, force=args.force)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'srm_ops_db' exists (createdb srm_ops_db)")
        print("3. Migrations have been applied (alembic upgrade head)")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
