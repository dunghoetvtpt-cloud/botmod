import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Web server giả lập để Render Web Service không bị lỗi cổng HTTP
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận file zip do người dùng gửi trực tiếp để xử lý"""
    document = update.message.document
    if not document:
        return
        
    status_message = await update.message.reply_text(f"📥 Đang nhận file `{document.file_name}`...")
    
    try:
        file = await context.bot.get_file(document.file_id)
        local_path = os.path.join("/tmp", document.file_name)
        
        await status_message.edit_text("📥 Đang tải file asset 109.5MB về server...")
        await file.download_to_drive(local_path)
        
        await status_message.edit_text("⚙️ Đang bóc tách và xử lý tài nguyên game...")
        output_path = local_path
        
        await status_message.edit_text("📤 Đang gửi file mod hoàn chỉnh về cho ông...")
        with open(output_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"Mod_Done_{document.file_name}",
                caption="✅ Đã xử lý xong gói mod Liên Quân thành công!"
            )
            
        await status_message.delete()
        
    except Exception as e:
        logging.error(f"Lỗi xử lý file: {e}")
        await status_message.edit_text(f"❌ Có lỗi xảy ra: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("Lỗi: Chưa cấu hình BOT_TOKEN!")
        return

    # Chạy Web Server ngầm ở một luồng riêng để đáp ứng yêu cầu của Render Web Service
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    # Khởi động Telegram Bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Bot đang chạy polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
