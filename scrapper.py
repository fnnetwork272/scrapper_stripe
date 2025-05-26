import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import os
from app import AdvancedCardChecker
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API Configuration
api_id = 25005379  # Replace with your actual API ID
api_hash = "f17fb76fd7acaca5ed44e0c04e260eaa"  # Replace with your actual API hash
session_name = "cc_scraper"
session_string = os.getenv("TELEGRAM_SESSION_STRING", "1BVtsOHkBuz4_Ji7QXzid2bKSXUxtjVR8QrYlu7I5IwK4QgwBGem5h3-uHUIYLDuShG2eHouBckZ7tBf12oIo5OG51mE2T85PLYGQguAihivLcCq9bV3UZ4kzG5SQWEYmkM2mN-ISe63hEJ_cukKsvEYL_Qt6qTF1DvA9GLVWY7-qOtsI06XFr9Ib857a-1jQjQs7hHS2jrMfxbjGm07UHEPpvHfae9jE4BE2la6QdwIQIelJjp1NyAHkjt7rR-kmmed6cm5axMog-sWcpiMELKexHHUijYU2qwU2NV5v4Nt5DHnW_gGNlt5hj7jDVEZ1mVs6mDkRAOq9QpWdBBeRsaYmwQtvnuw=")  # Use environment variable for security

# Sources Configuration
source_groups = [-1002410570317, -1001878543352]  # Add source group IDs
source_channels = []  # Add source channel IDs
target_channels = [-1002319403142]  # Add target channel IDs

# Initialize Telegram client
if session_string:
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
else:
    client = TelegramClient(session_name, api_id, api_hash)

# Initialize card checker
card_checker = AdvancedCardChecker()

# Set up Selenium for Render
selenium_options = Options()
selenium_options.add_argument('--headless')
selenium_options.add_argument('--no-sandbox')
selenium_options.add_argument('--disable-dev-shm-usage')
selenium_options.binary_location = "/opt/render/project/.render/chrome/google-chrome"
driver = webdriver.Chrome(options=selenium_options, executable_path="/usr/local/bin/chromedriver")

# CC patterns
cc_patterns = [
        r'(?:𝗖𝗖|CC)\s*➼\s*(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',
    
    r'[•\*\-]\s*CC\s+(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',

    # Format 2 & 9 & 10: 5262190163068118|01|2029|923 or 4432290821938088|07|28|183 or 5517760000228621|08|27|747
    r'(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',

    # Format 3: 5563800132516965\n03/27\n196
    r'(\d{13,16})\n(\d{2})/(\d{2,4})\n(\d{3,4})',

    # Format 4 & 11: 4628880202243142 10/27 501 or 5168404154402888 03/26 416
    r'(\d{13,16})\s(\d{2})/(\d{2,4})\s(\d{3,4})',

    # Format 5: CCNUM: 4622630013568831 CVV: 577 EXP: 12/2027
    r'CCNUM:?\s*(\d{13,16})\s*CVV:?\s*(\d{3,4})\s*EXP:?\s*(\d{1,2})/(\d{2,4})',

    # Format 6: NR: 4130220014499932 Holder: Merre Friend CVV: 703 EXPIRE: 03/28
    r'NR:?\s*(\d{13,16})\s*(?:Holder:.*?\s*)?CVV:?\s*(\d{3,4})\s*EXPIRE:?\s*(\d{1,2})/(\d{2,4})',

    # Format 7: Card: 5289460011885479 Exp. month: 9 Exp. year: 25 CVV: 350
    r'Card:?\s*(\d{13,16})\s*Exp\. month:?\s*(\d{1,2})\s*Exp\. year:?\s*(\d{2,4})\s*CVV:?\s*(\d{3,4})',

    # Format 8: 4019240106255832|03/26|987|小関美華|Doan|コセキ ミカ|k.mika.0801@icloud.com|0
    r'(\d{13,16})\|(\d{2})/(\d{2,4})\|(\d{3,4})(?:\|.*)?',

    # New Format 2: ╔ ● CC: 4491042736323072|12|2030|105
    r'[╔]\s*[●]\s*CC:?\s*(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',

    # Format 1: • CC  5418792156740992|04|2027|267
    r'[•\*\-]\s*CC\s+(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',

    # Format 2 & 9 & 10: 5262190163068118|01|2029|923 or 4432290821938088|07|28|183 or 5517760000228621|08|27|747
    r'(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',

    # Format 3: 5563800132516965\n03/27\n196
    r'(\d{13,16})\n(\d{2})/(\d{2,4})\n(\d{3,4})',

    # Format 4 & 11: 4628880202243142 10/27 501 or 5168404154402888 03/26 416
    r'(\d{13,16})\s(\d{2})/(\d{2,4})\s(\d{3,4})',

    # Format 5: CCNUM: 4622630013568831 CVV: 577 EXP: 12/2027
    r'CCNUM:?\s*(\d{13,16})\s*CVV:?\s*(\d{3,4})\s*EXP:?\s*(\d{1,2})/(\d{2,4})',

    # Format 6: NR: 4130220014499932 Holder: Merre Friend CVV: 703 EXPIRE: 03/28
    r'NR:?\s*(\d{13,16})\s*(?:Holder:.*?\s*)?CVV:?\s*(\d{3,4})\s*EXPIRE:?\s*(\d{1,2})/(\d{2,4})',

    # Format 7: Card: 5289460011885479 Exp. month: 9 Exp. year: 25 CVV: 350
    r'Card:?\s*(\d{13,16})\s*Exp\. month:?\s*(\d{1,2})\s*Exp\. year:?\s*(\d{2,4})\s*CVV:?\s*(\d{3,4})',
    r'(\d{13,16})[\s|/|\-|~]?\s*(\d{1,2})[\s|/|\-|~]?\s*(\d{2,4})[\s|/|\-|~]?\s*(\d{3,4})',
    r'(\d{13,16})[\s|/|\-|~]?\s*(\d{1,2})[\s|/|\-|~]?\s*(\d{2,4})[\s|/|\-|~]?\s*(\d{3,4})',
    r'(\d{13,16})\s(\d{1,2})\s(\d{2,4})\s(\d{3,4})',
    r'(\d{13,16})\n(\d{1,2})\n(\d{2,4})\n(\d{3,4})',
    r'(\d{13,16})\n(\d{1,2})[/|-](\d{2,4})\n(\d{3,4})',
    r'(\d{13,16})[:|=|>]?(\d{1,2})[:|=|>]?(\d{2,4})[:|=|>]?(\d{3,4})',
    r'(\d{13,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',
    r'cc(?:num)?:[\s]?(\d{13,16})[\s\n]+(?:exp|expiry|expiration):[\s]?(\d{1,2})[/|-](\d{2,4})[\s\n]+(?:cvv|cvc|cv2):[\s]?(\d{3,4})',
    r'(?:cc|card)(?:num)?[\s:]+(\d{13,16})[\s\n]+(?:exp|expiry|expiration)[\s:]+(\d{1,2})[/|-](\d{2,4})[\s\n]+(?:cvv|cvc|cv2)[\s:]+(\d{3,4})',
    r'(\d{13,16})(?:\s*(?:card|exp|expiry|expiration)\s*(?:date)?\s*[:|=|-|>])?\s*(\d{1,2})(?:\s*[/|-])?\s*(\d{2,4})(?:\s*(?:cvv|cvc|cv2)\s*[:|=|-|>])?\s*(\d{3,4})',
    r'(?:.*?:)?\s*(\d{13,16})\s*(?:\n|\r\n|\r)(?:.*?)?(\d{1,2})[/|-](\d{2}|20\d{2})(?:\n|\r\n|\r)(\d{3,4})(?:.*)',
    r'(?:.*?:)?\s*(\d{13,16})\|(\d{1,2})\|(\d{2})\|(\d{3,4})(?:\|.*)?',
    r'(?:.*?)NR:?\s*(\d{13,16})(?:.*?)EXPIRE:?\s*(\d{1,2})[/|-](\d{2}|20\d{2})(?:.*?)CVV:?\s*(\d{3,4})(?:.*)',
    r'(?:.*?)CVV:?\s*(\d{3,4})(?:.*?)EXPIRE:?\s*(\d{1,2})[/|-](\d{2}|20\d{2})(?:.*?)NR:?\s*(\d{13,16})(?:.*)',
    r'(?:.*?)(\d{13,16})(?:.*?)(\d{1,2})[/|-](\d{2}|20\d{2})(?:.*?)(\d{3,4})(?:.*)',
]

# Format CC to desired format
def format_cc(match):
    groups = match.groups()
    if len(groups) == 4:
        if len(groups[2]) >= 3 and len(groups[2]) <= 4 and len(groups[3]) == 2:
            cc, cvv, mm, yy = groups
        else:
            cc, mm, yy, cvv = groups
    else:
        return None
    
    cc = cc.strip()
    mm = mm.strip().zfill(2)
    yy = yy.strip()
    if len(yy) == 4:
        yy = yy[-2:]
    cvv = cvv.strip()
    
    if not (13 <= len(cc) <= 19) or not (3 <= len(cvv) <= 4):
        return None
        
    return f"{cc}|{mm}|{yy}|{cvv}"

# Function to log in to Telegram Web
def login_to_telegram():
    driver.get("https://web.telegram.org/k/")
    # Customize login logic (phone number, verification code)
    time.sleep(10)  # Adjust based on login time

# Function to click the "View Card" button
async def click_view_card_button():
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View Card')]"))
        )
        button.click()
        return True
    except Exception as e:
        logger.error(f"Error clicking button: {str(e)}")
        return False

# Function to get the Telegraph URL
async def get_telegraph_url():
    try:
        original_window = driver.current_window_handle
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
        telegraph_url = driver.current_url
        driver.close()
        driver.switch_to.window(original_window)
        return telegraph_url
    except Exception as e:
        logger.error(f"Error getting Telegraph URL: {str(e)}")
        return None

# Function to scrape CC details from Telegraph page
async def scrape_telegraph_page(telegraph_url):
    try:
        response = requests.get(telegraph_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find('pre')
        if content:
            return content.text
        return None
    except Exception as e:
        logger.error(f"Error scraping Telegraph page: {str(e)}")
        return None

# Define sources
def get_sources():
    sources = []
    if source_groups:
        sources.extend(source_groups)
    if source_channels:
        sources.extend(source_channels)
    return sources

# Scraper Event Handler
@client.on(events.NewMessage(chats=get_sources() if get_sources() else None))
async def cc_scraper(event):
    if "⭐ New Drop ⭐" in event.raw_text:
        try:
            chat_id = event.chat_id
            message_id = event.message.id
            driver.get(f"https://web.telegram.org/k/#?tgaddr=tg://msg?chat_id={chat_id}&message_id={message_id}")
            if await click_view_card_button():
                telegraph_url = await get_telegraph_url()
                if telegraph_url:
                    text = await scrape_telegraph_page(telegraph_url)
                    if text:
                        found_ccs = set()
                        for pattern in cc_patterns:
                            for match in re.finditer(pattern, text):
                                formatted_cc = format_cc(match)
                                if formatted_cc:
                                    found_ccs.add(formatted_cc)
                        if found_ccs:
                            for cc in found_ccs:
                                try:
                                    result = await card_checker.check_card(cc)
                                    if result:
                                        message = result['message']
                                        for channel_id in target_channels:
                                            try:
                                                await client.send_message(channel_id, message, parse_mode="HTML")
                                                logger.info(f"Sent approved CC {cc} to channel {channel_id}")
                                            except Exception as e:
                                                logger.error(f"Error sending to channel {channel_id}: {str(e)}")
                                    else:
                                        logger.info(f"CC {cc} declined or blacklisted")
                                except Exception as e:
                                    logger.error(f"Error checking CC {cc}: {str(e)}")
                    else:
                        logger.error("Failed to scrape CC details")
                else:
                    logger.error("Failed to retrieve Telegraph URL")
            else:
                logger.error("Failed to click 'View Card' button")
        except Exception as e:
            logger.error(f"Error processing message {event.message.id}: {str(e)}")

# Run Client
async def main():
    try:
        login_to_telegram()
        await client.start()
        logger.info("CC Scraper started")
        sources = get_sources()
        if sources:
            logger.info(f"Monitoring {len(sources)} source(s)")
        else:
            logger.warning("No sources specified")
        if target_channels:
            logger.info(f"Sending to {len(target_channels)} channel(s)")
        else:
            logger.warning("No target channels specified")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error starting client: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
