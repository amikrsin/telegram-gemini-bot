import os
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- Dummy HTTP Health Check Server (Render Port Binding Fix) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running live on Render!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Health check server listening on port {port}")
    server.serve_forever()

# --- Telegram Bot Logic ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Mujhe kisi product ka naam bhejiye, main price check karke batata hoon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    status_msg = await update.message.reply_text("🔎 Product ke live price aur offers search ho rahe hain...")

    try:
        client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options={'api_version': 'v1alpha'}
        )

        prompt = (
            f"Search the internet for current prices, discounts, and active deals for '{text}'. "
            f"Provide a clear summary with current prices and top 2 similar alternatives."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        if response.text:
            await status_msg.edit_text(response.text)
        else:
            await status_msg.edit_text("❌ Product details nahi mil payein.")

    except Exception as e:
        print(f"Gemini API Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

def main():
    # Start Dummy Web Server in background thread for Render
    server_thread = Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    print("Bot Starting on Render...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
