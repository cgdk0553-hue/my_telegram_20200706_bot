import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ログ設定
logging.basicConfig(level=logging.INFO)

# ★ Step 1で手に入れた情報をセット
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "123456789"))

# /start コマンドの処理
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return  # あなた以外からの操作は無視する
    await update.message.reply_text("こんにちは！あなた専用のBotです。何かメッセージを送ってみてください。")

# メッセージ返信の処理
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return  # あなた以外からの操作は無視する
    await update.message.reply_text(f"オウム返し: {update.message.text}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    print("Bot started...")
    app.run_polling()