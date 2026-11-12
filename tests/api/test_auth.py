import allure
import pytest

from data.payloads import LOGIN_USER, REGISTER_USER

pytestmark = [pytest.mark.api, allure.feature("Авторизация")]

REGISTER_INVALID_PAYLOADS = [
    pytest.param({"email": REGISTER_USER["email"]}, id="без пароля"),
    pytest.param({"password": REGISTER_USER["password"]}, id="без email"),
    pytest.param({}, id="пустое тело"),
]

LOGIN_INVALID_PAYLOADS = [
    pytest.param({"email": LOGIN_USER["email"]}, id="без пароля"),
    pytest.param({"password": LOGIN_USER["password"]}, id="без email"),
]


@allure.story("Регистрация")
class TestRegister:
    @allure.title("Успешная регистрация возвращает токен")
    @pytest.mark.smoke
    def test_register_success(self, api_client, base_url):
        response = api_client.post(f"{base_url}/register", json=REGISTER_USER)
        assert response.status_code == 200
        assert response.json().get("token")

    @allure.title("Регистрация с неполным телом запроса возвращает 400")
    @pytest.mark.parametrize("payload", REGISTER_INVALID_PAYLOADS)
    def test_register_invalid_payload(self, api_client, base_url, payload):
        response = api_client.post(f"{base_url}/register", json=payload)
        assert response.status_code == 400


@allure.story("Логин")
class TestLogin:
    @allure.title("Успешный логин возвращает токен")
    @pytest.mark.smoke
    def test_login_success(self, api_client, base_url):
        response = api_client.post(f"{base_url}/login", json=LOGIN_USER)
        assert response.status_code == 200
        assert response.json().get("token")

    @allure.title("Логин с неполным телом запроса возвращает 400")
    @pytest.mark.parametrize("payload", LOGIN_INVALID_PAYLOADS)
    def test_login_invalid_payload(self, api_client, base_url, payload):
        response = api_client.post(f"{base_url}/login", json=payload)
        assert response.status_code == 400
