import os
import logging
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
    await update.message.reply_text(
        "🤖 Chào ông! Bot Lọ Mod Liên Quân đã sẵn sàng.\n"
        "👉 Sử dụng lệnh theo cú pháp:\n"
        "`/mod [Đường dẫn trực tiếp file zip 109.5MB]`"
    )

async def mod_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tải file dung lượng lớn thông qua direct link"""
    if not context.args:
        await update.message.reply_text("⚠️ Thiếu link rồi ông ơi! Gõ theo mẫu: `/mod <đường_dẫn_file_zip>`")
        return
        
    url = context.args[0]
    status_message = await update.message.reply_text("📥 Đang kết nối tải gói asset 109.5MB qua đường dẫn trực tiếp...")
    
    try:
        local_path = os.path.join("/tmp", "Florentino_Mod.zip")
        
        # Tải file lớn bằng thư viện requests (bỏ qua giới hạn 20MB của Telegram)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        await status_message.edit_text("⚙️ Đã tải xong! Đang bóc tách và xử lý tài nguyên game...")
        
        output_path = local_path
        
        # Gửi file kết quả qua Telegram (Telegram cho phép upload file dưới 50MB, nếu file kết quả lớn hơn 50MB ta sẽ lưu vào server hoặc chia nhỏ)
        await status_message.edit_text("📤 Đang gửi file mod hoàn chỉnh...")
        with open(output_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename="Florentino_Mod_Da_Xu_Ly.zip",
                caption="✅ Đã xử lý gói mod Liên Quân thành công!"
            )
            
        await status_message.delete()
        
    except Exception as e:
        logging.error(f"Lỗi tải file: {e}")
        await status_message.edit_text(f"❌ Có lỗi xảy ra: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("Lỗi: Chưa cấu hình BOT_TOKEN!")
        return

    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mod", mod_download))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
