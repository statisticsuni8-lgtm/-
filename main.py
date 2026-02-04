import os, asyncio, aiohttp, logging, random, time, json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. 로깅 및 로컬 데이터 설정
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger("NousFarmer")
STATS_FILE = "stats.json"

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f: json.dump(stats, f)

class NousSystem:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        # API_KEY_MAIN, API_KEY_SUB 등 'API_KEY_'로 시작하는 모든 환경변수 수집
        self.keys = {k: v for k, v in os.environ.items() if k.startswith('API_KEY_')}
        self.stats = load_stats()
        self.topics = ["통계적 유의성", "베이즈 정리", "게임 이론", "행동 경제학", "거시 경제 지표"]

    async def call_api(self, key, msg):
        headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        payload = {
            "model": "Hermes-3-Llama-3.1-405B",
            "messages": [{"role": "user", "content": msg}],
            "temperature": 0.85
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post("https://inference-api.nousresearch.com/v1/chat/completions", 
                                        headers=headers, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['choices'][0]['message']['content'].strip()
            except Exception as e:
                logger.error(f"API Error: {e}")
        return None

    async def farm_worker(self, name, key):
        """독립적인 확률 프로세스 기반 워커"""
        logger.info(f"🚀 [{name}] 파밍 엔진 가동")
        await asyncio.sleep(random.uniform(10, 300)) # 시작 시간 분산
        
        while True:
            # 포아송 분포 기반 지연 (평균 50초)
            await asyncio.sleep(random.expovariate(1/50) + 15)
            
            # KST 기준 수면 주기 모사 (밤 시간대 활동 감소)
            kst_hour = (time.localtime().tm_hour + 9) % 24
            if not (8 <= kst_hour <= 23) and random.random() > 0.15:
                await asyncio.sleep(random.randint(1800, 3600))
                continue

            response = await self.call_api(key, random.choice(self.topics))
            if response:
                self.stats[name] = self.stats.get(name, 0) + 1
                save_stats(self.stats)
                if self.stats[name] % 10 == 0:
                    logger.info(f"📡 [{name}] 기여도: {self.stats[name]}회 달성")

    async def report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = "📊 **Nous Farming OS 현황 보고**\n---\n"
        for name, count in self.stats.items():
            msg += f"👤 {name}: {count} msg\n"
        msg += f"\n📈 **합계**: {sum(self.stats.values())} msg"
        await update.message.reply_text(msg, parse_mode='Markdown')

async def main():
    system = NousSystem()
    if not system.bot_token:
        logger.error("TELEGRAM_BOT_TOKEN이 없습니다!")
        return

    app = Application.builder().token(system.bot_token).build()
    app.add_handler(CommandHandler("report", system.report))

    # 모든 계정 워커를 백그라운드 태스크로 실행
    for name, key in system.keys.items():
        asyncio.create_task(system.farm_worker(name, key))
    
    logger.info(f"Detected {len(system.keys)} keys. Starting engine...")
    
    await app.initialize()
    await app.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
