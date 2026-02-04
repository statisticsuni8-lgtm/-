import os
import asyncio
import aiohttp
import logging
import random
import time

# 로깅 설정: Railway 'View Logs'에서 실시간 확인 가능
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("NousWorker")

class NousFarmer:
    def __init__(self):
        # 스크린샷에 설정하신 변수명을 정확히 읽어옵니다.
        self.api_key = os.getenv('NOUS_API_KEY')
        self.api_url = "https://inference-api.nousresearch.com/v1/chat/completions"
        self.topics = ["Bayesian Inference", "Stochastic Processes", "Game Theory", "Macroeconomics"]

    async def farm(self):
        r"""지수 분포 $X \sim \text{Exp}(\lambda)$ 기반의 포아송 프로세스 파밍"""
        if not self.api_key:
            logger.error("NOUS_API_KEY가 설정되지 않았습니다!")
            return

        logger.info("🚀 파밍 엔진 가동 시작")
        
        async with aiohttp.ClientSession() as session:
            while True:
                # 1. 시빌 방어용 무작위 지연 (평균 60초)
                delay = random.expovariate(1/60) + 20
                await asyncio.sleep(delay)

                # 2. 메시지 전송
                payload = {
                    "model": "Hermes-3-Llama-3.1-405B",
                    "messages": [{"role": "user", "content": random.choice(self.topics)}],
                    "temperature": 0.85
                }
                headers = {"Authorization": f"Bearer {self.api_key}"}

                try:
                    async with session.post(self.api_url, json=payload, headers=headers) as resp:
                        if resp.status == 200:
                            logger.info("📡 기여 완료 (로그 확인됨)")
                        else:
                            logger.error(f"에러 발생: {resp.status}")
                except Exception as e:
                    logger.error(f"연결 오류: {e}")

if __name__ == "__main__":
    farmer = NousFarmer()
    asyncio.run(farmer.farm())
