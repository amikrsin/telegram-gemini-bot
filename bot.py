import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PRODUCT_API_KEY = os.environ.get("PRODUCT_API_KEY")  # no hardcoded fallback - set this in Render's env vars


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Mujhe kisi product ka naam bhejiye, main live e-commerce prices search karke batata hoon.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    status_msg = await update.message.reply_text("🔎 Live e-commerce prices search ho rahe hain...")

    if not PRODUCT_API_KEY:
        await status_msg.edit_text("⚠️ Bot config error: PRODUCT_API_KEY set nahi hai.")
        logging.error("PRODUCT_API_KEY environment variable is not set.")
        return

    try:
        headers = {
            'x-api-key': PRODUCT_API_KEY
        }

        # Official v2 endpoint with query parameters (Fixed syntax)
        response = requests.get(
            'https://api.openwebninja.com/realtime-product-search/v2/search',
            params={
                "q": query_text,
                "gl": "in"
            },
            headers=headers,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print("API Response:", data)
            products = data.get('data', []) or data.get('products', []) or data.get('shopping_results', [])
            if products:
                reply_text = f"🛒 **Live Search Results for '{query_text}':**\n\n"
                for idx, p in enumerate(products[:3], 1):
                    title = p.get('title') or p.get('name') or 'N/A'
                    price = p.get('price') or p.get('extracted_price') or p.get('detected_price') or 'N/A'
                    link = p.get('link') or p.get('product_link') or p.get('url') or '#'

                    reply_text += f"{idx}. **{title}**\n💰 Price: {price}\n🔗 [View Product]({link})\n\n"

                await status_msg.edit_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)
            else:
                await status_msg.edit_text("❌ Is product ke liye koi live results nahi mile.")
        else:
            await status_msg.edit_text(f"❌ API Error: Status code {response.status_code}")
    except Exception as e:
        print(f"API Request Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")


# --- Dummy HTTP server so Render's free Web Service sees an open $PORT ---
class _HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running.")

    def log_message(self, format, *args):
        pass  # keep Render logs clean of health-check pings


def start_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), _HealthCheckHandler)
    logging.info(f"Health-check server listening on port {port}")
    server.serve_forever()


def main():
    print("Bot Starting on Render...")

    # Start dummy server in background thread so Render marks the service healthy
    threading.Thread(target=start_health_check_server, daemon=True).start()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
