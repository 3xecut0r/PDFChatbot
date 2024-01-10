from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
import io


client = TestClient(app)


def test_pay():
    test_user = {"_id": "user123", "username": "testuser"}

    with patch("myapp.your_module.get_current_user") as mock_user, patch(
        "myapp.your_module.get_payment"
    ) as mock_payment:
        mock_user.return_value = test_user
        mock_payment.return_value = {"status": "Payment initiated"}

        response = client.post("/users/pay")
        assert response.status_code == 200
        assert response.json() == {"status": "Payment initiated"}


def test_execute_payment_success():
    test_user = {"_id": "user123", "username": "testuser"}
    payment_id = "pay_123"
    payer_id = "payer_123"

    with patch("myapp.your_module.get_current_user") as mock_user, patch(
        "myapp.your_module.execute_paypal_payment"
    ) as mock_execute:
        mock_user.return_value = test_user
        mock_execute.return_value = True

        response = client.get(
            f"/payment/execute?paymentId={payment_id}&PayerID={payer_id}"
        )
        assert response.status_code == 200
        assert response.json() == {
            "status": "Payment successful, user upgraded to premium"
        }
