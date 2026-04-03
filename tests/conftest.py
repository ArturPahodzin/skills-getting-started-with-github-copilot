"""
Test configuration and fixtures for the High School Management System API.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset activities to a known state before each test.
    This fixture ensures test isolation and prevents test pollution.
    """
    # Arrange: Store original state
    original_activities = {
        key: {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }
    
    # Yield to let the test run
    yield
    
    # Cleanup: Restore original state
    for key in activities:
        activities[key]["participants"] = original_activities[key]["participants"].copy()
