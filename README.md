# 더 월드 서버 안내

플레이어용 안내 페이지: https://salkogi07.github.io/theworld-guide/

GitHub Actions가 15분마다 `check.py`로 게임 서버와 모드팩 서버를 확인해 `site/status.json`을 만들고 `site/`를 Pages에 배포합니다. 서버 주소는 저장소 Secret `SERVER_HOST`에만 있고 페이지·로그에는 나오지 않습니다.
