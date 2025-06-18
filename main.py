import requests
import sqlite3
import os
import logging
import time
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# ===== إعدادات البوت =====
TOKEN = os.environ.get('BOT_TOKEN', '7402242317:AAFOEfkocX3s-ZwX2-vMgcav-JGhw8Xt5Eo')
ADMIN_CHAT_ID = os.environ.get('ADMIN_ID', '5356044364')

# ===== إعداد التسجيل =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== مصادر الأحداث =====
EVENT_SOURCES = {
    "Binance": "https://www.binance.com/en/support/announcement/c-48",
    "Bybit": "https://www.bybit.com/en-US/support/announcement",
    "KuCoin": "https://www.kucoin.com/news/categories/announcement",
    "OKX": "https://www.okx.com/support/hc/en-us/sections/360000030652-Latest-Announcements",
    "Coinbase": "https://blog.coinbase.com/",
    "Gate.io": "https://www.gate.io/announcement",
    "Bitget": "https://www.bitget.com/support/articles"
}

KEYWORDS = ['reward', 'bonus', 'deposit', 'free', 'contest', 'competition', 
            'promotion', 'airdrop', 'giveaway', 'event', 'mission', 'task',
            'مكافأة', 'هدية', 'تسجيل', 'مسابقة', 'عرض', 'ترويج', 'اكتتاب']

# ===== إدارة قاعدة البيانات =====
def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS events
                (id TEXT PRIMARY KEY, title TEXT, url TEXT, source TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

def save_event(event_id, title, url, source):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?)", 
              (event_id, title, url, source, now))
    conn.commit()
    conn.close()

def is_new_event(event_id):
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute("SELECT id FROM events WHERE id=?", (event_id,))
    exists = c.fetchone() is not None
    conn.close()
    return not exists

# ===== كشط الأحداث لجميع المنصات =====
def scrape_events():
    new_events = []
    
    # Binance
    try:
        response = requests.get(EVENT_SOURCES["Binance"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.css-1l93ch0 a'):
            title = item.text.strip()
            if any(keyword in title.lower() for keyword in KEYWORDS):
                event_id = "binance_" + item['href'].split('/')[-1]
                url = "https://www.binance.com" + item['href']
                
                if is_new_event(event_id):
                    new_events.append({
                        'title': f"🎁 Binance: {title}",
                        'url': url,
                        'source': 'Binance'
                    })
                    save_event(event_id, title, url, 'Binance')
    except Exception as e:
        logger.error(f"Binance error: {str(e)[:100]}")
    
    # Bybit
    try:
        response = requests.get(EVENT_SOURCES["Bybit"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.article-title a'):
            title = item.text.strip()
            if any(keyword in title.lower() for keyword in KEYWORDS):
                event_id = "bybit_" + item['href'].split('/')[-1]
                url = "https://www.bybit.com" + item['href']
                
                if is_new_event(event_id):
                    new_events.append({
                        'title': f"🎯 Bybit: {title}",
                        'url': url,
                        'source': 'Bybit'
                    })
                    save_event(event_id, title, url, 'Bybit')
    except Exception as e:
        logger.error(f"Bybit error: {str(e)[:100]}")
    
    # KuCoin
    try:
        response = requests.get(EVENT_SOURCES["KuCoin"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.kucoin-news-list a'):
            title = item.select_one('.title').text.strip()
            if any(keyword in title.lower() for keyword in KEYWORDS):
                event_id = "kucoin_" + item['href'].split('/')[-1]
                url = "https://www.kucoin.com" + item['href']
                
                if is_new_event(event_id):
                    new_events.append({
                        'title': f"🎮 KuCoin: {title}",
                        'url': url,
                        'source': 'KuCoin'
                    })
                    save_event(event_id, title, url, 'KuCoin')
    except Exception as e:
        logger.error(f"KuCoin error: {str(e)[:100]}")
    
    # OKX
    try:
        response = requests.get(EVENT_SOURCES["OKX"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.article-list li a'):
            title = item.text.strip()
            if any(keyword in title.lower() for keyword in KEYWORDS):
                event_id = "okx_" + item['href'].split('/')[-1]
                url = "https://www.okx.com" + item['href']
                
                if is_new_event(event_id):
                    new_events.append({
                        'title': f"🚀 OKX: {title}",
                        'url': url,
                        'source': 'OKX'
                    })
                    save_event(event_id, title, url, 'OKX')
    except Exception as e:
        logger.error(f"OKX error: {str(e)[:100]}")
    
    # Gate.io
    try:
        response = requests.get(EVENT_SOURCES["Gate.io"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.article-list li a'):
            title = item.text.strip()
            if any(keyword in title.lower() for keyword in KEYWORDS):
                event_id = "gateio_" + item['href'].split('/')[-1]
                url = "https://www.gate.io" + item['href']
                
                if is_new_event(event_id):
                    new_events.append({
                        'title': f"🔔 Gate.io: {title}",
                        'url': url,
                        'source': 'Gate.io'
                    })
                    save_event(event_id, title, url, 'Gate.io')
    except Exception as e:
        logger.error(f"Gate.io error: {str(e)[:100]}")
    
    # Bitget
    try:
        response = requests.get(EVENT_SOURCES["Bitget"], timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.article-item a'):
            title = item.text.strip()
            if any(keyword in title.lower() for keyword in KEYWORDS):
                event_id = "bitget_" + item['href'].split('/')[-1]
                url = "https://www.bitget.com" + item['href']
                
                if is_new_event(event_id):
                    new_events.append({
                        'title': f"💰 Bitget: {title}",
                        'url': url,
                        'source': 'Bitget'
                    })
                    save_event(event_id, title, url, 'Bitget')
    except Exception as e:
        logger.error(f"Bitget error: {str(e)[:100]}")
    
    return new_events

# ===== وظائف البوت =====
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(
        f"مرحباً {user.first_name}!\nأنا بوت مراقبة أحداث التداول المجانية 🚀\n"
        "سأرسل لك إشعارات عن:\n"
        "🎁 مكافآت التسجيل • 💰 عروض الإيداع\n"
        "🏆 مسابقات التداول • 🎯 الأحداث المجانية\n\n"
        "المنصات المدعومة:\n"
        "Binance, Bybit, KuCoin, OKX, Coinbase, Gate.io, Bitget",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("آخر الأحداث", callback_data='latest_events')],
            [InlineKeyboardButton("مساعدة", callback_data='help')]
        ])
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "⚙️ الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/events - عرض آخر 10 أحداث\n"
        "/help - المساعدة\n\n"
        "البوت سيراقب الأحداث تلقائياً كل 10 دقائق"
    )

def latest_events(update: Update, context: CallbackContext):
    try:
        conn = sqlite3.connect('events.db')
        c = conn.cursor()
        c.execute("SELECT title, url, source FROM events ORDER BY created_at DESC LIMIT 10")
        events = c.fetchall()
        conn.close()
        
        if not events:
            update.message.reply_text("🔎 لم يتم العثور على أحداث بعد")
            return
            
        response = "📅 آخر 10 أحداث:\n\n"
        for i, (title, url, source) in enumerate(events, 1):
            response += f"{i}. {source}: {title}\n{url}\n\n"
        
        update.message.reply_text(response, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"حدث خطأ: {e}")
        update.message.reply_text("⚠️ حدث خطأ أثناء جلب الأحداث")

def check_events(context: CallbackContext):
    logger.info("🔍 جاري البحث عن أحداث جديدة...")
    new_events = scrape_events()
    if new_events:
        logger.info(f"✅ تم العثور على {len(new_events)} حدث جديد")
        for event in new_events:
            message = f"{event['title']}\n\n🔗 {event['url']}"
            try:
                context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID, 
                    text=message,
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"فشل الإرسال: {e}")
    else:
        logger.info("❌ لم يتم العثور على أحداث جديدة")

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == 'latest_events':
        latest_events(update, context)
    elif query.data == 'help':
        help_command(update, context)

# ===== التشغيل الرئيسي =====
def main():
    logger.info("جارٍ تشغيل البوت...")
    init_db()
    
    try:
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("events", latest_events))
        dp.add_handler(CallbackQueryHandler(button_handler))

        job_queue = updater.job_queue
        job_queue.run_repeating(check_events, interval=600, first=5)

        logger.info("✅ البوت يعمل الآن!")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"فشل تشغيل البوت: {str(e)}")

if __name__ == '__main__':
    main()