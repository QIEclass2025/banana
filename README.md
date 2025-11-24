# 🎮 Python 포켓몬 종족값 배틀 게임

PokeAPI를 활용한 GUI 기반의 포켓몬 랜덤 배틀 게임입니다.  
`tkinter`를 사용하여 GUI를 구성하였으며, `requests`와 `threading`을 통해 비동기로 데이터를 처리합니다.

## 📋 프로젝트 개요

사용자와 컴퓨터가 각각 랜덤한 포켓몬을 뽑아, 해당 포켓몬의 **종족값(Base Stats) 총합**을 기준으로 승패를 겨루는 게임입니다. 단순한 운 게임 요소에 '전설/환상' 포켓몬의 등장 확률과 고화질 일러스트를 더해 시각적인 재미를 제공합니다.

### 주요 기능
- **랜덤 포켓몬 소환:** 1세대부터 9세대(도감번호 1~1025) 사이의 포켓몬을 랜덤으로 호출합니다.
- **실시간 데이터 연동:** [PokeAPI](https://pokeapi.co/)를 통해 실시간으로 이름, 이미지, 스탯 정보를 가져옵니다.
- **비동기 처리:** 이미지 다운로드 및 API 통신 시 UI가 멈추지 않도록 `threading`을 적용했습니다.
- **이미지 최적화:** `Pillow` 라이브러리를 사용하여 고화질 공식 일러스트를 깔끔하게 리사이징하여 출력합니다.

## 🛠️ 기술 스택 (Tech Stack)

- **Language:** Python 3.12+
- **GUI:** tkinter (Python Standard Library)
- **Dependency Management:** uv
- **Libraries:**
  - `requests`: REST API 통신
  - `Pillow`: 이미지 처리

## 🚀 설치 및 실행 방법 (Installation & Usage)

이 프로젝트는 `uv` 패키지 매니저를 사용하여 관리됩니다.

### 1. 레포지토리 클론
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd pokemon-battle-game