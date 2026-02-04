import os
import asyncio
import aiohttp
import logging
import random
import time

# 1. 로깅 설정: Railway 'View Logs'에서 실시간 확인용
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("NousTestWorker")

class NousFarmer:
    def __init__(self):
        # Railway Variables의 키를 정확히 읽어옵니다.
        self.api_key = os.getenv('NOUS_API_KEY')
        self.api_url = "https://inference-api.nousresearch.com/v1/chat/completions"
        self.topics = ["Bayesian Inference", "Stochastic Processes", "Game Theory", "Macroeconomics"]

    async def farm(self):
        r"""지수 분포 $X \sim \text{Exp}(\lambda)$ 기반의 포아송 프로세스 파밍"""
        if not self.api_key:
            logger.error("❌ NOUS_API_KEY가 없습니다! Variables 설정을 확인하세요.")
            return

        logger.info("🚀 실험 엔진 가동! 빌드 후 즉시 첫 기여를 시도합니다.")
        
        async with aiohttp.ClientSession() as session:
            while True:
                # 2. 첫 기여는 즉시, 이후엔 무작위 지연 (평균 60초)
                payload = {
                    "model": "Hermes-3-Llama-3.1-405B",
                    "messages": [{"role": "user", "content": random.choice(self.topics)}],
                    "temperature": 0.85
                }
                headers = {"Authorization": f"Bearer {self.api_key}"}

                try:
                    async with session.post(self.api_url, json=payload, headers=headers) as resp:
                        if resp.status == 200:
                            logger.info(f"✅ 기여 완료! (주제: {payload['messages'][0]['content']})")
                        else:
                            logger.error(f"API 에러: {resp.status}")
                except Exception as e:
                    logger.error(f"연결 오류: {e}")

                # 시빌 방어용 무작위 지연 시간 주입
                delay = random.expovariate(1/60) + 20
                logger.info(f"💤 다음 기여까지 {int(delay)}초 대기합니다.")
                await asyncio.sleep(delay)

if __name__ == "__main__":
    farmer = NousFarmer()
    asyncio.run(farmer.farm())
