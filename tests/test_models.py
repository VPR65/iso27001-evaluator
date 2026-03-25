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
        """All models should import without errors"""
        from app.models import (
            User,
            Client,
            Evaluation,
            ControlDefinition,
            ControlResponse,
            Norma,
            Document,
            AuditLog,
            UserRole,
            EvaluationStatus,
        )

        assert True

    def test_routes_import(self):
        """All routes should import without errors"""
        from app.routes import (
            auth,
            dashboard,
            clients,
            evaluations,
            evaluate,
            documents,
            rfcs,
            sprints,
            users,
            admin,
            import_export,
            stats,
            biblioteca,
        )

        assert True

    def test_auth_import(self):
        """Auth module should import without errors"""
        from app.auth import hash_password, verify_password

        assert hash_password is not None
        assert verify_password is not None

    def test_security_import(self):
        """Security module should import without errors"""
        from app.security import generate_csrf_token, verify_csrf_token

        assert generate_csrf_token is not None
        assert verify_csrf_token is not None
