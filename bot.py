import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# OpenWebNinja API Key yahan environment variable ya direct set kar sakte hain
PRODUCT_API_KEY = os.environ.get("PRODUCT_API_KEY", "ak_vkc5a52ocak1wsnp1iatmtoeikurrospvxbnofl8y6eazg9")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Mujhe kisi product ka naam bhejiye, main live e-commerce prices search karke batata hoon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    status_msg = await update.message.reply_text("🔎 Live e-commerce prices fetch ho rahe hain...")

    try:
        headers = {
            "X-API-Key": PRODUCT_API_KEY
        }
        
        # OpenWebNinja Realtime Product Search API Call
        response = requests.get(
            'https://api.openwebninja.com/realtime-product-search/search-light-v2',
            params={"q": query_text},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            products = data.get('products', []) # API response structure ke mutabik

            if products:
                reply_text = f"🛒 **Live Search Results for '{query_text}':**\n\n"
                # Top 3 products dikhayein
                for idx, p in enumerate(products[:3], 1):
                    title = p.get('title', 'N/A')
                    price = p.get('price', 'N/A')
                    link = p.get('link', '#')
                    reply_text += f"{idx}. **{title}**\n💰 Price: {price}\n🔗 [View Product]({link})\n\n"
                
                await status_msg.edit_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)
            else:
                await status_msg.edit_text("❌ Is product ke liye koi live results nahi mile.")
        else:
            await status_msg.edit_text(f"❌ API Error: Status code {response.status_code}")

    except Exception as e:
        print(f"API Request Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

def main():
    print("Bot Starting on Render...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
