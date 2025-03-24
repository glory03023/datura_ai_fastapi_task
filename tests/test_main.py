import pytest
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app is in a file named `main.py`
from unittest.mock import patch

# Create a TestClient for the FastAPI app
client = TestClient(app)

@pytest.fixture
def user_data():
    """Fixture to mock a user registration"""
    return {
        "username": "aaa",
        "full_name": "aaa",
        "email": "aaa@gmail.com",
        "password": "aaa"
    }

@pytest.mark.asyncio
@patch("authenticator.authenticate_user")
async def test_register(mock_authenticate, user_data):
    """Test user registration"""
    # Mock the authentication method to bypass real authentication
    mock_authenticate.return_value = {"username": user_data['username']}

    response = await client.post("/api/v1/register", json=user_data)
    assert response.status_code == 200
    assert "result" in response.json()

@pytest.mark.asyncio
@patch("authenticator.authenticate_user")
async def test_login(mock_authenticate, user_data):
    """Test login functionality"""
    # Mock the authentication response
    mock_authenticate.return_value = {"username": user_data['username']}

    response = await client.post("/api/v1/login", data={
        "username": user_data['username'],
        "password": user_data['password']
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
@patch("authenticator.get_current_user")
@patch("trading.trading_process")
@patch("bittensor_interface.get_tao_dividend_from_netuid_address")
async def test_get_tao_dividends(mock_get_tao, mock_trading_process, mock_get_current_user):
    """Test the endpoint for fetching TAO dividends"""
    
    # Mocking the current user to simulate authentication
    mock_get_current_user.return_value = {"username": "testuser"}
    
    # Mock the return value of the trading process and TAO dividend fetching
    mock_trading_process.return_value = True
    mock_get_tao.return_value = 100.0  # Mock dividend value

    # Test when netuid and hotkey are provided, and trading is enabled
    response = await client.get("/api/v1/tao_dividends?netuid=1&hotkey=testhotkey&trade=true")
    assert response.status_code == 200
    data = response.json()
    assert data["netuid"] == 1
    assert data["hotkey"] == "testhotkey"
    assert data["dividend"] == 100.0
    assert data["stake_tx_triggered"] is True

    # Test when netuid is provided, but hotkey is not
    response = await client.get("/api/v1/tao_dividends?netuid=1")
    assert response.status_code == 200
    data = response.json()
    assert data["netuid"] == 1
    assert data["dividend"] == [100.0]  # Mocked value for the subnet

    # Test when no parameters are provided
    response = await client.get("/api/v1/tao_dividends")
    assert response.status_code == 200
    assert response.json()["message"] == "No netuid or hotkey provided"

    # Test when only hotkey is provided
    response = await client.get("/api/v1/tao_dividends?hotkey=testhotkey")
    assert response.status_code == 200
    data = response.json()
    assert data["hotkey"] == "testhotkey"
    assert data["dividend"] == 100.0  # Mocked value for the hotkey
