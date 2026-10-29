import pytest
from flask import Flask

import app as app_module


@pytest.fixture()
def application():
    return app_module.create_app({"TESTING": True})


@pytest.fixture()
def client(application):
    return application.test_client()


def test_root_immediately_displays_generated_code(client, monkeypatch):
    monkeypatch.setattr(app_module.secrets, "randbelow", lambda _: 2345)

    response = client.get("/")

    assert response.status_code == 200
    assert b'data-testid="generated-code"' in response.data
    assert b"3345" in response.data


@pytest.mark.parametrize(
    ("random_value", "expected_code"),
    [
        (0, b"1000"),
        (8999, b"9999"),
    ],
)
def test_root_includes_four_digit_boundaries(
    client, monkeypatch, random_value, expected_code
):
    monkeypatch.setattr(app_module.secrets, "randbelow", lambda _: random_value)

    response = client.get("/")

    assert response.status_code == 200
    assert expected_code in response.data


def test_refresh_generates_code_again(client, monkeypatch):
    random_values = iter((0, 1))
    monkeypatch.setattr(app_module.secrets, "randbelow", lambda _: next(random_values))

    first_response = client.get("/")
    refreshed_response = client.get("/")

    assert b"1000" in first_response.data
    assert b"1001" in refreshed_response.data


def test_root_is_not_cached(client):
    response = client.get("/")

    assert response.headers["Cache-Control"] == "no-store"


def test_page_explains_refresh_behavior(client):
    response = client.get("/")

    assert "Обновите страницу, чтобы получить новый код." in response.get_data(
        as_text=True
    )
    assert b'href="/static/style.css"' in response.data


def test_module_exposes_application_for_production_server():
    assert isinstance(app_module.app, Flask)
