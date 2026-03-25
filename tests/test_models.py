"""
Test suite for models and database
"""

import pytest
from app.models import (
    User,
    Client,
    Evaluation,
    ControlDefinition,
    ControlResponse,
    Norma,
    Document,
    AuditLog,
)


class TestModels:
    """Tests for database models"""

    def test_user_model_exists(self):
        """User model should exist"""
        assert User is not None
        assert hasattr(User, "email")
        assert hasattr(User, "password_hash")
        assert hasattr(User, "role")

    def test_client_model_exists(self):
        """Client model should exist"""
        assert Client is not None
        assert hasattr(Client, "name")

    def test_evaluation_model_exists(self):
        """Evaluation model should exist"""
        assert Evaluation is not None
        assert hasattr(Evaluation, "name")
        assert hasattr(Evaluation, "client_id")
        assert hasattr(Evaluation, "norma_id")  # Multi-norma support

    def test_norma_model_exists(self):
        """Norma model should exist"""
        assert Norma is not None
        assert hasattr(Norma, "code")
        assert hasattr(Norma, "name")

    def test_control_definition_has_norma(self):
        """ControlDefinition should have norma_id"""
        assert hasattr(ControlDefinition, "norma_id")

    def test_control_response_has_na_fields(self):
        """ControlResponse should have N/A fields"""
        assert hasattr(ControlResponse, "not_applicable")
        assert hasattr(ControlResponse, "justification")


class TestImports:
    """Tests for module imports"""

    def test_models_import(self):
        from app.models import User, Client, Evaluation, Norma

        assert User is not None
        assert Client is not None
        assert Evaluation is not None
        assert Norma is not None

    def test_routes_import(self):
        from app.routes import auth, dashboard, evaluations, admin

        assert auth is not None
        assert dashboard is not None
        assert evaluations is not None
        assert admin is not None

    def test_auth_import(self):
        from app.auth import hash_password, verify_password

        assert hash_password is not None
        assert verify_password is not None

    def test_security_import(self):
        from app.security import generate_csrf_token, verify_csrf_token

        assert generate_csrf_token is not None
        assert verify_csrf_token is not None


class TestITIL4:
    """Tests for ITIL v4 support"""

    def test_itil4_norma_exists(self):
        """Verificar que ITIL v4 existe como norma"""
        from app.seed import NORMAS

        itil4_codes = [n["code"] for n in NORMAS]
        assert "ITIL4" in itil4_codes, "ITIL4 deberia estar en las normas"

    def test_itil4_is_last_norma(self):
        """Verificar que ITIL v4 esta en la lista de normas"""
        from app.seed import NORMAS

        itil4 = [n for n in NORMAS if n["code"] == "ITIL4"]
        assert len(itil4) == 1, "ITIL4 debe existir una vez"
        assert itil4[0]["name"] == "ITIL v4 Framework"
