import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = "8882717840:AAF5IgwDbHpmjdqgVf-nQ1vWoSePF_iZj1o"
GEMINI_API_KEY = "AQ.Ab8RN6K8GHB8dNtEz3brgv1Plswl9jRjneOhY66EjAKZcMJ2Eg"

client = genai.Client(api_key=GEMINI_API_KEY)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Mujhe kisi product ka naam bhejiye, main price check karke batata hoon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    status_msg = await update.message.reply_text("🔎 Product ke live price aur offers search ho rahe hain...")

    try:
        prompt = (
            f"Search the internet for current prices, discounts, and active deals for '{text}'. "
            f"Provide a clear summary with current prices and top 2 similar alternatives."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"tools": [{"google_search": {}}]}
        )

        if response.text:
            await status_msg.edit_text(response.text)
        else:
            await status_msg.edit_text("❌ Product details nahi mil payein.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")

def main():
    print("Bot Starting on Render...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()