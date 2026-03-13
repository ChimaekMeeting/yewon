# 🤖 AI 기반 맞춤형 경로 추천 서비스 (MVP)

사용자의 자연어 요청을 분석하여 상황에 맞는 최적의 경로(최단거리, 안전 귀가, 풍경/산책)를 추천해 주는 지능형 에이전트 기반 웹 서비스입니다.

## 📌 프로젝트 개요
단순한 '최단 시간' 위주의 기존 길 찾기 서비스에서 벗어나, 사용자의 현재 상황과 감정(예: "밤길이 무서워서 밝은 길로 가고 싶어", "예쁜 산책로를 걷고 싶어")을 LLM이 분석하여 그에 맞는 가중치를 적용한 맞춤형 경로를 제공합니다. 본 코드는 서비스의 가능성을 검증하기 위한 초기 프로토타입(MVP)입니다.

## 🛠 기술 스택 (Tech Stack)
- **Backend:** Python, FastAPI, Uvicorn, Pydantic, Jinja2
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **AI / NLP:** OpenAI API (gpt-3.5-turbo)
- **External API:** Kakao Maps API (지도 시각화), Kakao Mobility API (경로 데이터)

## ✨ 주요 기능 (Key Features)
1. **자연어 의도 분석 (Intent Analysis)**
   - OpenAI API를 활용해 사용자의 일상적인 문장을 입력받아 `shortest`(최단), `safe`(안전), `scenic`(산책/풍경) 3가지 모드로 자동 분류합니다.
2. **동적 경로 추천 (Dynamic Routing)**
   - 분석된 의도에 맞춰 카카오 모빌리티 길 찾기 API의 탐색 우선순위(Priority)를 조정하여 상황에 맞는 경로 좌표를 추출합니다.
3. **직관적인 UI (Interactive Map)**
   - 카카오 지도를 통해 출발지/도착지 마커를 생성하고, 추천된 경로를 맵 위에 시각적인 선(Polyline)으로 그려줍니다.
⚠️현재는 카카오 지도를 연결만 해둔 상태이기 때문에 같은 경로가 추천됩니다. 어떤 문장이 입력되느냐에 따라 모드가 달라지는 것이 차이점입니다. 아래는 모드 분류와 인식되는 단어 목록입니다. 
- 빨리 가고 싶거나 일반적인 목적: 'shortest' 모드
- 어둡다, 무섭다, 안전하게 등의 맥락: 'safe' 모드
- 산책, 경치, 여유롭게 걷기 등의 맥락: 'scenic' 모드

## 🚀 실행 방법 (Getting Started)

### 1. 환경 변수 설정
`backend` 폴더 최상단에 `.env` 파일을 생성하고 발급받은 API 키를 입력합니다.
```env
OPENAI_API_KEY=sk-your-openai-api-key
KAKAO_REST_API_KEY=your-kakao-rest-api-key
KAKAO_JS_KEY=your-kakao-javascript-key