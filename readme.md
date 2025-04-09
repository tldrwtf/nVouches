# nVouches Bot

nVouches Bot! This bot streamlines vouch submissions, enables recovery of past vouches, and provides vouch statistics. Follow the guide start using the bot.

## Features
- **`vouch`**: Submit a vouch with a review, star rating, product name, and optional screenshot.
- **`r`**: Recover all vouches and send them to the current channel.
- **`s`**: Show vouch statistics including total reviews and recent review counts.

## Install

### Setup

1. **Create a config file**

   Create a file named `config.ini` in the root directory with the following:

   ```ini
   [Bot]
   TOKEN = BOT TOKEN HERE
   STATUS = Monitoring vouches
   EMBED_COLOR = ff0000
   FOOTER_TEXT = By tldr/Neuro/Itchy https://github.com/tldrwtf
   THUMBNAIL_URL = https://cdn.discordapp.com/attachments/12761172432125308998/1234567898765456/9.jpg
   REVIEW_CHANNEL_ID = CHANNEL ID FOR VOUCHES TO BE SENT (integer)
   ACCESS_ROLE_ID = ROLE REQUIRED TO RUN COMMANDS (integer)
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### 🚀 Running the Bot

Run:

```bash
py main.py
```

## Commands

### `vouch`

- **Description**: Submit a vouch.
- **Usage**: `/vouch <product_name> <review_text> [stars] [screenshot]`
- **Stars**: Choose ⭐ (1), ⭐⭐ (2), ⭐⭐⭐ (3), ⭐⭐⭐⭐ (4), ⭐⭐⭐⭐⭐ (5)

### `restore`

- **Description**: Restore historical vouches received and saved.
- **Usage**: `/r`
- **Usage**: `.r`

### `stats`

- **Description**: Show stats.
- **Usage**: `/s`
- **Usage**: `.s`