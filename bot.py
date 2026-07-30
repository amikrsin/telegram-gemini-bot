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
    await update.message.reply_text("👋 Hello! Mujhe kisi product ka naam bhejiye, main live prices search karke batata hoon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    status_msg = await update.message.reply_text("🔎 Live e-commerce prices search ho rahe hain...")

    try:
        headers = {
            "X-API-Key": PRODUCT_API_KEY
        }
        
        response = requests.get(
            'https://api.openwebninja.com/realtime-product-search/search-light-v2',
            params={"q": query_text, "country": "in"}, # Country India set kiya hai
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print("API Response:", data) # Render logs me data print hoga

            # Flexible keys check (products, data, results, items)
            products = data.get('products') or data.get('data') or data.get('results') or data.get('items', [])

            if not products and isinstance(data, list):
                products = data

            if products:
                reply_text = f"🛒 **Live Search Results for '{query_text}':**\n\n"
                for idx, p in enumerate(products[:3], 1):
                    # Alag-alag possible keys for title, price, link
                    title = p.get('title') or p.get('name') or 'N/A'
                    price = p.get('price') or p.get('extracted_price') or p.get('offer_price') or 'N/A'
                    link = p.get('link') or p.get('product_link') or p.get('url') or '#'
                    
                    reply_text += f"{idx}. **{title}**\n💰 Price: {price}\n🔗 [View Product]({link})\n\n"
                
                await status_msg.edit_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)
            else:
                await status_msg.edit_text(f"❌ API se data mila lekin products list empty hai. (Response: {str(data)[:100]})")
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
