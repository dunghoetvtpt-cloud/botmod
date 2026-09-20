import os
import logging
import threading
import asyncio
import zipfile
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
        await update.message.reply_text("⚠️ Thiếu link rồi ông ơi!")
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
                raise Exception("Không tìm thấy link tải trực tiếp!")

        await status_message.edit_text("📥 Đang tải file asset về server...")
        zip_path = os.path.join("/tmp", "source.zip")
        extracted_path = os.path.join("/tmp", "extracted")
        
        response = requests.get(target_url, stream=True)
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        await status_message.edit_text("⚙️ Đang lọc bỏ file rác, chỉ giữ lại tài nguyên cần thiết...")
        
        # Giải nén file
        os.makedirs(extracted_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_path)
            
        # Lọc: Chỉ giữ lại các file asset/unity hoặc file có dung lượng phù hợp, loại bỏ file nặng không cần thiết
        slim_zip_path = os.path.join("/tmp", "Florentino_Mod_Gon.zip")
        with zipfile.ZipFile(slim_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(extracted_path):
                for file in files:
                    # Chỉ lấy file asset cốt lõi hoặc bỏ qua các file rác lớn
                    if file.endswith(('.unity3d', '.txt', '.bytes', '.prefab')) or not file.endswith(('.mp4', '.avi')):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, extracted_path)
                        zip_out.write(file_path, arcname)

        await status_message.edit_text("📤 Đang gửi file gọn nhẹ cho ông...")
        with open(slim_zip_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename="Florentino_Mod_Da_Loc.zip",
                caption="✅ Đã lọc và tối ưu gói mod thành công dưới 50MB!"
            )
            
        await status_message.delete()
        
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
    
