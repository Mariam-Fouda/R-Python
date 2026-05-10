def test_register_student(client):
    res = client.post("/api/auth/register", json={
        "username": "student1",
        "email": "s1@test.com",
        "password": "pass1234",
        "role": "student",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "student1"
    assert data["role"] == "student"


def test_register_admin(client):
    res = client.post("/api/auth/register", json={
        "username": "admin1",
        "email": "a1@test.com",
        "password": "pass1234",
        "role": "admin",
    })
    assert res.status_code == 201
    assert res.json()["role"] == "admin"


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={
        "username": "dupuser", "email": "dup@test.com", "password": "pass", "role": "student"
    })
    res = client.post("/api/auth/register", json={
        "username": "dupuser", "email": "dup2@test.com", "password": "pass", "role": "student"
    })
    assert res.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "loginuser", "email": "login@test.com", "password": "pass1234", "role": "student"
    })
    res = client.post("/api/auth/login", json={"username": "loginuser", "password": "pass1234"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "wrongpass", "email": "wp@test.com", "password": "correct", "role": "student"
    })
    res = client.post("/api/auth/login", json={"username": "wrongpass", "password": "wrong"})
    assert res.status_code == 401


def test_get_me(client, student_token):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    assert res.json()["role"] == "student"


def test_protected_route_no_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
