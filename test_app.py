
import json
import pytest
from app import app, init_db


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["DATABASE"] = str(tmp_path / "test.db")
    init_db()

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Cappuccino" in response.data


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_order_and_bill(client):
    response = client.post("/order", data={
        "customer": "Rahul",
        "Cappuccino": "2",
        "Mocha": "1",
    })

    assert response.status_code == 200
    assert b"260.00" in response.data
    assert b"Total: " in response.data

    history = client.get("/orders")
    assert history.status_code == 200
    assert b"Rahul" in history.data


def test_discount(client):
    response = client.post("/order", data={
        "customer": "Sneha",
        "Cappuccino": "7",
    })

    assert response.status_code == 200
    assert b"560.00" in response.data
    assert b"56.00" in response.data
    assert b"504.00" in response.data


def test_empty_order_rejected(client):
    response = client.post("/order", data={
        "customer": "Amit",
        "Cappuccino": "0",
    })

    assert response.status_code == 400
