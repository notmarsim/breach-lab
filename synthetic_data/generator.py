"""Deterministic synthetic data generator for Nexora Technologies (nexora.test)."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any


DEPARTMENTS = [
    {"id": "it", "name": "Information Technology", "code": "IT"},
    {"id": "eng", "name": "Engineering", "code": "ENG"},
    {"id": "hr", "name": "Human Resources", "code": "HR"},
    {"id": "fin", "name": "Finance", "code": "FIN"},
    {"id": "sup", "name": "Customer Support", "code": "SUP"},
    {"id": "sal", "name": "Sales", "code": "SAL"},
    {"id": "mkt", "name": "Marketing", "code": "MKT"},
    {"id": "ops", "name": "Operations", "code": "OPS"},
    {"id": "mgmt", "name": "Management", "code": "MGMT"},
]

FIRST_NAMES = [
    "Alice", "Bruno", "Carla", "Diego", "Elena", "Felipe", "Gabriela", "Hugo",
    "Isabela", "Joao", "Karina", "Lucas", "Marina", "Rafael", "Sofia", "Tiago",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Costa", "Ferreira", "Almeida", "Rocha", "Lima",
    "Pereira", "Ribeiro", "Carvalho", "Mendes", "Barbosa", "Nunes", "Araujo", "Cardoso",
]

PRODUCTS = [
    {"sku": "NX-SEC-100", "name": "Nexora Sentinel Gateway", "category": "Security Appliances", "price": 1299.00, "stock": 42},
    {"sku": "NX-LOG-200", "name": "Nexora AuditStream Enterprise", "category": "Software", "price": 499.00, "stock": 150},
    {"sku": "NX-IAM-300", "name": "Nexora Identity Vault", "category": "Identity", "price": 799.00, "stock": 85},
    {"sku": "NX-NET-400", "name": "Nexora NetGuard Sensor", "category": "Hardware", "price": 1899.00, "stock": 19},
    {"sku": "NX-SUP-500", "name": "Nexora 24/7 Enterprise Support", "category": "Services", "price": 2400.00, "stock": 999},
    {"sku": "NX-BAK-600", "name": "Nexora ColdVault Backup", "category": "Storage", "price": 649.00, "stock": 60},
]

COUPONS = [
    {"code": "NEXORA10", "discount_pct": 10, "active": True},
    {"code": "PARTNER20", "discount_pct": 20, "active": True},
    {"code": "LEGACY50", "discount_pct": 50, "active": False},
]


def _synthetic_pw_hash(username: str, seed: int) -> str:
    return hashlib.sha256(f"nexora-synth:{seed}:{username}".encode("utf-8")).hexdigest()


def generate_enterprise_dataset(seed: int = 845921) -> dict[str, Any]:
    """Generate a cohesive, relational synthetic dataset for Nexora Technologies."""
    rng = random.Random(seed)

    employees: list[dict[str, Any]] = []
    used_usernames: set[str] = set()
    for idx in range(18):
        dept = DEPARTMENTS[idx % len(DEPARTMENTS)]
        for _ in range(20):
            fname = rng.choice(FIRST_NAMES)
            lname = rng.choice(LAST_NAMES)
            uname = f"{fname.lower()}.{lname.lower()}"
            if uname not in used_usernames:
                used_usernames.add(uname)
                break
        role = "manager" if idx < 9 else "staff"
        if dept["id"] == "it" and role == "manager":
            role = "sysadmin"
        employees.append(
            {
                "id": f"EMP-{1001 + idx}",
                "username": uname,
                "full_name": f"{fname} {lname}",
                "email": f"{uname}@nexora.test",
                "department_id": dept["id"],
                "department": dept["name"],
                "role": role,
                "title": f"{dept['code']} {'Lead' if role != 'staff' else 'Specialist'}",
                "password_hash": _synthetic_pw_hash(uname, seed),
                "public_profile": True,
            }
        )

    customers: list[dict[str, Any]] = []
    for idx in range(10):
        fname = rng.choice(FIRST_NAMES)
        lname = rng.choice(LAST_NAMES)
        cname = f"{fname.lower()}.{lname.lower()}.{idx + 1}"
        customers.append(
            {
                "id": f"CUST-{2001 + idx}",
                "username": cname,
                "full_name": f"{fname} {lname}",
                "email": f"{cname}@client-example.test",
                "company": f"{lname} Solutions Ltd.",
                "tier": rng.choice(["standard", "business", "enterprise"]),
                "password_hash": _synthetic_pw_hash(cname, seed),
            }
        )

    orders: list[dict[str, Any]] = []
    invoices: list[dict[str, Any]] = []
    tickets: list[dict[str, Any]] = []
    for idx, cust in enumerate(customers):
        prod = PRODUCTS[idx % len(PRODUCTS)]
        qty = rng.randint(1, 3)
        total = round(prod["price"] * qty, 2)
        order_id = f"ORD-{3001 + idx}"
        inv_id = f"INV-{4001 + idx}"
        orders.append(
            {
                "id": order_id,
                "customer_id": cust["id"],
                "sku": prod["sku"],
                "product_name": prod["name"],
                "quantity": qty,
                "total_amount": total,
                "status": rng.choice(["paid", "processing", "shipped"]),
            }
        )
        invoices.append(
            {
                "id": inv_id,
                "order_id": order_id,
                "customer_id": cust["id"],
                "amount": total,
                "currency": "USD",
                "status": "paid" if idx % 3 != 0 else "pending",
            }
        )
        assignee = next((e for e in employees if e["department_id"] == "sup"), employees[0])
        tickets.append(
            {
                "id": f"TCK-{5001 + idx}",
                "customer_id": cust["id"],
                "assignee_id": assignee["id"],
                "subject": f"Support inquiry for {prod['name']}",
                "priority": rng.choice(["low", "medium", "high"]),
                "status": rng.choice(["open", "in_progress", "resolved"]),
            }
        )

    announcements = [
        {
            "id": "ANN-01",
            "title": "Q4 Security & Infrastructure Maintenance Window",
            "department": "Information Technology",
            "summary": "Scheduled internal network segmentation review for DMZ and Database tiers.",
        },
        {
            "id": "ANN-02",
            "title": "Nexora Sentinel Gateway 4.2 Release",
            "department": "Engineering",
            "summary": "New telemetry pipeline and improved audit logging now available for enterprise customers.",
        },
    ]

    emails = [
        {
            "id": "MAIL-01",
            "from": employees[0]["email"],
            "to": employees[1]["email"],
            "subject": "Quarterly Backup Verification",
            "body": "Please confirm the nightly backup rotation on BACKUP01 completed without warnings.",
            "folder": "inbox",
        },
        {
            "id": "MAIL-02",
            "from": employees[3]["email"],
            "to": employees[8]["email"],
            "subject": "Q4 Budget Approvals",
            "body": "Updated vendor invoices are staged in the Finance portal for manager review.",
            "folder": "sent",
        },
    ]

    return {
        "meta": {
            "organization": "Nexora Technologies",
            "domain": "nexora.test",
            "seed": seed,
            "synthetic_only": True,
        },
        "departments": DEPARTMENTS,
        "employees": employees,
        "customers": customers,
        "products": PRODUCTS,
        "coupons": COUPONS,
        "orders": orders,
        "invoices": invoices,
        "tickets": tickets,
        "announcements": announcements,
        "emails": emails,
    }


def export_dataset(output_dir: Path, seed: int = 845921) -> Path:
    """Write the generated dataset to synthetic_data/dataset.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    data = generate_enterprise_dataset(seed=seed)
    target = output_dir / "dataset.json"
    target.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return target
