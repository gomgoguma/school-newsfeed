# 뉴스피드 모아보기 API

## 1. 구현 기능

#### 사용자
- 회원가입
- 로그인

#### 학교 관리자
- 학교 페이지 생성
- 학교 페이지 소식 작성
- 소식 삭제
- 소식 수정

#### 학생
- 학교 페이지 구독
- 구독 중인 학교 페이지 목록 확인
- 학교 페이지 구독 취소
- 구독 중인 학교 페이지 별 소식
- 뉴스피드 모아보기

<br><br>
## 2.  Status Code
- 200: 성공 (select, update, delete, etc)
- 201: 성공 (insert)
- 400: 잘못된 요청(데이터 에러)
- 401: 로그인 실패 또는, 인증하지 않고 인증이 필요한 API 요청하는 경우
- 403: 권한 오류
- 404: 요청한 리소스 없음
- 409: 중복 오류
- 422: 입력값 검증 오류
- 500: 그밖의 서버의 오류

<br><br>
## 3. 구동 방법
1. [파이썬 3.12](https://www.python.org/downloads/release/python-3120/) 설치
2. [postgresql](https://www.postgresql.org/download/) 설치
3. [PyCharm](https://www.jetbrains.com/ko-kr/pycharm/) 설치 및 실행
4. git clone
```
git clone https://github.com/gomgoguma/school-newsfeed.git
```
5. 가상 환경 생성 (PyCharm)
 - PyCharm 초기 화면에서 가상환경 생성 창이 뜨는 경우 > OK 
 - 그렇지 않은 경우 ↓
```
- 프로젝트 설정 : ctrl + alt + s
- Project: school-newsfeed
- Python Interpreter
- Add Interpreter > Add Local Interpreter
- Virtualevn Environment
- Environment > New
- Location > 기본값
- Base Interpreter > 설치한 python 경로 찾아서 선택
```
6. 가상 환경에 의존성 설치 
```
(venv) 프로젝트 경로 > pip install -r requirements.txt
```
7. db 연동
```
newsfeed_app/common/env.py 파일 > DB 연결 정보 수정

DB_URL = "postgresql://{username}:{password}@{host}:{port}/{database}"
```

<br><br>

## 4. 확인 절차

### 테스트 코드
1. Uvicorn 실행 (DB 테이블 자동 생성)
```
(venv) 프로젝트 경로 > uvicorn newsfeed_app.main:app --host 127.0.0.1 --port 5000
```
2. 테스트 목록 확인 > pytest.ini
3. 테스트 코드 실행
```
(venv) 프로젝트 경로 > pytest -m [테스트명]

(venv) 프로젝트 경로 > pytest -m sign_up_student
```
4. 테스트 결과 확인
```
============== 1 passed, 12 deselected, 2 warnings in 7.03s ================= 
```

<br><br>
### Swagger API
1. Uvicorn 실행 (테스트 코드 1번에서 진행한 경우 생략)
```
(venv) 프로젝트 경로 > uvicorn newsfeed_app.main:app --host 127.0.0.1 --port 5000
```
2. swagger 접속
```
http://localhost:5000/docs
```
3. 회원가입 API 요청 
4. 로그인 API 요청 후 응답 값의 access_token을 복사하여 우측 상단 Authorize 버튼 눌러 토큰 붙여넣기
4. API 별 테스트 (Swagger Schema 참고)
