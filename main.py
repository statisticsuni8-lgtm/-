import os
import time
import logging
import requests
import numpy as np
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 로깅 설정
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("NousNuclearFarmer")

class NousSystem:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_key = os.getenv('NOUS_API_KEY')
        self.api_url = "https://inference-api.nousresearch.com/v1/chat/completions"
        self.topics = ["통계적 유의성 검정", "베이즈 사후 확률", "내쉬 균형의 동학", "거시경제 유동성"]
        self.msg_count = 0
        self.scheduler = BackgroundScheduler()

    def call_api(self):
        if not self.api_key:
            logger.error("❌ NOUS_API_KEY가 없습니다!")
            return

        # KST 수면 주기 (00-08시 휴식 확률 85%)
        kst_hour = (datetime.utcnow().hour + 9) % 24
        if not (8 <= kst_hour <= 23) and np.random.rand() > 0.15:
            logger.info("💤 야간 휴식 중...")
            self.schedule_next(np.random.randint(1800, 3600))
            return

        topic = np.random.choice(self.topics)
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        payload = {
            "model": "Hermes-3-Llama-3.1-405B",
            "messages": [{"role": "user", "content": f"{topic}에 대해 짧게 답변해줘."}],
            "temperature": float(np.random.uniform(0.7, 0.9))
        }

        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=40)
            if resp.status_code == 200:
                self.msg_count += 1
                logger.info(f"✅ [기여 {self.msg_count}회] {topic}")
                # 지수 분포($\lambda=1/60$) 기반 무작위 지연
                self.schedule_next(int(np.random.exponential(60) + 20))
            else:
                logger.error(f"API Error: {resp.status_code}")
                self.schedule_next(60)
        except Exception as e:
            logger.error(f"Conn Error: {e}")
            self.schedule_next(120)

    def schedule_next(self, delay):
        run_date = datetime.now() + timedelta(seconds=delay)
        self.scheduler.add_job(self.call_api, 'date', run_date=run_date)
        logger.info(f"⏰ 다음 예약: {delay}초 후")

    async def report(self, u: Update, c: ContextTypes.DEFAULT_TYPE):
        await u.message.reply_text(f"📊 누적 기여: {self.msg_count}회\n(17M 아웃풋 유지 중)")

def main():
    sys = NousSystem()
    sys.scheduler.start()
    sys.schedule_next(5) # 빌드 후 5초 내 즉시 가동
    
    if sys.bot_token:
        app = Application.builder().token(sys.bot_token).build()
        app.add_handler(CommandHandler("report", sys.report))
        app.run_polling(drop_pending_updates=True)
    else:
        while True: time.sleep(100)

if __name__ == "__main__":
    main()
