import uuid

import allure
import pytest
import requests

from config import BASE_URL
from data.payloads import LOGIN_USER


def pytest_html_report_title(report):
    report.title = "Автотесты: API + UI"


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    # При падении UI-теста прикладываем скриншот в Allure-отчёт
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            allure.attach(
                page.screenshot(full_page=True),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
    return report


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def api_client():
    """HTTP-сессия для запросов к API."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def auth_token(api_client, base_url):
    """Токен авторизации — запрашивается один раз на всю сессию."""
    response = api_client.post(f"{base_url}/login", json=LOGIN_USER)
    assert response.status_code == 200, "Не удалось получить токен авторизации"
    return response.json()["token"]


@pytest.fixture(scope="session")
def auth_client(auth_token, base_url):
    """Отдельная HTTP-сессия с заголовком авторизации.

    Не переиспользует api_client: иначе заголовок Authorization протечёт
    в остальные тесты, и стенд, проверяющий авторизацию, начнёт отвечать 401.
    """
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    })
    return session


@pytest.fixture
def user_payload():
    """Фабрика уникальных payload для создания пользователя."""

    def _factory(**overrides):
        payload = {
            "name": f"user_{uuid.uuid4().hex[:8]}",
            "job": "qa",
        }
        payload.update(overrides)
        return payload

    return _factory


@pytest.fixture
def created_user(api_client, base_url, user_payload):
    """Создаёт пользователя перед тестом и удаляет его после (yield-фикстура)."""
    response = api_client.post(f"{base_url}/users", json=user_payload())
    assert response.status_code == 201
    user = response.json()
    yield user
    response = api_client.delete(f"{base_url}/users/{user['id']}")
    assert response.status_code == 204, "Не удалось удалить тестового пользователя"
