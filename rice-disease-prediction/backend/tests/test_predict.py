"""
Tests for prediction endpoints.
"""

import io
from PIL import Image


def create_test_image(width=200, height=200, color="green"):
    """Create a test image in memory."""
    img = Image.new("RGB", (width, height), color)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer


class TestPredict:
    def test_predict_success(self, client, auth_headers):
        image = create_test_image()
        response = client.post(
            "/api/predict",
            headers=auth_headers,
            files={"file": ("test_leaf.jpg", image, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "disease_name" in data["data"]
        assert "confidence" in data["data"]
        assert "all_probabilities" in data["data"]
        assert "treatment" in data["data"]
        assert "prediction_id" in data["data"]

    def test_predict_unauthorized(self, client):
        image = create_test_image()
        response = client.post(
            "/api/predict",
            files={"file": ("test.jpg", image, "image/jpeg")},
        )
        assert response.status_code == 403

    def test_predict_invalid_file_type(self, client, auth_headers):
        text_file = io.BytesIO(b"not an image")
        response = client.post(
            "/api/predict",
            headers=auth_headers,
            files={"file": ("test.txt", text_file, "text/plain")},
        )
        assert response.status_code == 400

    def test_predict_image_too_small(self, client, auth_headers):
        image = create_test_image(width=50, height=50)
        response = client.post(
            "/api/predict",
            headers=auth_headers,
            files={"file": ("small.jpg", image, "image/jpeg")},
        )
        assert response.status_code == 400

    def test_predict_png(self, client, auth_headers):
        img = Image.new("RGB", (200, 200), "green")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        response = client.post(
            "/api/predict",
            headers=auth_headers,
            files={"file": ("test.png", buffer, "image/png")},
        )
        assert response.status_code == 200


class TestHistory:
    def _make_prediction(self, client, auth_headers):
        """Helper: make a prediction to populate history."""
        image = create_test_image()
        return client.post(
            "/api/predict",
            headers=auth_headers,
            files={"file": ("test.jpg", image, "image/jpeg")},
        )

    def test_get_history_empty(self, client, auth_headers):
        response = client.get("/api/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    def test_get_history_with_predictions(self, client, auth_headers):
        # Make 3 predictions
        for _ in range(3):
            self._make_prediction(client, auth_headers)

        response = client.get("/api/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["data"]) == 3

    def test_get_prediction_detail(self, client, auth_headers):
        # Make a prediction
        pred_response = self._make_prediction(client, auth_headers)
        pred_id = pred_response.json()["data"]["prediction_id"]

        # Get detail
        response = client.get(f"/api/history/{pred_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["prediction_id"] == pred_id

    def test_delete_prediction(self, client, auth_headers):
        # Make a prediction
        pred_response = self._make_prediction(client, auth_headers)
        pred_id = pred_response.json()["data"]["prediction_id"]

        # Delete
        response = client.delete(f"/api/history/{pred_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify deleted
        response = client.get(f"/api/history/{pred_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_history_isolation(self, client, auth_headers, second_user_headers):
        """User cannot see another user's predictions."""
        # User 1 makes a prediction
        pred_response = self._make_prediction(client, auth_headers)
        pred_id = pred_response.json()["data"]["prediction_id"]

        # User 2 tries to access it
        response = client.get(f"/api/history/{pred_id}", headers=second_user_headers)
        assert response.status_code == 404
