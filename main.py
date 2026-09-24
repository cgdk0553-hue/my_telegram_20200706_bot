import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI

# ログ設定
logging.basicConfig(level=logging.INFO)

# 環境変数のセット
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "123456789"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# OpenAI クライアントの初期化
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ユーザーごとのタスクを保存する辞書
user_tasks = {}

# --- コマンドの処理 ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text(
        "こんにちは！あなた専用のBotです。\n"
        "/todo [内容] : タスク追加\n"
        "/list : タスク一覧\n"
        "/clear : タスク全削除\n"
        "/ai [質問] : AIに質問"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text(f"オウム返し: {update.message.text}")

# --- タスク管理機能 ---
async def add_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    user_id = update.effective_user.id
    task_content = " ".join(context.args)
    if not task_content:
        await update.message.reply_text("タスクの内容を入力してください。\n例: /todo 牛乳を買う")
        return
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    user_tasks[user_id].append(task_content)
    await update.message.reply_text(f"✅ タスクを追加しました:\n{task_content}")

async def list_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    user_id = update.effective_user.id
    tasks = user_tasks.get(user_id, [])
    if not tasks:
        await update.message.reply_text("📝 現在登録されているタスクはありません。")
    else:
        response = "📋 あなたのタスク一覧:\n"
        for i, task in enumerate(tasks, 1):
            response += f"{i}. {task}\n"
        await update.message.reply_text(response)

async def clear_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    user_id = update.effective_user.id
    if user_id in user_tasks:
        del user_tasks[user_id]
    await update.message.reply_text("🗑️ すべてのタスクを削除しました。")

# --- AI情報収集機能 ---
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("AIに聞きたいことを入力してください。\n例: /ai テレグラムボットの作り方")
        return

    if not client:
        await update.message.reply_text("⚠️ OpenAI APIキーが設定されていません。")
        return

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはTelegramで使える便利なアシスタントです。簡潔かつ分かりやすく回答してください。"},
                {"role": "user", "content": query}
            ]
        )
        answer = completion.choices[0].message.content
        await update.message.reply_text(answer)
        
    except Exception as e:
        await update.message.reply_text(f"AI処理中にエラーが発生しました: {str(e)}")

# --- メイン処理 (Python 3.12+ 対応) ---
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ハンドラーの登録
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    app.add_handler(CommandHandler("todo", add_todo))
    app.add_handler(CommandHandler("list", list_todos))
    app.add_handler(CommandHandler("clear", clear_todos))
    app.add_handler(CommandHandler("ai", ask_ai))
    
    # ボットを起動
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("Bot started... (Ctrl+C で停止)")
    
    # 停止信号を待つ
    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == '__main__':
    # asyncio.run() を使ってイベントループを安全に起動
    asyncio.run(main())
