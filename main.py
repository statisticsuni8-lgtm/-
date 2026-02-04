import os, asyncio, aiohttp, logging, random, time, json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
DATA_FILE = "stats.json"

class Storage:
    @staticmethod
    def load():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f: return json.load(f)
            except: return {}
        return {}
    @staticmethod
    def save(data):
        with open(DATA_FILE, 'w') as f: json.dump(data, f)

class NousOS:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.api_keys = {k: v for k, v in os.environ.items() if k.startswith('API_KEY_')}
        self.stats = Storage.load()
        self.topics = ["베이지안 사후 확률 추론", "게임 이론의 내쉬 균형", "행동경제학의 손실 회피", "시계열 분석의 자기상관"]

    async def call_nous(self, key, msg):
        headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        payload = {"model": "Hermes-3-Llama-3.1-405B", "messages": [{"role": "user", "content": msg}], "temperature": 0.85}
        async with aiohttp.ClientSession() as s:
            try:
                async with s.post("https://inference-api.nousresearch.com/v1/chat/completions", headers=headers, json=payload, timeout=30) as r:
                    if r.status == 200:
                        res = await r.json()
                        return res['choices'][0]['message']['content'].strip()
            except: pass
        return None

    async def worker(self, name, key):
        # 따옴표 앞에 'r'을 추가하여 SyntaxWarning 해결
        r"""독립적 확률 워커 ($P(A \cap B) = P(A)P(B)$ 확보)"""
        await asyncio.sleep(random.uniform(30, 300))
        while True:
            await asyncio.sleep(random.expovariate(1/50) + 15)
            kst = (time.localtime().tm_hour + 9) % 24
            if not (8 <= kst <= 23) and random.random() > 0.15:
                await asyncio.sleep(random.randint(1800, 3600))
                continue
            res = await self.call_nous(key, random.choice(self.topics))
            if res:
                self.stats[name] = self.stats.get(name, 0) + 1
                Storage.save(self.stats)

    async def report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = "📊 **Nous Farming OS 실시간 현황**\n---\n"
        for name, count in self.stats.items():
            msg += f"👤 {name}: {count} msg\n"
        msg += f"\n📈 **총합**: {sum(self.stats.values())} msg"
        await update.message.reply_text(msg, parse_mode='Markdown')

def main():
    sys = NousOS()
    if not sys.token: return
    app = Application.builder().token(sys.token).build()
    app.add_handler(CommandHandler("report", sys.report))
    
    # 워커 실행
    for name, key in sys.api_keys.items():
        asyncio.get_event_loop().create_task(sys.worker(name, key))
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
