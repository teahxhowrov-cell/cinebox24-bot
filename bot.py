import os, sqlite3, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB = os.getenv("DB_PATH", "cinebox24.db")
AD_URL = os.getenv("AD_URL", "").strip()
logging.basicConfig(level=logging.INFO)

CATEGORIES = {
    "movies": "🎬 মুভি",
    "music": "🎵 গান",
    "drama": "📺 নাটক",
    "viral": "🔥 ভাইরাল ভিডিও",
    "shorts": "⚡ শর্ট ভিডিও",
}
pending = {}

def db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL, title TEXT NOT NULL,
        file_id TEXT NOT NULL, file_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, referred_by INTEGER,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    con.commit()
    return con

def main_menu():
    rows = [[InlineKeyboardButton(label, callback_data=f"cat:{key}")]
            for key, label in CATEGORIES.items()]
    return InlineKeyboardMarkup(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    con = db()
    con.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (uid,))
    con.commit(); con.close()
    await update.message.reply_text(
        "🎥 স্বাগতম CINEBOX 24-এ!\nমুভি, গান, নাটক ও ভিডিওর ক্যাটাগরি বেছে নিন।",
        reply_markup=main_menu()
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("এই কমান্ডটি শুধু Admin-এর জন্য।")
        return
    await update.message.reply_text(
        "🛠 Admin Panel\n"
        "/addvideo — ভিডিও যোগ\n"
        "/stats — ভিডিও ও ইউজার সংখ্যা\n"
        "/setad URL — বিজ্ঞাপন লিংক সেট\n"
        "ভিডিও যোগ করতে /addvideo লিখুন।"
    )

async def addvideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    pending[update.effective_user.id] = {"step": "category"}
    rows = [[InlineKeyboardButton(label, callback_data=f"admincat:{key}")]
            for key, label in CATEGORIES.items()]
    await update.message.reply_text("ভিডিওর ক্যাটাগরি বেছে নিন:", reply_markup=InlineKeyboardMarkup(rows))

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    con = db()
    v = con.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
    u = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    con.close()
    await update.message.reply_text(f"📊 মোট ভিডিও: {v}\n👥 মোট ইউজার: {u}")

async def setad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AD_URL
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("ব্যবহার: /setad https://example.com")
        return
    AD_URL = context.args[0]
    await update.message.reply_text("বিজ্ঞাপনের লিংক এই বট চালু থাকা পর্যন্ত সেট হয়েছে। স্থায়ী করতে হোস্টের AD_URL সেটিংসেও দিন।")

async def on_text_or_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    state = pending.get(uid)
    if not state or uid != ADMIN_ID: return
    if state.get("step") == "title":
        title = update.message.text or "নামহীন ভিডিও"
        state["title"] = title
        state["step"] = "media"
        await update.message.reply_text("এখন ভিডিওটি পাঠান (Telegram video হিসেবে)।")
        return
    if state.get("step") == "media":
        msg = update.message
        if msg.video:
            file_id, typ = msg.video.file_id, "video"
        elif msg.audio:
            file_id, typ = msg.audio.file_id, "audio"
        elif msg.document:
            file_id, typ = msg.document.file_id, "document"
        else:
            await msg.reply_text("ভিডিও/অডিও/ফাইল পাঠান।")
            return
        con = db()
        con.execute("INSERT INTO videos(category,title,file_id,file_type) VALUES (?,?,?,?)",
                    (state["category"], state["title"], file_id, typ))
        con.commit(); con.close()
        pending.pop(uid, None)
        await msg.reply_text("✅ কনটেন্ট সংরক্ষিত হয়েছে।", reply_markup=main_menu())

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data.startswith("admincat:"):
        if q.from_user.id != ADMIN_ID: return
        pending[q.from_user.id] = {"step": "title", "category": data.split(":",1)[1]}
        await q.message.reply_text("ভিডিওর নাম/পর্ব লিখুন:")
        return
    if data.startswith("cat:"):
        key = data.split(":",1)[1]
        con = db()
        rows = con.execute("SELECT id,title FROM videos WHERE category=? ORDER BY id DESC LIMIT 50", (key,)).fetchall()
        con.close()
        if not rows:
            await q.message.reply_text("এই ক্যাটাগরিতে এখনো কোনো ভিডিও নেই।", reply_markup=main_menu())
            return
        kb = [[InlineKeyboardButton(title, callback_data=f"video:{vid}")] for vid,title in rows]
        kb.append([InlineKeyboardButton("⬅️ Main Menu", callback_data="home")])
        await q.message.reply_text("ভিডিও বেছে নিন:", reply_markup=InlineKeyboardMarkup(kb))
    elif data == "home":
        await q.message.reply_text("🏠 Main Menu", reply_markup=main_menu())
    elif data.startswith("video:"):
        vid = int(data.split(":",1)[1])
        con = db()
        row = con.execute("SELECT title,file_id,file_type FROM videos WHERE id=?", (vid,)).fetchone()
        con.close()
        if not row:
            await q.message.reply_text("ভিডিওটি পাওয়া যায়নি।"); return
        title, file_id, typ = row
        if AD_URL:
            kb = [[InlineKeyboardButton("📢 বিজ্ঞাপন দেখুন", url=AD_URL)],
                  [InlineKeyboardButton("▶️ Continue to video", callback_data=f"send:{vid}")]]
            await q.message.reply_text(f"ভিডিও: {title}\nপ্রথমে বিজ্ঞাপনের লিংকটি খুলুন, তারপর Continue চাপুন।",
                                       reply_markup=InlineKeyboardMarkup(kb))
        else:
            await q.message.reply_text("বিজ্ঞাপন এখনো সেট করা হয়নি। ভিডিও পাঠানো হচ্ছে।")
            await send_content(q, row)
    elif data.startswith("send:"):
        vid = int(data.split(":",1)[1])
        con = db()
        row = con.execute("SELECT title,file_id,file_type FROM videos WHERE id=?", (vid,)).fetchone()
        con.close()
        if row: await send_content(q, row)

async def send_content(q, row):
    title, file_id, typ = row
    chat_id = q.message.chat_id
    if typ == "video":
        await q.message.reply_video(file_id, caption=f"🎬 {title}")
    elif typ == "audio":
        await q.message.reply_audio(file_id, caption=f"🎵 {title}")
    else:
        await q.message.reply_document(file_id, caption=title)

def main():
    if not TOKEN or not ADMIN_ID:
        raise SystemExit("BOT_TOKEN এবং ADMIN_ID environment variables সেট করুন।")
    db().close()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addvideo", addvideo))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("setad", setad))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT | filters.VIDEO | filters.AUDIO | filters.Document.ALL, on_text_or_media))
    app.run_polling()

if __name__ == "__main__":
    main()
