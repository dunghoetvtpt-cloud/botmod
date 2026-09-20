import os
import logging
import threading
import asyncio
import requests
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Thiết lập ghi log hệ thống
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Web server giả lập duy trì cổng 10000 cho Render
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
    await update.message.reply_text(
        "🤖 Chào ông! Bot Lọ Mod Liên Quân đã sẵn sàng.\n"
        "👉 Sử dụng cú pháp lệnh:\n"
        "`/mod <link_mediafire>`"
    )

async def mod_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Thiếu link rồi ông ơi! Gõ theo mẫu: `/mod <link_mediafire>`")
        return
        
    url = context.args[0]
    status_message = await update.message.reply_text("📥 Đang phân tích đường dẫn MediaFire...")
    
    try:
        target_url = url
        if "mediafire.com" in url:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            download_btn = soup.find('a', id='downloadButton')
            if download_btn and 'href' in download_btn.attrs:
                target_url = download_btn['href']
            else:
                raise Exception("Không tìm thấy nút tải trực tiếp từ trang MediaFire này!")

        await status_message.edit_text("📥 Đang tiến hành tải gói asset 109.5MB về server Render...")
        local_path = os.path.join("/tmp", "Florentino_Mod.zip")
        
        response = requests.get(target_url, stream=True)
        response.raise_for_status()
        
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        await status_message.edit_text("📤 Đang gửi file hoàn chỉnh cho ông...")
        with open(local_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename="Florentino_Mod_Da_Xu_Ly.zip",
                caption="✅ Đã xử lý gói mod Liên Quân thành công!"
            )
            
        await status_message.delete()
        
    except Exception as e:
        logging.error(f"Lỗi xử lý file MediaFire: {e}")
        await status_message.edit_text(f"❌ Có lỗi xảy ra: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("Lỗi: Chưa cấu hình BOT_TOKEN!")
        return

    # Chạy Web Server ngầm cho Render
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    # Khởi tạo và chạy bot an toàn với event loop riêng
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mod", mod_download))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
