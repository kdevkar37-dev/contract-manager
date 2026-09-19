from __future__ import annotations

from backend.app.core.auth import require_roles


# Authentication
require_authenticated = require_roles(
    "admin",
    "manager",
    "viewer",
)


# Contract management
require_contract_manager = require_roles(
    "admin",
    "manager",
)


# Administrative operations
require_admin = require_roles(
    "admin",
)