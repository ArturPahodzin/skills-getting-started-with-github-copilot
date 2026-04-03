"""
Tests for the High School Management System API using AAA (Arrange-Act-Assert) pattern.
"""
import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client, reset_activities):
        """Test that retrieving all activities returns 200 OK."""
        # Arrange
        expected_status = 200
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == expected_status

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that activities endpoint returns a dictionary."""
        # Arrange
        expected_type = dict
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert isinstance(activities_data, expected_type)

    def test_get_activities_contains_core_activities(self, client, reset_activities):
        """Test that the response contains the core activities."""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in activities_data

    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has all required fields."""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_details in activities_data.items():
            for field in required_fields:
                assert field in activity_details, f"Activity '{activity_name}' missing field '{field}'"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_returns_200(self, client, reset_activities):
        """Test that signing up a new participant returns 200 OK."""
        # Arrange
        activity_name = "Basketball Team"
        email = "john.doe@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message."""
        # Arrange
        activity_name = "Basketball Team"
        email = "john.doe@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        result = response.json()
        
        # Assert
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity."""
        # Arrange
        activity_name = "Basketball Team"
        email = "john.doe@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signing up for a nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "john.doe@mergington.edu"
        expected_status = 404
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == expected_status

    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """Test that signing up twice returns 400 Bad Request."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant
        expected_status = 400
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == expected_status

    def test_signup_duplicate_returns_error_message(self, client, reset_activities):
        """Test that duplicate signup returns appropriate error message."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        result = response.json()
        
        # Assert
        assert "already registered" in result["detail"].lower()

    def test_signup_at_max_capacity_returns_400(self, client, reset_activities):
        """Test that signing up when activity is full returns 400."""
        # Arrange
        # Use an activity and fill it up
        activity_name = "Gym Class"
        new_email = "new.participant@mergington.edu"
        
        # First, set up the activity at max capacity
        from src.app import activities
        activities[activity_name]["max_participants"] = 2
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 400


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_existing_participant_returns_200(self, client, reset_activities):
        """Test that unregistering an existing participant returns 200 OK."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        result = response.json()
        
        # Assert
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_unregister_removes_participant_from_activity(self, client, reset_activities):
        """Test that unregister actually removes the participant from the activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        activities_data = response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregistering from a nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "john.doe@mergington.edu"
        expected_status = 404
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == expected_status

    def test_unregister_non_participant_returns_400(self, client, reset_activities):
        """Test that unregistering a non-participant returns 400."""
        # Arrange
        activity_name = "Basketball Team"
        email = "nonexistent@mergington.edu"
        expected_status = 400
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == expected_status

    def test_unregister_non_participant_returns_error_message(self, client, reset_activities):
        """Test that unregistering a non-participant returns appropriate error."""
        # Arrange
        activity_name = "Basketball Team"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        result = response.json()
        
        # Assert
        assert "not registered" in result["detail"].lower()


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows."""

    def test_signup_then_unregister_flow(self, client, reset_activities):
        """Test the complete signup and unregister flow."""
        # Arrange
        activity_name = "Tennis Club"
        email = "student@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup was successful
        assert signup_response.status_code == 200
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert unregister was successful
        assert unregister_response.status_code == 200
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]

    def test_multiple_signups_then_unregister_one(self, client, reset_activities):
        """Test signing up multiple participants and unregistering one."""
        # Arrange
        activity_name = "Science Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act - Sign up two students
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})
        
        # Assert both are registered
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants
        
        # Act - Unregister one
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email1})
        
        # Assert only one remains
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email1 not in participants
        assert email2 in participants
