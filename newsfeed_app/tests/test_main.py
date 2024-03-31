import asyncio

import pytest
from starlette.testclient import TestClient

from newsfeed_app.common.database import SessionLocal
from newsfeed_app.main import app
from newsfeed_app.user.user_service import delete_user_by_username

client = TestClient(app)

username = "testuser"
username2 = "testuser2"
username3 = "testuser3"
password = "test1234!@"
name = "테스트사용자"


@pytest.fixture
def db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def delete_user(db):
    def delete(user):
        delete_user_by_username(db, user)

    yield delete
    delete_user_by_username(username, db)
    delete_user_by_username(username2, db)
    delete_user_by_username(username3, db)


# 회원가입 테스트
def sign_up(role: str):
    # 1. 입력값 누락(role)
    response = client.post("/api/v1/auth/sign-up", json={
        "username": username,
        "password": password,
        "name": name
    })
    assert response.status_code == 422

    # 2. 잘못된 아이디 형식(username 특수문자 포함)
    response = client.post("/api/v1/auth/sign-up", json={
        "username": f"{username}%!@#",
        "password": password,
        "role": role,
        "name": name
    })
    assert response.status_code == 422

    # 3. 패스워드 길이 초과 (30자 초과)
    response = client.post("/api/v1/auth/sign-up", json={
        "username": username,
        "password": "1234^a235325sadkjfaasd#$adw324sdfsd3243%",
        "role": role,
        "name": name
    })
    assert response.status_code == 422

    # 4. 회원가입 성공
    response = client.post("/api/v1/auth/sign-up", json={
        "username": username,
        "password": password,
        "role": role,
        "name": name
    })
    assert response.status_code == 201

    # 5. 아이디 중복
    response = client.post("/api/v1/auth/sign-up", json={
        "username": username,
        "password": password,
        "role": role,
        "name": name
    })
    assert response.status_code == 409


@pytest.mark.sign_up_student
def test_sign_up_student(delete_user):
    sign_up("student")


@pytest.mark.sign_up_admin
def test_sign_up_admin(delete_user):
    sign_up("admin")


# 로그인
def sign_in(role: str):
    # 1. 회원가입 성공
    response = client.post("/api/v1/auth/sign-up", json={
        "username": username,
        "password": password,
        "role": role,
        "name": name
    })
    assert response.status_code == 201

    # 2. 입력값 누락 (패스워드)
    response = client.post("/api/v1/auth/sign-in", json={
        "username": username
    })
    assert response.status_code == 422

    # 3. 사용자 정보 없는 경우 로그인 실패
    response = client.post("/api/v1/auth/sign-in", json={
        "username": f"{username}10000",
        "password": password,
    })
    assert response.status_code == 401

    # 4. 로그인 성공
    response = client.post("/api/v1/auth/sign-in", json={
        "username": username,
        "password": password,
    })
    assert response.status_code == 200


@pytest.mark.sign_in_student
def test_sign_in_student(delete_user):
    sign_in("student")


@pytest.mark.sign_in_admin
def test_sign_in_admin(delete_user):
    sign_in("admin")


def get_access_token(user: str, role: str):
    # 회원가입
    response = client.post("/api/v1/auth/sign-up", json={
        "username": user,
        "password": password,
        "role": role,
        "name": name
    })
    assert response.status_code == 201

    # 로그인
    response = client.post("/api/v1/auth/sign-in", json={
        "username": user,
        "password": password,
    })
    assert response.status_code == 200

    # 토큰 반환
    response_data = response.json()
    data = response_data['data']
    return data['access_token']


# 학교 페이지 등록
@pytest.mark.school_page_insert
def test_school_page_insert(delete_user):
    # 1. 인증 없이 요청 > 401
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    })
    assert response.status_code == 401

    # 2. 학생 권한으로 요청 > 403
    access_token = get_access_token(username, "student")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 403

    # 3. 성공
    access_token = get_access_token(username2, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201


# 학교 소식 등록
@pytest.mark.school_news_insert
def test_school_news_insert(delete_user):
    # 학교 페이지 등록
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']

    # 학교 소식 등록
    # 1. 인증 없이 요청 > 401
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    })
    assert response.status_code == 401

    # 2. 학생 권한으로 요청 > 403
    student_token = get_access_token(username2, "student")
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403

    # 3. 다른 학교 관리자 요청 > 403
    another_admin_token = get_access_token(username3, "admin")
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {another_admin_token}"})
    assert response.status_code == 403

    # 4. 입력값 오류(제목에 특수문자 포함) > 422
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식@@@@",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 422

    # 5. 성공 > 201
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201


# 학교 소식 수정
@pytest.mark.school_news_update
def test_school_news_update(delete_user):
    # 학교 페이지 등록
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']

    # 학교 소식 등록
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    news_id = response.json()['data']['news_id']

    # 학교 소식 수정
    # 1. 인증 없이 요청 > 401
    response = client.put("/api/v1/admin/school-page/news", json={
        "news_id": news_id,
        "title": "서초고등학교 소식",
        "content": "서초고등학교 소식입니다.",
    })
    assert response.status_code == 401

    # 2. 학생 권한으로 요청 > 403
    student_token = get_access_token(username2, "student")
    response = client.put("/api/v1/admin/school-page/news", json={
        "news_id": news_id,
        "title": "서초고등학교 소식",
        "content": "서초고등학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403

    # 3. 다른 학교 관리자 요청 > 403
    another_admin_token = get_access_token(username3, "admin")
    response = client.put("/api/v1/admin/school-page/news", json={
        "news_id": news_id,
        "title": "서초고등학교 소식",
        "content": "서초고등학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {another_admin_token}"})
    assert response.status_code == 403

    # 4. 입력값 오류(제목에 특수문자 포함) > 422
    response = client.put("/api/v1/admin/school-page/news", json={
        "news_id": news_id,
        "title": "서초고등학교 소식@@@",
        "content": "서초고등학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 422

    # 5. 성공 > 200
    response = client.put("/api/v1/admin/school-page/news", json={
        "news_id": news_id,
        "title": "서초고등학교 소식",
        "content": "서초고등학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


# 학교 소식 삭제
@pytest.mark.school_news_delete
def test_school_news_delete(delete_user):
    # 학교 페이지 등록
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']

    # 학교 소식 등록
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    news_id = response.json()['data']['news_id']

    # 학교 소식 삭제
    # 1.인증 없이 요청 > 401
    response = client.delete(f"/api/v1/admin/school-page/news/{news_id}")
    assert response.status_code == 401

    # 2. 학생 권한으로 요청 > 403
    student_token = get_access_token(username2, "student")
    response = client.delete(f"/api/v1/admin/school-page/news/{news_id}",
                             headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403

    # 3. 다른 관리자가 요청 > 403
    another_admin_token = get_access_token(username3, "admin")
    response = client.delete(f"/api/v1/admin/school-page/news/{news_id}",
                             headers={"Authorization": f"Bearer {another_admin_token}"})
    assert response.status_code == 403

    # 4. 성공 > 200
    response = client.delete(f"/api/v1/admin/school-page/news/{news_id}",
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


# 학교 페이지 구독
@pytest.mark.school_page_sub_insert
def test_school_page_sub_insert(delete_user):
    # 학교 페이지 등록 (관리자)
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']

    # 학교 페이지 구독 (학생)
    student_token = get_access_token(username2, "student")

    # 1.인증 없이 요청 > 401
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    })
    assert response.status_code == 401

    # 2. 관리자 권한으로 요청 > 403
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 403

    # 3.존재하지 않는 페이지 ID > 404
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": 0
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404

    # 4. 성공 > 201
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201

    # 5. 중복 오류(구독 상태) > 409
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 409


# 학교 페이지 구독 취소
@pytest.mark.school_page_sub_delete
def test_school_page_sub_delete(delete_user):
    # 학교 페이지 등록 (관리자)
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']

    student_token = get_access_token(username2, "student")

    # 학교 페이지 구독 (학생)
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201

    # 학교 페이지 구독 취소 (학생)
    # 1.구독 상태 오류 > 404
    response = client.delete(f"/api/v1/student/school-page/0/subscription",
                             headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404

    # 3.관리자 권한으로 요청 > 403
    response = client.delete(f"/api/v1/student/school-page/{page_id}/subscription",
                             headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 403

    # 3.성공 > 200
    response = client.delete(f"/api/v1/student/school-page/{page_id}/subscription",
                             headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


# 학교 페이지 구독 목록 조회
@pytest.mark.school_page_sub_search
def test_school_page_sub_search(delete_user):
    # 학교 페이지 등록 (관리자)
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']

    student_token = get_access_token(username2, "student")

    # 학교 페이지 구독 조회 > 없음
    response = client.get("/api/v1/student/school-page/subscriptions",
                          headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404

    # 학교 페이지 구독 (학생)
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201

    # 학교 페이지 구독 조회 > 성공
    response = client.get("/api/v1/student/school-page/subscriptions",
                          headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


# 학교 페이지 별 소식 조회
@pytest.mark.school_page_news_search
def test_school_page_news_search(delete_user):

    # 학교 페이지 등록 (관리자)
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']
    student_token = get_access_token(username2, "student")

    # 학교 페이지 구독 (학생)
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201

    # 페이지 별 소식 조회 (학생)
    # 1.학교 소식 없음 > 404
    response = client.get(f"/api/v1/student/school-page/{page_id}/news",
                          headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404

    # 학교 페이지 소식 등록 (관리자)
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    # 페이지 별 소식 조회 (학생)
    # 2.권한 오류(구독하지 않은 경우) > 403
    another_student_token = get_access_token(username3, "student")
    response = client.get(f"/api/v1/student/school-page/{page_id}/news",
                          headers={"Authorization": f"Bearer {another_student_token}"})
    assert response.status_code == 403

    # 3.권한 오류(관리자가 요청) > 403
    response = client.get(f"/api/v1/student/school-page/{page_id}/news",
                          headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 403

    # 4.성공 > 200
    response = client.get(f"/api/v1/student/school-page/{page_id}/news",
                          headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200


# 학교 페이지 뉴스피드 모아보기
@pytest.mark.school_page_newsfeed_search
def test_school_page_newsfeed_search(delete_user):

    # 학교 페이지 등록 (관리자)
    admin_token = get_access_token(username, "admin")
    response = client.post("/api/v1/admin/school-page", json={
        "location": "서초동",
        "school_name": "서초중학교",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    page_id = response.json()['data']['page_id']
    student_token = get_access_token(username2, "student")

    # 학교 페이지 소식 등록 (관리자)
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식",
        "content": "서초중학교 소식입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201

    # 백그라운드 작업 대기(사용자 뉴스피드 추가)
    loop = asyncio.get_event_loop()
    loop.run_until_complete((lambda: asyncio.sleep(3))())

    # 학교 페이지 구독 (학생)
    response = client.post("/api/v1/student/school-page/subscription", json={
        "page_id": page_id
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201

    # 뉴스피드 모아보기 (학생) > 구독 전 등록된 소식 > 404
    response = client.get("/api/v1/student/school-page/newsfeed",
                          headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 404

    # 학교 페이지 소식 등록 (관리자)
    response = client.post("/api/v1/admin/school-page/news", json={
        "page_id": page_id,
        "title": "서초중학교 소식2",
        "content": "서초중학교 소식2입니다.",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    loop.run_until_complete((lambda: asyncio.sleep(3))())

    # 뉴스피드 모아보기 (학생) > 구독 후 등록된 소식 > 200
    response = client.get("/api/v1/student/school-page/newsfeed",
                          headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200

    # 학교 페이지 구독 취소 (학생)
    response = client.delete(f"/api/v1/student/school-page/{page_id}/subscription",
                             headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200

    # 뉴스피드 모아보기 (학생) > 구독 취소 후에도 기존 피드 유지
    response = client.get("/api/v1/student/school-page/newsfeed",
                          headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 200
