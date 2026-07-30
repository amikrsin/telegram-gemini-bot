import os
import logging
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Mujhe kisi product ka naam bhejiye, main price check karke batata hoon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    status_msg = await update.message.reply_text("🔎 Product ke live price aur offers search ho rahe hain...")

    try:
        # Pass API key with v1alpha options for developer API keys
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
    print("Bot Starting on Render...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
