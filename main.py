import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ログ設定
logging.basicConfig(level=logging.INFO)

# ★ Step 1で手に入れた情報をセット
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "123456789"))

# ユーザーごとのタスクを保存する辞書 (メモリ上での管理)
user_tasks = {}

# /start コマンドの処理
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text("こんにちは！あなた専用のBotです。\n/todos でタスク管理、/ai でAI検索ができます。")

# メッセージ返信の処理 (オウム返し)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text(f"オウム返し: {update.message.text}")

# --- ここからタスク管理機能 ---

# /todo [内容] でタスクを追加
async def add_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    user_id = update.effective_user.id
    # コマンドの後ろにある文字列を取得
    task_content = " ".join(context.args)
    
    if not task_content:
        await update.message.reply_text("タスクの内容を入力してください。\n例: /todo 牛乳を買う")
        return

    if user_id not in user_tasks:
        user_tasks[user_id] = []
    
    user_tasks[user_id].append(task_content)
    await update.message.reply_text(f"✅ タスクを追加しました:\n{task_content}")

# /list でタスク一覧を表示
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

# /clear でタスクを全削除
async def clear_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    user_id = update.effective_user.id
    if user_id in user_tasks:
        del user_tasks[user_id]
    await update.message.reply_text("🗑️ すべてのタスクを削除しました。")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ハンドラーの登録
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    # タスク管理用ハンドラーの追加
    app.add_handler(CommandHandler("todo", add_todo))
    app.add_handler(CommandHandler("list", list_todos))
    app.add_handler(CommandHandler("clear", clear_todos))
    
    print("Bot started...")
    app.run_polling()
