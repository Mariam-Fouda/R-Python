EXAM_PAYLOAD = {
    "title": "Submit Test Exam",
    "duration_minutes": 30,
    "questions": [
        {
            "text": "What is 2+2?",
            "question_type": "multiple_choice",
            "option_a": "3", "option_b": "4", "option_c": "5", "option_d": "6",
            "correct_answer": "B", "points": 2,
        },
        {
            "text": "The sky is blue.",
            "question_type": "true_false",
            "correct_answer": "T", "points": 1,
        },
    ],
}


def test_submit_exam(client, admin_token, student_token):
    create_res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    exam_id = create_res.json()["exam_id"]

    # Get questions
    exam_detail = client.get(f"/api/exams/{exam_id}", headers={"Authorization": f"Bearer {student_token}"}).json()
    q1_id = exam_detail["questions"][0]["id"]
    q2_id = exam_detail["questions"][1]["id"]

    res = client.post("/api/results/submit", json={
        "exam_id": exam_id,
        "answers": [
            {"question_id": q1_id, "selected_answer": "B"},
            {"question_id": q2_id, "selected_answer": "T"},
        ],
    }, headers={"Authorization": f"Bearer {student_token}"})

    assert res.status_code == 200
    data = res.json()
    assert data["passed"] is True
    assert data["percentage"] == 100.0


def test_cannot_submit_twice(client, admin_token, student_token):
    create_res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    exam_id = create_res.json()["exam_id"]
    exam_detail = client.get(f"/api/exams/{exam_id}", headers={"Authorization": f"Bearer {student_token}"}).json()
    q1_id = exam_detail["questions"][0]["id"]
    q2_id = exam_detail["questions"][1]["id"]

    answers = {
        "exam_id": exam_id,
        "answers": [
            {"question_id": q1_id, "selected_answer": "B"},
            {"question_id": q2_id, "selected_answer": "T"},
        ],
    }
    client.post("/api/results/submit", json=answers, headers={"Authorization": f"Bearer {student_token}"})
    res = client.post("/api/results/submit", json=answers, headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 400


def test_view_my_results(client, admin_token, student_token):
    create_res = client.post("/api/exams/", json=EXAM_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"})
    exam_id = create_res.json()["exam_id"]
    exam_detail = client.get(f"/api/exams/{exam_id}", headers={"Authorization": f"Bearer {student_token}"}).json()
    q1_id = exam_detail["questions"][0]["id"]

    client.post("/api/results/submit", json={
        "exam_id": exam_id, "answers": [{"question_id": q1_id, "selected_answer": "A"}]
    }, headers={"Authorization": f"Bearer {student_token}"})

    res = client.get("/api/results/my", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_admin_view_all_results(client, admin_token):
    res = client.get("/api/results/admin/all", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200


def test_student_cannot_view_admin_results(client, student_token):
    res = client.get("/api/results/admin/all", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 403
