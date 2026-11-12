# Шаблон автотестов: API (Pytest) + UI (Playwright)

Готовый шаблон проекта автотестов для публикации на GitHub. Из коробки запускается
без своего бэкенда: API-тесты работают против публичного демо-API [reqres.in](https://reqres.in),
UI-сценарий — против [playwright.dev](https://playwright.dev).

## Структура проекта

```
├── .github/workflows/tests.yml   # CI: прогон API- и UI-тестов на GitHub Actions
├── config.py                     # Чтение настроек из .env
├── conftest.py                   # Фикстуры: api_client, auth_token, user_payload, created_user
├── pytest.ini                    # Маркеры (api, ui, smoke) и опции отчётов
├── requirements.txt              # Зависимости
├── .env.example                  # Пример файла настроек
├── data/
│   └── payloads.py               # Тестовые данные (payload)
├── scripts/
│   └── mock_server.py            # Локальный mock-стенд API — без лимитов reqres.in
├── tests/
│   ├── api/
│   │   ├── test_auth.py          # Авторизация: успех / негативные кейсы
│   │   └── test_users.py         # CRUD: список, получение, создание, обновление, удаление
│   └── ui/
│       └── test_ui.py            # Один Playwright-сценарий
└── reports/                      # Создаётся при прогоне (в .gitignore)
```

## Установка

Требуется Python 3.10+.

```bash
# 1. Клонировать репозиторий
git clone <url-репозитория>
cd auto-tests

# 2. Создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Установить браузеры для Playwright
playwright install chromium
```

## Запуск тестов

```bash
# Все тесты (API + UI)
pytest

# Только API-тесты
pytest tests/api
# или по маркеру
pytest -m api

# Только UI-тесты
pytest tests/ui
pytest -m ui

# UI-тесты в видимом браузере (headed-режим)
pytest tests/ui --headed

# Один конкретный тест
pytest tests/api/test_users.py::TestUsersCRUD::test_create_user

# Дымовые тесты — быстрый набор для проверки после деплоя
pytest -m smoke

# UI-тесты сразу на нескольких браузерах (параметризация от pytest-playwright)
pytest tests/ui --browser chromium --browser firefox
```

После прогона создаются отчёты:

- `reports/report.html` — простой HTML-отчёт (pytest-html), открывается сразу в браузере;
- `reports/allure-results/` — сырые результаты для Allure (см. раздел ниже).

## Фикстуры, параметризация, маркеры

**Фикстуры (`conftest.py`):**

- `api_client` (scope="session") — HTTP-сессия `requests`;
- `auth_token` (scope="session") — токен из `/login`, запрашивается один раз за прогон;
- `auth_client` (scope="session") — отдельная сессия с заголовком `Authorization`
  (для собственного стенда с авторизацией; против reqres.in не используется —
  он отвечает 401 на `Bearer` без валидного ключа, поэтому тесты идут анонимно);
- `user_payload` — фабрика уникальных данных (uuid при каждом вызове);
- `created_user` — создаёт пользователя перед тестом и удаляет его после
  (`yield`-фикстура с тирдауном).

**Параметризация (`@pytest.mark.parametrize`):**

- API: негативные сценарии регистрации/логина с разными неполными телами запроса,
  получение пользователей по разным id;
- UI: один сценарий прогоняется для всех четырёх языков документации.

**Маркеры (регистрируются в `pytest.ini`):**

- `api`, `ui` — разделение тестов по типу;
- `smoke` — короткий дымовой набор: `pytest -m smoke`.

## Allure-отчёт

Тесты размечены декораторами `@allure.feature` / `@allure.story` / `@allure.title`,
UI-сценарий разбит на шаги `allure.step`, при падении UI-теста в отчёт
автоматически прикладывается скриншот.

Для генерации отчёта нужен Allure CLI (требуется Java 8+):

```bash
# macOS
brew install allure
# Windows
scoop install allure
# Linux — дистрибутив с https://github.com/allure-framework/allure2/releases
```

```bash
pytest                                              # прогнать тесты
allure serve reports/allure-results                 # сгенерировать и открыть в браузере
# или сгенерировать статический отчёт без запуска сервера:
allure generate reports/allure-results -o reports/allure-report --clean
```

## Подключение своего стенда

По умолчанию тесты идут на публичные демо-сервисы. У reqres.in есть лимит
≈40 запросов в день с одного IP — для разовой проверки шаблона этого хватает,
но для регулярных прогонов лучше подключить свой стенд (или локальный
mock-стенд, см. раздел ниже): он снимает лимит и зависимость от чужого аптайма.

Чтобы направить тесты на свой бэкенд и своё приложение:

```bash
cp .env.example .env
```

и задайте в `.env` свои значения:

```
BASE_URL=https://your-api.example.com/api
UI_BASE_URL=https://your-app.example.com
```

После этого адаптируйте тестовые данные в `data/payloads.py` и эндпоинты
в `tests/api/` под свой API.

## Локальный mock-стенд

Для регулярных локальных прогонов в шаблоне есть готовый mock-сервер,
повторяющий контракт reqres.in (register/login, CRUD пользователей). Он работает
только на стандартной библиотеке Python — ничего устанавливать не нужно:

```bash
# терминал 1 — поднять стенд (порт 8765 по умолчанию, можно задать --port)
python scripts/mock_server.py

# терминал 2 — прогнать тесты на нём
BASE_URL=http://127.0.0.1:8765/api pytest
```

Под Windows (PowerShell): `$env:BASE_URL="http://127.0.0.1:8765/api"; pytest`.
Постоянно переключиться на мок можно, раскомментировав строку в `.env`.

## CI на GitHub Actions

Workflow `.github/workflows/tests.yml` запускает API- и UI-тесты на каждый
`push` и `pull request`. Артефакты прогона: `report.html` (pytest-html) и
`allure-report/` (статический сайт Allure) — хранятся 7 дней.

## Технологии

- `pytest` — фреймворк тестирования
- `requests` — HTTP-клиент для API-тестов
- `pytest-playwright` — UI-тесты на Playwright
- `pytest-html` — HTML-отчёт
- `allure-pytest` — интеграция с Allure
- `python-dotenv` — настройки через `.env`
