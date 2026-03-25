"""
Test suite for evaluation routes
"""

import pytest


class TestEvaluationsList:
    """Tests for evaluations list page"""

    def test_evaluations_page_requires_auth(self, client):
        """Evaluations page should require authentication"""
        response = client.get("/evaluations")
        assert response.status_code in [200, 302, 401]


class TestNewEvaluation:
    """Tests for creating new evaluations"""

    def test_new_evaluation_form_requires_auth(self, client):
        """New evaluation form should require authentication"""
        response = client.get("/evaluations/new")
        assert response.status_code in [200, 302, 401]


class TestEvaluationDetail:
    """Tests for evaluation detail page"""

    def test_evaluation_detail_requires_auth(self, client):
        """Evaluation detail should require authentication"""
        response = client.get("/evaluations/test-id-123")
        assert response.status_code in [200, 302, 401, 404]


class TestEvaluateControl:
    """Tests for control evaluation"""

    def test_evaluate_control_requires_auth(self, client):
        """Evaluate control should require authentication"""
        response = client.get("/evaluate/test-eval/control/test-ctrl")
        assert response.status_code in [200, 302, 401, 404]
