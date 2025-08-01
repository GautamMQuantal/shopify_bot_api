
import os
import requests
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SHOPIFY_ADMIN_API_TOKEN = os.getenv("SHOPIFY_ADMIN_API_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

def handle_user_input_with_pelican_support(user_input: str) -> str:
    session_state = {
        "conversation": [],
        "awaiting_clarification": False,
        "clarification_type": "",
        "clarification_data": [],
        "original_query": "",
        "original_product": None,
        "clarified_variant": "",
        "original_requested_info": []
    }

    def extract_product_info(product):
        variants = product.get("variants", [])
        options = [v.get("title", "") for v in variants]
        return {
            "title": product.get("title", ""),
            "options": options,
            "price": variants[0].get("price", "") if variants else "N/A"
        }

    def fetch_shopify_products():
        url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-04/products.json"
        headers = {
            "X-Shopify-Access-Token": SHOPIFY_ADMIN_API_TOKEN,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("products", [])
        return []

    def query_openai(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a Shopify product store."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    products = fetch_shopify_products()
    matched_products = []
    for product in products:
        if any(word.lower() in product.get("title", "").lower() for word in user_input.split()):
            matched_products.append(product)

    if len(matched_products) == 1:
        info = extract_product_info(matched_products[0])
        response = f"{info['title']} is available for ${info['price']}. Options: {', '.join(info['options'])}"
    elif len(matched_products) > 1:
        titles = [p.get("title", "Untitled") for p in matched_products]
        response = f"I found multiple products: {', '.join(titles)}. Could you please specify the color or variant?"
    else:
        prompt = f"User asked: '{user_input}'. No product matched directly. Suggest a helpful response."
        response = query_openai(prompt)

    session_state["conversation"].append(("user", user_input))
    session_state["conversation"].append(("bot", response))

    # Build response history
    result = ""
    for role, message in session_state["conversation"]:
        result += f"{role.upper()}: {message}\n"
    return result.strip()
