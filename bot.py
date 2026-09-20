import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Chào ông! Bot Lọ Mod Liên Quân đã sẵn sàng.\n"
        "👉 Ông chỉ cần **gửi trực tiếp file zip asset (ví dụ file 109.5MB)** vào đây, bot sẽ tự động nhận diện và xử lý cho ông nhé!"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận file do người dùng gửi trực tiếp vào chat để xử lý"""
    document = update.message.document
    if not document:
        return
        
    status_message = await update.message.reply_text(f"📥 Đang nhận file `{document.file_name}` từ ông...")
    
    try:
        # Tải file trực tiếp từ chat của người dùng về server
        file = await context.bot.get_file(document.file_id)
        local_path = os.path.join("/tmp", document.file_name)
        
        await status_message.edit_text("📥 Đang tải file asset về server (dung lượng lớn có thể mất vài giây)...")
        await file.download_to_drive(local_path)
        
        # Xử lý UnityPy hoặc thao tác file ở đây
        await status_message.edit_text("⚙️ Đang bóc tách và xử lý tài nguyên game...")
        
        output_path = local_path # Giữ nguyên hoặc đóng gói lại
        
        # Gửi trả file kết quả
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
        await status_message.edit_text(f"❌ Có lỗi xảy ra khi xử lý: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("Lỗi: Chưa cấu hình BOT_TOKEN!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    # Lắng nghe mọi file tài liệu (zip) người dùng gửi vào
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
