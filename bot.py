# This Repo was not fully owned by me. Some codes are scraped from respected DEVOLEPERS whom where mine friends. 
# check Readme.md For More. 

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)
import os, re, time, math, json, string, random, traceback, wget, asyncio, datetime, aiofiles, aiofiles.os, requests, youtube_dl, lyricsgenius, wget
import yt_dlp
from config import Config
from random import choice 
from pyrogram import Client, filters
from youtube_search import YoutubeSearch
from youtubesearchpython import VideosSearch
from database import Database
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid


Bot = Client(
    "Song Downloader Bot",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)

db = Database()

START_TEXT = """ 𝙷𝚊𝚒 {}, 
𝙸 𝙰𝚖 𝙼𝙷𝚈𝚃𝚍𝚕𝙱𝚘𝚃 𝚋𝚢 𝚌𝚛𝚎𝚊𝚝𝚎𝚍 𝚋𝚢 @MutyalaHarshith
𝚄𝚜𝚎 /help 𝙲𝚘𝚖𝚖𝚊𝚗𝚍𝚜 𝙵𝚘𝚛 𝙼𝚘𝚛𝚎
"""

CMDS_TEXT = """
`Here It is The List of Commamds and Its usage Created By @MutyalaHarshith.`

- /MHsong - This command to download the songs of the songs. 
- /video - This Command is For Downloading Videos. 
- Also You Can search videos via inline Mode on Bot. 

`ఇక్కడ ఆదేశాల జాబితా మరియు దాని వినియోగం ఉంది నా సృష్టికర్త @MutyalaHarshith.`

- /song - పాటల పాటలను డౌన్‌లోడ్ చేయడానికి ఈ ఆదేశం. 
- /video - ఈ కమాండ్ వీడియోలను డౌన్‌లోడ్ చేయడం కోసం. 
- అలాగే మీరు బాట్‌లో ఇన్‌లైన్ మోడ్ ద్వారా వీడియోలను శోధించవచ్చు ఎలాగంటే @MHYTDLBot. 
"""

ABOUT_TEXT = """
- **Bot :** `[MHYtDl BoT](https://t.me/MHYTdlBoT)`
- **Creator :** [Mutyala Harshith](https://t.me/MutyalaHarshith)
- **Support :** [Support Group](https://telegram.me/MHGcHaT)
- **Channel :** [Telugu RoBoTs](https://t.me/Telugu_robots)
- **Language :** [Python3](https://python.org)
- **Library :** [Pyrogram](https://pyrogram.org)
- **Server :** [Heroku](https://heroku.com)

"""
START_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('🔍 search', switch_inline_query_current_chat=""), 
        InlineKeyboardButton(text="🕵️Go Inline", switch_inline_query="")
        ],[
        InlineKeyboardButton('MH Help 💕', callback_data ='cmds'), 
        InlineKeyboardButton)'💞 Channel', url=f"https://t.me/MutyalaHarshith")
        ],[
        InlineKeyboardButton('about 😄', callback_data='about'),
        InlineKeyboardButton('Close 🤪', callback_data='close')
        ]]
    )
CMDS_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('😜 Home', callback_data='home'),
        InlineKeyboardButton('Support📕', url=f"https://telegram.me/{Config.SUPPORT}"),
        InlineKeyboardButton('🥳 Close', callback_data='close')
        ]]
    )
ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('😜 Home', callback_data='home'),
        InlineKeyboardButton('Support📕', url=f"https://telegram.me/{Config.SUPPORT}"),
        InlineKeyboardButton('🥳 Close', callback_data='close')
        ]]
    )

@Bot.on_callback_query()
async def cb_handler(bot, update):
    if update.data == "home":
        await update.message.edit_text(
            text=START_TEXT.format(update.from_user.mention),
            reply_markup=START_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "cmds":
        await update.message.edit_text(
            text=CMDS_TEXT,
            reply_markup=CMDS_BUTTONS,
            disable_web_page_preview=True
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=ABOUT_TEXT,
            reply_markup=ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    else:
        await update.message.delete()

        
@Bot.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)  

    await update.reply_text(
        text=START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
	reply_markup=START_BUTTONS
    )

@Bot.on_message(filters.private & filters.command(["about"]))
async def about(bot, update):
    await update.reply_text(
        text=ABOUT_TEXT,
        disable_web_page_preview=True,
        reply_markup=ABOUT_BUTTONS
    )
@Bot.on_message(filters.private & filters.command("status"), group=5)
async def status(bot, update):
    total_users = await db.total_users_count()
    text = "**Music Bot Status**\n"
    text += f"\n**Total Users hit start:** `{total_users}`"
    await update.reply_text(
        text=text,
        quote=True,
        disable_web_page_preview=True
    )

broadcast_ids = {}

async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"

	
@Bot.on_message(filters.command(['mhsong']))
def a(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('`Searching... Please Wait...`')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]
            views = results[0]["views"]

            ## UNCOMMENT THIS IF YOU WANT A LIMIT ON DURATION. CHANGE 1800 TO YOUR OWN PREFFERED DURATION AND EDIT THE MESSAGE (30 minutes cap) LIMIT IN SECONDS
            # if time_to_seconds(duration) >= 7000:  # duration limit
            #     m.edit("Exceeded 30mins cap")
            #     return

            performer = f"[@MutyalaHarshith]" 
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('**👎 Nothing found Retry with another @MutyalaHarshith !**')
            return
    except Exception as e:
        m.edit(
            "**Enter Song Name with /song Command! @MutyalaHarshith**"
        )
        print(str(e))
        return
    m.edit("`Bro/sis... Uploading... Please Wait... @MutyalaHarshith`")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f'🎶 <b>Title:</b> <a href="{link}">{title}</a>\n⌚ <b>Duration:</b> <code>{duration}</code>\n📻 <b>Uploaded By:</b> <a href="https://t.me/MutyalaHarshith">MutyalaHarshith</a>'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='HTML',quote=False, title=title, duration=dur, performer=performer, thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit('**An internal Error Occured, Report This @MHGcHaT!!**')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

@Bot.on_inline_query()
async def inline(client: Client, query: InlineQuery):
    answers = []
    search_query = query.query.lower().strip().rstrip()

    if search_query == "":
        await client.answer_inline_query(
            query.id,
            results=answers,
            switch_pm_text="Search your query here...🔎 @MutyalaHarshith",
            switch_pm_parameter="help",
            cache_time=0
        )
    else:
        search = VideosSearch(search_query, limit=50)

        for result in search.result()["result"]:
            answers.append(
                InlineQueryResultArticle(
                    title=result["title"],
                    description="{}, {} views.".format(
                        result["duration"],
                        result["viewCount"]["short"]
                    ),
                    input_message_content=InputTextMessageContent(
                        "https://www.youtube.com/watch?v={}".format(
                            result["id"]
                        )
                    ),
                    thumb_url=result["thumbnails"][0]["url"]
                )
            )

        try:
            await query.answer(
                results=answers,
                cache_time=0
            )
        except errors.QueryIdInvalid:
            await query.answer(
                results=answers,
                cache_time=0,
                switch_pm_text="Error: Search timed out",
                switch_pm_parameter="",
            )
        
@Bot.on_message(filters.private & filters.command("broadcast") & filters.reply)
async def broadcast_(c, m):
    print("broadcasting......")
    if m.from_user.id not in Config.OWNER_ID:
        await c.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.message_id,
            revoke=True
        )
        return
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    
    out = await m.reply_text(
        text = f"Broadcast initiated! You will be notified with log file when all the users are notified."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    
    broadcast_ids[broadcast_id] = dict(
        total = total_users,
        current = done,
        failed = failed,
        success = success
    )
    
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            
            sts, msg = await send_msg(
                user_id = int(user['id']),
                message = broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            
            if sts == 200:
                success += 1
            else:
                failed += 1
            
            if sts == 400:
                await db.delete_user(user['id'])
            
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current = done,
                        failed = failed,
                        success = success
                    )
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
    
    await asyncio.sleep(3)
    
    await out.delete()
    
    if failed == 0:
        await m.reply_text(
            text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    
    await aiofiles.os.remove('broadcast.txt') 

@Bot.on_message(filters.command(["vsong", "video"]))
async def ytmusic(client, message: Message):
    global is_downloading
    if is_downloading:
        await message.reply_text(
            "Another download is in progress, try again after sometime."
        )
        return

    urlissed = get_text(message)

    pablo = await client.send_message(
        message.chat.id, f"`Finding {urlissed} From Youtube Servers. Please Wait.\n\n Uploading Slowed down Due to Heavy Traffic @MutyalaHarshith.!`"
    )
    if not urlissed:
        await pablo.edit("Invalid Command Syntax, Please Check Help Menu To Know More!")
        return

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        is_downloading = True
        with youtube_dl.YoutubeDL(opts) as ytdl:
            infoo = ytdl.extract_info(url, False)
            duration = round(infoo["duration"] / 60)

            if duration > DURATION_LIMIT:
                await pablo.edit(
                    f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {duration} minute(s) @MutyalaHarshith"
                )
                is_downloading = False
                return
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception:
        # await pablo.edit(event, f"**Failed To Download** \n**Error :** `{str(e)}`")
        is_downloading = False
        return

    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"**Video Title ➠** `{thum}` \n**Requested Song :** `{urlissed}` \n**Source :** `{thums}` \n**Link :** `{mo}`"
    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        progress=progress,
        progress_args=(
            pablo,
            c_time,
            f"`Uploading {urlissed} Song From YouTube Music! @MutyalaHarshith`",
            file_stark,
        ),
    )
    await pablo.delete()
    is_downloading = False
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)

Bot.run()
