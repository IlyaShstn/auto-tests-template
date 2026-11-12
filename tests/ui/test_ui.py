import re

import allure
import pytest
from playwright.sync_api import Page, expect

from config import UI_BASE_URL

pytestmark = [pytest.mark.ui, allure.feature("Главная страница")]

# Языковая вкладка на главной → путь к документации этого языка
LANGUAGES = [
    ("TypeScript", "/docs/intro"),
    ("Python", "/python/docs/intro"),
    (".NET", "/dotnet/docs/intro"),
    ("Java", "/java/docs/intro"),
]


@allure.story("Навигация")
@allure.title("Главная страница → документация на языке {language}")
@pytest.mark.smoke
@pytest.mark.parametrize("language,docs_path", LANGUAGES)
def test_homepage_open_language_docs(page: Page, language: str, docs_path: str):
    """Открыть главную страницу, проверить заголовок и перейти к документации выбранного языка."""
    with allure.step(f"Открыть главную страницу: {UI_BASE_URL}"):
        page.goto(UI_BASE_URL)

    with allure.step("Проверить заголовок страницы"):
        expect(page).to_have_title(re.compile("Playwright"))

    with allure.step(f"Перейти к документации на языке {language}"):
        page.locator(".hero").get_by_role("link", name=language, exact=True).click()

    with allure.step(f"Проверить URL страницы документации: {docs_path}"):
        expect(page).to_have_url(re.compile(re.escape(docs_path) + r"$"))
