import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Thiết lập log để dễ theo dõi trạng thái bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Lấy Token từ biến môi trường trên Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

# File ID chuẩn của gói mod Florentino (109.5MB) trên Kênh riêng tư
TEMPLATE_FILE_ID = "BQACAgUAAxkBAAEit6Nqr3nLyPqForprXnAal6rYaDoMQwAC6CIAAtJleFVTaJUS_57lXT0E"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start chào hỏi hướng dẫn"""
    await update.message.reply_text(
        "🤖 Chào ông! Bot Lọ Mod Liên Quân đã sẵn sàng.\n"
        "Gõ lệnh `/modflo` để test hệ thống tải, giải nén và đóng gói gói mod 109.5MB."
    )

async def modflo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh xử lý gói mod Florentino"""
    status_message = await update.message.reply_text("⏳ Đang kết nối lấy gói asset 109.5MB từ kho lưu trữ riêng tư...")
    
    try:
        # 1. Tải file từ Telegram ID về thư mục tạm /tmp
        file = await context.bot.get_file(TEMPLATE_FILE_ID)
        local_path = os.path.join("/tmp", "Florentino_Mod.zip")
        await status_message.edit_text("📥 Đang tải file asset 109.5MB về server (quá trình này mất vài giây)...")
        await file.download_to_drive(local_path)
        
        # 2. Xử lý logic giả lập / UnityPy tại đây (có thể mở rộng thay thế asset)
        await status_message.edit_text("⚙️ Đang xử lý bóc tách và đóng gói lại tài nguyên bằng UnityPy...")
        
        # Giả lập thời gian xử lý hoặc thao tác file zip tại đây nếu cần
        output_path = local_path # Dùng lại file hoặc nén lại kết quả mới
        
        # 3. Gửi file kết quả trả ngược lại cho người dùng
        await status_message.edit_text("📤 Đang gửi file mod hoàn chỉnh về cho ông...")
        with open(output_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename="Florentino_Mod_Da_Xu_Ly.zip",
                caption="✅ Đã hoàn tất xử lý gói mod Liên Quân thành công!"
            )
            
        await status_message.delete()
        
    except Exception as e:
        logging.error(f"Lỗi xử lý mod: {e}")
        await status_message.edit_text(f"❌ Có lỗi xảy ra: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("Lỗi: Chưa cấu hình BOT_TOKEN trong biến môi trường!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Đăng ký các lệnh
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("modflo", modflo))

    print("Bot đang khởi động và sẵn sàng nhận lệnh...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
