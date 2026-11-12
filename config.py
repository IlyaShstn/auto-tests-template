import os

from dotenv import load_dotenv

load_dotenv()

# URL тестируемого API (по умолчанию — публичное демо-API reqres.in)
BASE_URL = os.getenv("BASE_URL", "https://reqres.in/api")

# URL веб-приложения для UI-тестов Playwright
UI_BASE_URL = os.getenv("UI_BASE_URL", "https://playwright.dev")
