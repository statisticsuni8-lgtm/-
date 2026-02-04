import os
import time
import random
import requests
import threading
from datetime import datetime, timedelta, timezone
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# ==========================================
# [설정] 환경 변수 & 모델
# ==========================================
# Railway에서 NOUS_API_KEY 환경변수 설정 필수
API_KEY = os.getenv("NOUS_API_KEY") 
API_URL = "https://inference-api.nousresearch.com/v1/chat/completions"
# Railway가 할당해주는 포트 (기본 8080)
PORT = int(os.environ.get("PORT", 8080)) 

MODELS = {
    "PRIMARY": "Hermes-3-Llama-3.1-405B", 
    "SECONDARY": "Hermes-3-Llama-3.1-70B"
}

app = Flask(__name__)
# 상태 저장을 위한 전역 변수
last_run_status = {"time": "Never", "mode": "None", "status": "Initializing"}

# ==========================================
# [데이터 엔진] 주제: AI 기술 및 에이전트 개발
# ==========================================
def gen_tech_trend_data():
    """Mode A: 최신 AI 기술 동향 데이터"""
    techs = ["Multi-modal RAG", "Autonomous Agents", "Small Language Models", "AI Governance"]
    focus = random.choice(techs)
    return f"TOPIC: {focus}\nTREND_SCORE: {random.randint(70, 100)}\nRESEARCH_LAB: {random.choice(['DeepMind','OpenAI','Meta','Anthropic'])}", "TECH_ANALYSIS"

def gen_coding_challenge():
    """Mode B: 에이전트 로직 구현 시나리오"""
    tasks = ["Tool Calling Logic", "Memory Management", "Self-Reflection Loop"]
    return f"AGENT_TASK: {random.choice(tasks)}\nLANGUAGE: Python\nERROR_LOG: Memory leak in long-term context buffer.", "AGENT_DEV"

def gen_short_qa():
    """Mode C: 짧은 기술 질문 리스트"""
    questions = ["What is the difference between LoRA and QLoRA?", "Explain Chain-of-Thought prompting.", "Best practices for API security?"]
    return random.choice(questions), "QUICK_QA"

# ==========================================
# [요청 처리기]
# ==========================================
def execute_api(payload, model_name):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            usage = resp.json().get('usage', {})
            print(f"      ✅ Success ({model_name}): In={usage.get('prompt_tokens')} Out={usage.get('completion_tokens')}")
            return resp.json()['choices'][0]['message']['content']
        else:
            print(f"      ⚠️ Error {resp.status_code}")
            return None
    except Exception as e:
        print(f"      ⚠️ Exception: {e}")
        return None

def process_request(model, prompt, max_t, temp):
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_t, "temperature": temp}
    return execute_api(payload, model)

def process_request_history(model, messages, max_t):
    payload = {"model": model, "messages": messages, "max_tokens": max_t, "temperature": 0.8}
    return execute_api(payload, model)

# ==========================================
# [행동 패턴]
# ==========================================
def run_deep_analysis():
    print(" >>> [Mode: Deep Analysis] Deep dive into AI Trends...")
    data, theme = gen_tech_trend_data()
    prompt = f"Data:\n{data}\n\n[TASK]: Write a professional 1000-word research summary about this trend's impact on 2026."
    process_request(MODELS["PRIMARY"], prompt, 1200, 0.7)
    return "Deep Analysis"

def run_dev_sprint():
    print(" >>> [Mode: Dev Sprint] Solving Agent logic...")
    data, theme = gen_coding_challenge()
    messages = [
        {"role": "system", "content": "You are a senior AI Engineer."},
        {"role": "user", "content": f"Fix this agent issue:\n{data}"}
    ]
    process_request_history(MODELS["PRIMARY"], messages, 800)
    return "Dev Sprint"

def run_rapid_check():
    print(" >>> [Mode: Rapid Check] Quick tech Q&A...")
    data, theme = gen_short_qa()
    process_request(MODELS["SECONDARY"], data, 300, 0.5)
    return "Rapid Check"

# ==========================================
# [스케줄러 로직]
# ==========================================
def get_korea_time():
    return datetime.now(timezone.utc) + timedelta(hours=9)

def job_logic():
    global last_run_status
    
    # API 키 확인
    if not API_KEY: 
        print("❌ Error: NOUS_API_KEY not found in environment variables.")
        last_run_status["status"] = "Error: No API Key"
        return

    hour = get_korea_time().hour
    current_time_str = get_korea_time().strftime('%Y-%m-%d %H:%M:%S')

    # 수면 모드 (03시~08시 KST)
    if 3 <= hour < 8:
        print(f"[{current_time_str}] 💤 Sleep mode active.")
        last_run_status = {"time": current_time_str, "mode": "Sleep", "status": "Sleeping..."}
        return

    # 실행 모드 결정
    dice = random.random()
    mode_name = ""
    try:
        if dice < 0.4: 
            mode_name = run_deep_analysis()
        elif dice < 0.8: 
            mode_name = run_dev_sprint()
        else: 
            mode_name = run_rapid_check()
        
        last_run_status = {"time": current_time_str, "mode": mode_name, "status": "Success"}
    except Exception as e:
        print(f"❌ Error during job execution: {e}")
        last_run_status = {"time": current_time_str, "mode": "Error", "status": str(e)}

# ==========================================
# [Railway Health Check 엔드포인트]
# ==========================================
@app.route('/')
def health_check():
    """웹 브라우저로 접속 시 봇 상태 표시"""
    html = f"""
    <html>
        <head>
            <title>AI Agent Status</title>
            <meta http-equiv="refresh" content="60"> </head>
        <body style="font-family: sans-serif; padding: 40px; line-height: 1.6;">
            <h1>🤖 AI Agent Status Board</h1>
            <div style="background: #f4f4f4; padding: 20px; border-radius: 10px;">
                <p><strong>🕒 Current KST:</strong> {get_korea_time().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>✅ Last Execution:</strong> {last_run_status['time']}</p>
                <p><strong>🛠️ Last Mode:</strong> {last_run_status['mode']}</p>
                <p><strong>📡 Status:</strong> <span style="color: {'green' if last_run_status['status'] == 'Success' else 'red'}">{last_run_status['status']}</span></p>
            </div>
            <p style="color: gray; margin-top: 20px;">* Running on Railway. Scheduling interval: 12-25 mins.</p>
        </body>
    </html>
    """
    return html

if __name__ == "__main__":
    print("=== AI Agent Started ===")
    
    # 1. 백그라운드 스케줄러 시작
    scheduler = BackgroundScheduler()
    # 12분 ~ 25분 사이 랜덤 간격으로 실행
    scheduler.add_job(job_logic, 'interval', minutes=random.randint(12, 25))
    scheduler.start()

    # 2. 서버 시작 시 1회 즉시 실행 (테스트용)
    print("🚀 Triggering initial test run...")
    threading.Thread(target=job_logic).start()

    # 3. Flask 웹 서버 실행 (Railway 포트 바인딩)
    print(f"🌍 Starting Web Server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)
