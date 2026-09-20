import os
import zipfile
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import UnityPy

# Bật log để theo dõi tiến trình
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Cấu hình Token Bot và File ID mẫu 109.5MB trên Kênh Telegram của ông
BOT_TOKEN = os.environ.get("BOT_TOKEN", "NHAP_TOKEN_BOT_CUA_ONG")
TEMPLATE_FILE_ID = "BQACAgUAAxkBAAEit6Nqr3nLyPqForprXnAal6rYaDoMQwAC6CIAAtJleFVTaJUS_57lXT0E"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Chào ông! Bot Lọ Mod Liên Quân đã sẵn sàng.\n"
        "Gõ lệnh `/modflo` để test hệ thống tải, giải nén và đóng gói gói mod 109.5MB."
    )

async def xu_ly_mod_flo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Đang kéo file khung 109.5MB từ kênh Telegram về Server...")
    
    tmp_zip = "/tmp/template_flo.zip"
    extract_dir = "/tmp/working_dir/"
    output_zip = "/tmp/Florentino_Vụ_Ảnh_Lang_Hồn_Custom.zip"
    
    try:
        # 1. Tải file mẫu từ Telegram về thư mục tạm /tmp/
        file_obj = await context.bot.get_file(TEMPLATE_FILE_ID)
        await file_obj.download_to_drive(tmp_zip)
        
        await msg.edit_text("📂 Đang giải nén gói mod cấu trúc chuẩn...")
        # Tạo thư mục làm việc sạch sẽ
        if os.path.exists(extract_dir):
            import shutil
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        await msg.edit_text("⚙️ Đang quét và xử lý các file Asset/UnityPy...")
        
        # Ví dụ: Duyệt qua các file assetbundle bên trong để sẵn sàng thay thế texture/skill khi cần
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".assetbundle"):
                    file_path = os.path.join(root, file)
                    # Ở đây ông có thể dùng UnityPy.load(file_path) để can thiệp sâu hơn nếu muốn
                    pass

        await msg.edit_text("📦 Đang đóng gói lại thành file .zip hoàn chỉnh...")
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, extract_dir)
                    zip_out.write(full_path, rel_path)
                    
        await msg.edit_text("🚀 Đang gửi file kết quả cho ông...")
        await update.message.reply_document(
            document=open(output_zip, "rb"),
            filename="Florentino_Vụ_Ảnh_Lang_Hồn_Custom.zip",
            caption="✅ Gói Mod 109.5MB đã được Bot xử lý và đóng gói thành công!"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {str(e)}")
        
    finally:
        # Dọn dẹp bộ nhớ đệm trên Server để nhẹ máy
        for p in [tmp_zip, output_zip]:
            if os.path.exists(p):
                os.remove(p)
        await msg.delete()

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("modflo", xu_ly_mod_flo))
    
    print("🤖 Bot đang chạy cực mượt...")
    app.run_polling()
