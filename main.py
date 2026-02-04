import os
import time
import logging
import requests
import numpy as np
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. 로깅 설정: Railway 'View Logs'에서 실시간 확인 가능
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("NousApsFarmer")

class NousApsSystem:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_key = os.getenv('NOUS_API_KEY') # 배리어블의 키 로드
        self.api_url = "https://inference-api.nousresearch.com/v1/chat/completions"
        self.topics = ["중심극한정리의 통계적 의미", "베이즈 정리를 활용한 데이터 추론", "게임이론과 전략적 안정성", "행동경제학의 의사결정 모델"]
        self.msg_count = 0
        self.scheduler = BackgroundScheduler()

    def call_nous(self):
        r"""Numpy를 활용한 확률적 API 호출 로직"""
        if not self.api_key:
            logger.error("❌ NOUS_API_KEY가 설정되지 않았습니다!")
            return

        # KST 수면 주기 반영 (00시~08시 사이에는 활동 확률 15% 미만으로 제한)
        kst_hour = (datetime.utcnow().hour + 9) % 24
        if not (8 <= kst_hour <= 23) and np.random.rand() > 0.15:
            logger.info("💤 야간 수면 모드: 이번 턴은 통계적으로 휴식합니다.")
            self.schedule_next(np.random.randint(1800, 3600))
            return

        topic = np.random.choice(self.topics)
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        payload = {
            "model": "Hermes-3-Llama-3.1-405B",
            "messages": [{"role": "user", "content": f"{topic}에 대해 2문장으로 깊이 있게 답해줘."}],
            "temperature": float(np.random.uniform(0.7, 0.95))
        }

        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=45)
            if resp.status_code == 200:
                self.msg_count += 1
                logger.info(f"✅ [기여 {self.msg_count}회 달성] 주제: {topic}")
                # 다음 기여 시간을 지수 분포에 따라 무작위 설정 (평균 60초)
                next_delay = int(np.random.exponential(60) + 20)
                self.schedule_next(next_delay)
            else:
                logger.error(f"⚠️ API 에러: {resp.status_code}")
                self.schedule_next(60) # 에러 시 1분 후 재시도
        except Exception as e:
            logger.error(f"📡 연결 오류: {e}")
            self.schedule_next(120)

    def schedule_next(self, delay_seconds):
        """APScheduler를 이용한 다음 작업 예약"""
        run_time = datetime.now() + timedelta(seconds=delay_seconds)
        self.scheduler.add_job(self.call_nous, 'date', run_date=run_time)
        logger.info(f"⏰ 다음 기여 예정: {delay_seconds}초 후")

    async def report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"📊 실시간 현황: {self.msg_count}회 기여 중\n(17M 아웃풋 자산 유지됨)")

def main():
    sys = NousApsSystem()
    
    # 빌드 완료 직후 10초 뒤에 첫 실험 가동 시작
    sys.scheduler.start()
    sys.schedule_next(10)
    
    if sys.bot_token:
        app = Application.builder().token(sys.bot_token).build()
        app.add_handler(CommandHandler("report", sys.report))
        logger.info("🚀 봇과 스케줄러가 동시에 가동되었습니다.")
        app.run_polling(drop_pending_updates=True)
    else:
        logger.info("📡 텔레그램 토큰 없음: 스텔스 파밍 모드로 가동합니다.")
        while True: time.sleep(100)

if __name__ == "__main__":
    main()
