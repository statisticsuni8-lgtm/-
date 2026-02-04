import os
import time
import logging
import requests
import numpy as np
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 로깅 설정: Railway 'View Logs'에서 즉시 확인 가능
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("NousExpFarmer")

class NousApsSystem:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_key = os.getenv('NOUS_API_KEY')
        self.api_url = "https://inference-api.nousresearch.com/v1/chat/completions"
        self.topics = ["통계적 유의성 검정", "베이즈 사후 확률 추론", "게임이론의 내쉬 균형", "거시경제 유동성 분석"]
        self.msg_count = 0
        self.scheduler = BackgroundScheduler()

    def call_api(self):
        """requests와 numpy를 활용한 즉시 가동형 API 호출"""
        if not self.api_key:
            logger.error("❌ NOUS_API_KEY가 없습니다! Variables를 확인하세요.")
            return

        # KST 수면 주기 반영 (00시~08시 활동 확률 15% 미만 제한)
        kst_hour = (datetime.utcnow().hour + 9) % 24
        if not (8 <= kst_hour <= 23) and np.random.rand() > 0.15:
            logger.info("💤 야간 수면 주기: 통계적으로 이번 턴은 쉽니다.")
            self.schedule_next(np.random.randint(1800, 3600))
            return

        topic = np.random.choice(self.topics)
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        payload = {
            "model": "Hermes-3-Llama-3.1-405B",
            "messages": [{"role": "user", "content": f"{topic}에 대해 학술적으로 답변해줘."}],
            "temperature": float(np.random.uniform(0.7, 0.95))
        }

        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=40)
            if resp.status_code == 200:
                self.msg_count += 1
                logger.info(f"✅ [테스트 성공/기여 {self.msg_count}회] 주제: {topic}")
                # 다음 기여 시간: 지수 분포 적용 (평균 60초)
                next_delay = int(np.random.exponential(60) + 20)
                self.schedule_next(next_delay)
            else:
                logger.error(f"⚠️ API 에러: {resp.status_code}")
                self.schedule_next(60)
        except Exception as e:
            logger.error(f"📡 연결 오류: {e}")
            self.schedule_next(120)

    def schedule_next(self, delay_seconds):
        run_time = datetime.now() + timedelta(seconds=delay_seconds)
        self.scheduler.add_job(self.call_api, 'date', run_date=run_time)
        logger.info(f"⏰ 다음 기여 예약: {delay_seconds}초 후 실행")

    async def report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"📊 현재 {self.msg_count}회차 기여 중\n(17M 아웃풋 자산 유지됨)")

def main():
    sys = NousApsSystem()
    sys.scheduler.start()
    
    # [핵심] 빌드 직후 5초 뒤 즉시 첫 실험 가동 시작
    sys.schedule_next(5)
    
    if sys.bot_token:
        app = Application.builder().token(sys.bot_token).build()
        app.add_handler(CommandHandler("report", sys.report))
        logger.info("🚀 봇과 스케줄러 가동 준비 완료.")
        app.run_polling(drop_pending_updates=True)
    else:
        logger.info("📡 텔레그램 토큰 없음: 스텔스 모드 가동.")
        while True: time.sleep(100)

if __name__ == "__main__":
    main()
