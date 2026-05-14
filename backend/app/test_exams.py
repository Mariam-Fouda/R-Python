EXAM_PAYLOAD = {
    "title": "Test Exam",
    "description": "A test exam",
    "duration_minutes": 30,
    "questions": [
        {
            "text": "What is 2+2?",
            "question_type": "multiple_choice",
            "option_a": "3",
            "option_b": "4",
            "option_c": "5",
            "option_d": "6",
            "correct_answer": "B",
            "points": 1,
        },
        {
            "text": "The sky is blue.",
            "question_type": "true_false",
            "correct_answer": "T",
            "points": 1,
        },
    ],
}


def test_admin_create_exam(client, admin_token):
    res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201
    assert "exam_id" in res.json()


def test_student_cannot_create_exam(client, student_token):
    res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 403


def test_list_exams(client, admin_token, student_token):
    client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    res = client.get("/api/exams/", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_exam_by_id(client, admin_token, student_token):
    create_res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    exam_id = create_res.json()["exam_id"]
    res = client.get(f"/api/exams/{exam_id}", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    assert res.json()["title"] == "Test Exam"


def test_update_exam(client, admin_token):
    create_res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    exam_id = create_res.json()["exam_id"]
    res = client.put(f"/api/exams/{exam_id}", json={"title": "Updated Exam"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200


def test_delete_exam(client, admin_token):
    create_res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    exam_id = create_res.json()["exam_id"]
    res = client.delete(f"/api/exams/{exam_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
