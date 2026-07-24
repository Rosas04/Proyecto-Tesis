import pytest
from unittest.mock import MagicMock
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from services.auth_service import (
    perform_form_login,
    validate_form_auth,
    AuthenticationError,
    normalize_auth_config
)

def test_execute_login():
    # Setup mock page
    mock_page = MagicMock()
    
    # Mock locator chain: page.locator().first -> locator
    mock_locator = MagicMock()
    mock_locator.is_visible.return_value = True
    
    # Mock get_by_placeholder, get_by_label, get_by_role, etc.
    # We want these to return mock_locator when .first is called
    mock_chain = MagicMock()
    mock_chain.first = mock_locator
    mock_chain.or_.return_value = mock_chain
    
    mock_page.locator.return_value = mock_chain
    mock_page.get_by_placeholder.return_value = mock_chain
    mock_page.get_by_label.return_value = mock_chain
    mock_page.get_by_role.return_value = mock_chain
    
    auth_config = {
        "mode": "form",
        "username": "testuser@example.com",
        "password": "password123",
        "login_url": "https://example.com/login"
    }
    
    # Execute login
    perform_form_login(mock_page, auth_config, "https://example.com")
    
    # Verify navigation
    mock_page.goto.assert_called_with("https://example.com/login", wait_until="domcontentloaded", timeout=60000)
    
    # Verify credentials filled
    mock_locator.fill.assert_any_call("testuser@example.com", force=True)
    
    # The password field might be filled with timeout=5000 according to code
    # We just ensure fill was called twice
    assert mock_locator.fill.call_count >= 2
