import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ==========================================
# 1. 환경 변수 및 초기 세팅
# ==========================================
load_dotenv()
client = OpenAI()
KAKAO_REST_KEY = os.environ.get("KAKAO_REST_API_KEY")
KAKAO_JS_KEY = os.environ.get("KAKAO_JS_KEY")

app = FastAPI()

# CORS 설정 (프론트-백엔드 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 템플릿 폴더 지정 (HTML 파일이 있는 곳)
templates = Jinja2Templates(directory="templates")


# ==========================================
# 2. 🌐 메인 화면(HTML) 띄워주기 API
# ==========================================
@app.get("/")
async def serve_frontend(request: Request):
    """
    브라우저에서 주소창에 http://127.0.0.1:8000 을 쳤을 때 실행됩니다.
    templates 폴더 안의 index.html을 화면에 뿌려주고, 카카오 JS 키를 전달합니다.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "kakao_js_key": KAKAO_JS_KEY}
    )


# ==========================================
# 3. 데이터 규격 및 AI 의도 분석기
# ==========================================
class RouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    user_message: str


class IntentAnalyzer:
    def analyze(self, user_input):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "너는 길 찾기 앱의 경로 추천 보조 AI야. "
                            "사용자의 문장을 읽고 의도를 파악해서 오직 'shortest', 'safe', 'scenic' 중 하나로만 대답해.\n"
                            "- 빨리 가고 싶거나 일반적인 목적: 'shortest'\n"
                            "- 어둡다, 무섭다, 안전하게 등의 맥락: 'safe'\n"
                            "- 산책, 경치, 여유롭게 걷기 등의 맥락: 'scenic'"
                        ),
                    },
                    {"role": "user", "content": user_input},
                ],
                temperature=0.0,
            )
            intent = response.choices[0].message.content.strip().lower()
            return intent if intent in ["shortest", "safe", "scenic"] else "shortest"
        except Exception as e:
            print(f"ChatGPT 에러: {e}")
            return "shortest"


analyzer = IntentAnalyzer()


# ==========================================
# 4. 카카오 모빌리티 API 연동 (실제 도로 정보)
# ==========================================
def get_kakao_route(start_lng, start_lat, end_lng, end_lat, intent):
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}

    # AI 의도에 따른 경로 탐색 옵션 변경
    priority = "RECOMMEND"
    if intent == "shortest":
        priority = "TIME"

    params = {
        "origin": f"{start_lng},{start_lat}",
        "destination": f"{end_lng},{end_lat}",
        "priority": priority,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("카카오 API 호출 실패:", response.text)
        return []

    data = response.json()
    path_coordinates = []
    try:
        roads = data["routes"][0]["sections"][0]["roads"]
        for road in roads:
            vertexes = road["vertexes"]
            for i in range(0, len(vertexes), 2):
                path_coordinates.append({"lng": vertexes[i], "lat": vertexes[i + 1]})
    except (KeyError, IndexError):
        print("경로 데이터를 파싱할 수 없습니다.")

    return path_coordinates


# ==========================================
# 5. 🚀 경로 계산 API (프론트엔드와 통신)
# ==========================================
@app.post("/api/get_route")
async def process_route(req: RouteRequest):
    print(f"\n[요청 수신] 사용자 메시지: {req.user_message}")

    intent = analyzer.analyze(req.user_message)
    print(f"[의도 분석 완료] 적용 모드: {intent}")

    path_coords = get_kakao_route(
        start_lng=req.start_lng,
        start_lat=req.start_lat,
        end_lng=req.end_lng,
        end_lat=req.end_lat,
        intent=intent,
    )

    return {"status": "success", "intent": intent, "path": path_coords}
