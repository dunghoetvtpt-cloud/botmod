import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 1. Lưu khung mặc định (dạng gốc 000 và 599) trực tiếp vào trong code
DEFAULT_TEMPLATE_STRUCTURE = [
    "files/Resources/1.63.1/Ages/Prefab_Characters/Prefab_Hero/Actor_000_Actions.pkg.bytes",
    "files/Resources/1.63.1/Ages/Prefab_Characters/Prefab_Hero/CommonActions.pkg.bytes",
    "files/Resources/1.63.1/Databin/Client/Sound/BattleBank.bytes",
    "files/Resources/1.63.1/Databin/Client/Sound/HeroSound.bytes",
    "files/Resources/1.63.1/Databin/Client/Sound/LobbyBank.bytes",
    "files/Resources/1.63.1/Databin/Client/Sound/LobbySound.bytes",
    "files/Resources/1.63.1/KernelLua.pkg.bytes",
    "files/Resources/1.63.1/Prefab_Characters/Actor_000_Infos.pkg.bytes",
    "files/Resources/1.63.1/StableSystems_3.pkg.bytes",
    "files/Resources/1.63.1/StableSystems_3.pkg.bytes.bak",
    "files/Resources/1.63.1/assetbundle/battle/hero/599_lvmeng_battle_base.assetbundle",
    "files/Resources/1.63.1/assetbundle/show/hero/599_lvmeng_show_base.assetbundle"
]

def generate_hero_files(hero_id: str, hero_name: str) -> str:
    """Tạo cây thư mục cấu trúc cho tướng mới dựa trên ID và tên."""
    root_dir = f"Project_{hero_id}_{hero_name}"
    os.makedirs(root_dir, exist_ok=True)
    
    created_files_count = 0
    for path_template in DEFAULT_TEMPLATE_STRUCTURE:
        # Thay thế ID '000' hoặc '599' thành ID mới
        new_path = path_template.replace("000", hero_id).replace("599", hero_id)
        
        # Thay thế tên mẫu 'lvmeng' thành tên tướng mới
        if "lvmeng" in new_path.lower():
            new_path = new_path.replace("lvmeng", hero_name.lower())
            
        full_path = os.path.join(root_dir, new_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("") # Khởi tạo file trống
        created_files_count += 1
        
    return root_dir

# Lệnh /start hướng dẫn sử dụng
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào bạn! Bot đã sẵn sàng tạo khung dự án.\n\n"
        "Hãy gửi theo cú pháp:\n"
        "`/tao [ID_Tướng] [Tên_Tướng]`\n\n"
        "Ví dụ:\n"
        "`/tao 521 Florentino`",
        parse_mode="Markdown"
    )

# Lệnh /tao để xử lý tạo khung
async def tao_khung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Thiếu thông tin! Vui lòng nhập đúng cú pháp:\n`/tao [ID] [Tên]`\nVí dụ: `/tao 521 Florentino`", parse_mode="Markdown")
        return
    
    hero_id = args[0]
    hero_name = args[1]
    
    try:
        root_dir = generate_hero_files(hero_id, hero_name)
        await update.message.reply_text(
            f"✅ Tạo khung dự án thành công!\n"
            f"🆔 ID: `{hero_id}`\n"
            f"👤 Tên: `{hero_name}`\n"
            f"📁 Thư mục: `{root_dir}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Có lỗi xảy ra: {str(e)}")

def main():
    # Thay 'YOUR_BOT_TOKEN' bằng Token thực tế của bạn
    TOKEN = "8757645824:AAEy_4hGt3aE5fkd7nbg1pACF0iMvWEQzxA"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tao", tao_khung))
    
    print("Bot Telegram đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
