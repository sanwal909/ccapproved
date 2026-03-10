import json
import logging
import os
from pathlib import Path

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode, ChatType
from telegram.ext import Application, ContextTypes, MessageHandler, CommandHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN") or "PUT_BOT_TOKEN_HERE"
OWNER_ID = int(os.getenv("OWNER_ID") or "0")

CUSTOM_TEXT = """🔥 Join Our Premium Channel
📢 Latest Updates Daily

Post No: {count}

👉 https://t.me/mixbadis9
"""

CONFIG_FILE = Path("channels.json")


# ---------------- CONFIG ---------------- #

def load_config():
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text())
    except:
        pass

    return {"channels": {}}


def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


# ---------------- UTIL ---------------- #

def is_media(msg):
    return any([
        msg.photo,
        msg.video,
        msg.document,
        msg.animation
    ])


def is_owner(update):
    if OWNER_ID == 0:
        return True

    user = update.effective_user
    return user and user.id == OWNER_ID


# ---------------- CHANNEL POST HANDLER ---------------- #

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        msg = update.effective_message
        chat = update.effective_chat

        if chat.type != ChatType.CHANNEL:
            return

        if not is_media(msg):
            return

        cfg = load_config()
        channels = cfg["channels"]

        ch = channels.get(str(chat.id))

        if not ch:
            return

        count = ch.get("count", 0) + 1
        ch["count"] = count

        caption_template = ch.get("caption", CUSTOM_TEXT)

        caption = caption_template.format(count=count)

        keyboard = None

        if ch.get("button"):

            text = ch.get("button_text")
            url = ch.get("button_url")

            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text, url=url)]]
            )

        save_config(cfg)

        try:

            await msg.edit_caption(
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )

        except Exception as e:

            logging.warning(f"Edit caption failed: {e}")

    except Exception as e:

        logging.error(e)


# ---------------- COMMANDS ---------------- #

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update):
        return

    try:

        args = context.args

        if len(args) < 1:
            await update.message.reply_text("Usage:\n/addchannel -100xxxx")
            return

        channel_id = args[0]

        cfg = load_config()

        cfg["channels"][channel_id] = {

            "caption": CUSTOM_TEXT,
            "count": 0,
            "button": False,
            "button_text": "",
            "button_url": ""

        }

        save_config(cfg)

        await update.message.reply_text(f"Channel added:\n{channel_id}")

    except Exception as e:

        await update.message.reply_text(str(e))


async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update):
        return

    args = context.args

    if len(args) < 1:
        await update.message.reply_text("/removechannel channel_id")
        return

    cfg = load_config()

    if args[0] in cfg["channels"]:
        del cfg["channels"][args[0]]

        save_config(cfg)

        await update.message.reply_text("Channel removed")


async def set_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update):
        return

    if len(context.args) < 2:

        await update.message.reply_text(
            "/setcaption channel_id caption"
        )
        return

    channel_id = context.args[0]

    caption = " ".join(context.args[1:])

    cfg = load_config()

    if channel_id not in cfg["channels"]:
        await update.message.reply_text("Channel not added")
        return

    cfg["channels"][channel_id]["caption"] = caption

    save_config(cfg)

    await update.message.reply_text("Caption updated")


async def enable_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update):
        return

    if len(context.args) < 3:

        await update.message.reply_text(
            "/enablebutton channel_id text url"
        )
        return

    channel_id = context.args[0]
    text = context.args[1]
    url = context.args[2]

    cfg = load_config()

    if channel_id not in cfg["channels"]:
        await update.message.reply_text("Channel not added")
        return

    ch = cfg["channels"][channel_id]

    ch["button"] = True
    ch["button_text"] = text
    ch["button_url"] = url

    save_config(cfg)

    await update.message.reply_text("Button enabled")


async def disable_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update):
        return

    if len(context.args) < 1:
        return

    cfg = load_config()

    ch = cfg["channels"].get(context.args[0])

    if not ch:
        return

    ch["button"] = False

    save_config(cfg)

    await update.message.reply_text("Button disabled")


async def set_count(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update):
        return

    if len(context.args) < 2:
        return

    channel_id = context.args[0]
    num = int(context.args[1])

    cfg = load_config()

    if channel_id not in cfg["channels"]:
        return

    cfg["channels"][channel_id]["count"] = num

    save_config(cfg)

    await update.message.reply_text("Count updated")


async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_owner(update):
        return

    cfg = load_config()

    txt = ""

    for cid, data in cfg["channels"].items():

        txt += f"{cid} | Post:{data['count']}\n"

    if not txt:
        txt = "No channels"

    await update.message.reply_text(txt)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    txt = """
Commands:

/addchannel -100xxxx

/removechannel -100xxxx

/setcaption -100xxxx Caption text {count}

/enablebutton -100xxxx text url

/disablebutton -100xxxx

/setcount -100xxxx number

/listchannels
"""

    await update.message.reply_text(txt)


# ---------------- MAIN ---------------- #

def main():

    logging.basicConfig(level=logging.INFO)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))

    app.add_handler(CommandHandler("addchannel", add_channel))
    app.add_handler(CommandHandler("removechannel", remove_channel))
    app.add_handler(CommandHandler("setcaption", set_caption))
    app.add_handler(CommandHandler("enablebutton", enable_button))
    app.add_handler(CommandHandler("disablebutton", disable_button))
    app.add_handler(CommandHandler("setcount", set_count))
    app.add_handler(CommandHandler("listchannels", list_channels))
    app.add_handler(CommandHandler("help", help_cmd))

    app.run_polling()


if __name__ == "__main__":
    main()
