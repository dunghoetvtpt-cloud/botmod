import os
import logging
import threading
import asyncio
import requests
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Lọ Mod đã sẵn sàng! Gõ `/mod <link_mediafire>`")

async def mod_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Thiếu link rồi ông ơi! Gõ theo mẫu: `/mod <link_mediafire>`")
        return
        
    url = context.args[0]
    status_message = await update.message.reply_text("🔍 Đang bóc tách Direct Link từ MediaFire...")
    
    try:
        target_url = url
        if "mediafire.com" in url:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            download_btn = soup.find('a', id='downloadButton')
            if download_btn and 'href' in download_btn.attrs:
                target_url = download_btn['href']
            else:
                raise Exception("Không tìm thấy link tải trực tiếp từ trang MediaFire này!")

        # Gửi thẳng link tải trực tiếp cho người dùng, không qua trung gian tốn băng thông
        await status_message.edit_text(
            f"✅ **Đã lấy thành công Direct Link!**\n\n"
            f"🔗 Link tải trực tiếp tốc độ cao:\n{target_url}\n\n"
            f"👉 Ông bấm vào link trên để tải thẳng về máy không lo nghẽn mạng nhé!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Lỗi: {e}")
        await status_message.edit_text(f"❌ Có lỗi xảy ra: {str(e)}")

def main():
    if not BOT_TOKEN:
        return
    threading.Thread(target=run_web_server, daemon=True).start()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mod", mod_download))
    app.run_polling()

if __name__ == '__main__':
    main()
    
