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
PRODUCT_API_KEY = os.environ.get("PRODUCT_API_KEY", "ak_vkc5a52ocak1wsnp1iatmtoeikurrospvxbnofl8y6eazg9")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Mujhe kisi product ka naam bhejiye, main live e-commerce prices search karke batata hoon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    status_msg = await update.message.reply_text("🔎 Live e-commerce prices search ho rahe hain...")

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

def main():
    print("Bot Starting on Render...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
