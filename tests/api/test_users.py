import allure
import pytest

pytestmark = [pytest.mark.api, allure.feature("Управление пользователями")]


@allure.story("Получение пользователей")
class TestGetUsers:
    @allure.title("Список пользователей второй страницы")
    @pytest.mark.smoke
    def test_get_users_list(self, api_client, base_url):
        # Примечание: против reqres.in запрос идёт анонимно — стенд отвечает 401
        # на Authorization: Bearer (см. фикстуру auth_client для своего стенда).
        response = api_client.get(f"{base_url}/users", params={"page": 2})
        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 2
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0

    @allure.title("Получение пользователя по id: {user_id}")
    @pytest.mark.parametrize("user_id", [1, 2, 3], ids=["id=1", "id=2", "id=3"])
    def test_get_single_user(self, api_client, base_url, user_id):
        response = api_client.get(f"{base_url}/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == user_id

    @allure.title("Запрос несуществующего пользователя возвращает 404")
    def test_user_not_found_returns_404(self, api_client, base_url):
        response = api_client.get(f"{base_url}/users/23")
        assert response.status_code == 404


@allure.story("Изменение пользователей")
class TestModifyUsers:
    @allure.title("Создание пользователя с уникальными данными")
    def test_create_user(self, api_client, base_url, user_payload):
        payload = user_payload()
        response = api_client.post(f"{base_url}/users", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == payload["name"]
        assert body["job"] == payload["job"]
        assert body.get("id")

    @allure.title("Обновление пользователя")
    def test_update_user(self, api_client, base_url, user_payload):
        payload = user_payload(job="zion resident")
        response = api_client.put(f"{base_url}/users/2", json=payload)
        assert response.status_code == 200
        assert response.json()["job"] == payload["job"]

    @allure.title("Удаление пользователя, созданного фикстурой created_user")
    def test_delete_user(self, api_client, base_url, created_user):
        response = api_client.delete(f"{base_url}/users/{created_user['id']}")
        assert response.status_code == 204
