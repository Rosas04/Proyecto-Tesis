import pytest

@pytest.fixture
def mock_playwright_page(mocker):
    """Fixture para mockear la clase Page de Playwright."""
    page_mock = mocker.Mock()
    page_mock.goto = mocker.AsyncMock()
    page_mock.fill = mocker.AsyncMock()
    page_mock.click = mocker.AsyncMock()
    page_mock.wait_for_selector = mocker.AsyncMock()
    page_mock.evaluate = mocker.AsyncMock()
    page_mock.inner_html = mocker.AsyncMock()
    page_mock.screenshot = mocker.AsyncMock()
    return page_mock
