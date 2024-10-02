from pyrogram import Client, filters
import requests
import time

# Define your Telegram bot token and other variables
API_ID = 5461760
API_HASH = '396b10bcf5e1ed5fcc71f1603800b7cf'
BOT_TOKEN = '6658351224:AAHdlDUfEOmK4DHzoB_Pj2oUgZVEDUO9zLI'
TRON_ADDRESS = 'TM1Ka2tdNdy9VWD7iW7bGDazbHy8Z3TKNg'  # Your TRON wallet address
ADMIN_CONTACT = 't.me/siddhant_devil'  # Admin contact link
IMAGE_PATH = 'image.jpg'  # Path to your image file
TRONSCAN_API_KEY = '54689f27-9369-40e0-87b0-ce08a46243f3'  # Your Tronscan API key

# Store verified transactions in a dictionary
verified_transactions = {}

app = Client("crypto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("crypto"))
def send_crypto_info(client, message):
    # Send TRON address with an image
    message.reply_photo(
        photo=IMAGE_PATH,
        caption=(
            f"Your TRON address is: {TRON_ADDRESS}\n\n"
            "To verify your payment:\n"
            "1. Send the amount to the above address.\n"
            "2. Click the button below to verify your payment."
        ),
        reply_markup=app.create_inline_keyboard([
            [("Verify Payment", "verify_payment")],
        ])
    )

@app.on_callback_query(filters.regex("verify_payment"))
def verify_payment_query(client, callback_query):
    # Ask user to send the transaction ID
    callback_query.answer()  # Acknowledge callback
    callback_query.message.reply_text(
        "Please send the transaction ID for payment verification."
    )

@app.on_message(filters.text & ~filters.command)
def handle_payment_verification(client, message):
    # Assume the message is the transaction ID
    transaction_id = message.text.strip()

    # Check if the payment is verified
    payment_verified = check_payment(transaction_id)

    if payment_verified:
        # Store the verified transaction with the current timestamp
        verified_transactions[transaction_id] = time.time()
        message.reply_text("Your payment is verified!")
    else:
        message.reply_text(
            "Payment not received or transaction ID is older than 10 minutes. Please contact admin for support.",
            reply_markup=app.create_inline_keyboard([
                [("Contact Admin", ADMIN_CONTACT)],
            ])
        )

def check_payment(transaction_id):
    # Call Tronscan API to check the transaction
    url = f'https://api.tronscan.org/api/transaction/{transaction_id}'
    headers = {
        'accept': 'application/json',
        'TRON-PRO-API-KEY': TRONSCAN_API_KEY  # Include your API key in the headers
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        # Check if the transaction is directed to the TRON address
        to_address = data.get('raw_data', {}).get('contract', [{}])[0].get('parameter', {}).get('value', {}).get('to', '')
        
        # Verify if the transaction ID is in verified transactions and check age
        if transaction_id in verified_transactions:
            # Check if the transaction is older than 10 minutes
            current_time = time.time()
            if current_time - verified_transactions[transaction_id] <= 600:  # 600 seconds = 10 minutes
                return True  # Transaction ID is verified and recent
        
        # Check if the transaction is sent to your TRON address
        if to_address == TRON_ADDRESS:
            return True  # Payment verified
        
    return False  # Payment not verified

if __name__ == "__main__":
    app.start()
    app.idle()
