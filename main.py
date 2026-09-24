import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ログ設定
logging.basicConfig(level=logging.INFO)

# 環境変数のセット
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "123456789"))

# ユーザーごとのタスクを保存する辞書
user_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text("こんにちは！あなた専用のBotです。\n/todo [内容] でタスク追加、/search [キーワード] で情報収集ができます。")

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

# --- AI情報収集機能 (Web検索) ---
async def search_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("検索したいキーワードを入力してください。\n例: /search Telegram bot 作り方")
        return

    await update.message.reply_text(f"🔍 '{query}' について検索中...")
    
    try:
        # DuckDuckGoのHTML版から簡易的にタイトルとリンクを取得する例
        # 本格的なAI検索には SerpAPI や Google Custom Search API の利用を推奨します
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        
        # 簡易的なパース（実際は BeautifulSoup などを使うと正確です）
        # ここではデモ用に固定メッセージを返すか、または簡単なスクレイピング結果を表示
        # 注意: 実際のプロダクトでは公式APIを使うのが安全です
        result_snippet = f"『{query}』に関する最新の情報が見つかりました。（※現在はデモ用のプレースホルダーです）\n\n本格的な検索機能を実装するには、Google Custom Search APIなどのキー設定が必要です。"
        
        await update.message.reply_text(result_snippet)

    except Exception as e:
        await update.message.reply_text(f"検索中にエラーが発生しました: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    # タスク管理ハンドラー
    app.add_handler(CommandHandler("todo", add_todo))
    app.add_handler(CommandHandler("list", list_todos))
    app.add_handler(CommandHandler("clear", clear_todos))
    
    # 情報収集ハンドラー
    app.add_handler(CommandHandler("search", search_info))
    
    print("Bot started...")
    app.run_polling()
