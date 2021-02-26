# mpy_toogoodtogo
MicroPython TooGoodToGo watcher


## Setup: 

-Install micropython onto esp32 board

-copy boot.py,tgtg.py and reqs.py onto esp32 via tools like ampy

-create config.py which should have the following variables:

    essid = WLANNETWORK
    pw = WLANPASSWORD
    tgtg_email= TGTGEMAILADDRESS
    tgtg_pw= TGTGPACCOUNTPASSWORD
    telegram_token = TELEGRAMBOTTOKEN
    telegram_chat_id = TELEGRAMCHATID

-copy config.py onto board and it should run

## Usage:

ESP32 connects to wifi via essid and pw and fetches every 10 seconds the favorite items of TGTG account via tgtg_email and tgtg_pw. Telegram bot with token telegram_token sends message to telegram chat with telegram_chat_id.
