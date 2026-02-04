import os
import asyncio
import aiohttp
import logging
import random
import time

# 1. 로깅 설정: Railway 'View Logs'에서 즉시 확인 가능
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("NousTestWorker")

class NousTestFarmer:
    def __init__(self):
        # Railway Variables의 NOUS_API_KEY를 읽어옵니다.
        self.api_key = os.getenv('NOUS_API_KEY')
        self.api_url = "https://inference-api.nousresearch.com/v1/chat/completions"
        # 통계/경제 전공자다운 고엔트로피 주제군
        self.topics = [
            "중심극한정리와 표본 분포의 관계", 
            "베이즈 정리를 이용한 시장 변동성 예측", 
            "게임이론의 Nash 균형과 경제적 함의", 
            "시계열 분석의 자기상관성 검정"
        ]

    async def call_api(self, session, msg):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": "Hermes-3-Llama-3.1-405B",
            "messages": [{"role": "user", "content": msg}],
            "temperature": 0.82
        }
        try:
            async with session.post(self.api_url, json=payload, headers=headers, timeout=40) as r:
                if r.status == 200:
                    return True
                logger.error(f"API 에러 발생: {r.status}")
        except Exception as e:
            logger.error(f"연결 오류: {e}")
        return False

    async def run_experiment(self):
        r"""지수 분포 $X \sim \text{Exp}(\lambda)$ 기반의 무작위 지연 적용"""
        if not self.api_key:
            logger.error("❌ NOUS_API_KEY를 찾을 수 없습니다. Railway Variables를 확인하세요!")
            return

        logger.info("🚀 실험용 엔진 가동! 첫 번째 기여를 시작합니다...")
        
        async with aiohttp.ClientSession() as session:
            count = 0
            while True:
                topic = random.choice(self.topics)
                success = await self.call_api(session, topic)
                
                if success:
                    count += 1
                    logger.info(f"✅ [{count}회차] 기여 완료: {topic}")
                
                # 2. 통계적 무작위 지연 (평균 6
