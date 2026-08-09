import os
import json
import asyncio
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 34365075
API_HASH = "23c4c0cd9fef652b967d9f2b66cbf560"
COUNTER_FILE = "counter.json"
TEMP_PHOTO = "bot_profile_temp.jpg"
BOT_USERNAME = "SecuredMMbot"

SESSION_STRING = "AQIMXpMAQF8yfBFtUSBWI0yg0mEdDkiD4owc0cs7-ZfwDa1vbFwl2UYz_0YRs5daaV--TJ1ibXipgGEPLVSIMCeH5A5RmY6xk-NpsOsaFbChPbd_HCDRmWNws0aoehKub0TaNjib6z5o3ZK_LvWqISGQTibzDOHXcFB33nyVKIuj7Zz5HlraPLuXpHDDoFtNXTd9Sq3XIyFWKAc7KCHK5Cg9DrHdjwAaoG8lCAGEwc9lu3ZVqy4x42BqOVaXPHeMqgeo8JFxB5zBvuCKRupo73LeZWTDIJhIPw2t1wadmTEdospwTIa9jLsfuQccmFUN9Tt3-s_qNjlA3FqlF0T3-Bew5jYprwAAAAIJb2BwAA"

def get_next_deal_number():
    start_num = 1170
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                next_num = data.get("count", start_num)
            except:
                next_num = start_num
    else:
        next_num = start_num
    
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump({"count": next_num + 1}, f)
        
    return next_num

app = Client(
    name="my_alt_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.on_message(filters.text & filters.command("mm", prefixes=".") & filters.user(7913633925))
async def create_group_for_shuify(client: Client, message: Message):
    status_msg = await message.reply("...")
    
    try:
        deal_num = get_next_deal_number()
        group_title = f"Deal {deal_num} | @Secureble"

        r = await client.invoke(
            pyrogram.raw.functions.channels.CreateChannel(
                title=group_title,
                about="Experience the fastest Middleman in the community\n\nt.me/shuify — Always confirm it's me.",
                megagroup=True
            )
        )
        
        chat_id = r.chats[0].id
        full_chat_id = int(f"-100{chat_id}")
        
        await asyncio.sleep(1.5)
        await client.get_chat(full_chat_id)
        
        try:
            await client.set_chat_permissions(
                chat_id=full_chat_id,
                permissions=pyrogram.types.ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False
                )
            )
        except Exception:
            pass
        
        channel_peer = await client.resolve_peer(full_chat_id)

        session_admin_rights = pyrogram.raw.types.ChatAdminRights(
            change_info=True, post_messages=True, edit_messages=True,
            delete_messages=True, ban_users=True, invite_users=True,
            pin_messages=True, manage_call=True, add_admins=True,
            anonymous=True, manage_topics=True
        )

        bot_admin_rights = pyrogram.raw.types.ChatAdminRights(
            change_info=True, post_messages=True, edit_messages=True,
            delete_messages=True, ban_users=True, invite_users=True,
            pin_messages=True, manage_call=True, add_admins=True,
            anonymous=False, manage_topics=True
        )

        shuify_admin_rights = pyrogram.raw.types.ChatAdminRights(
            change_info=True, post_messages=True, edit_messages=True,
            delete_messages=True, ban_users=True, invite_users=True,
            pin_messages=True, manage_call=True, add_admins=True,
            anonymous=False, manage_topics=True
        )

        me = await client.get_me()
        my_peer = await client.resolve_peer(me.id)

        await client.invoke(
            pyrogram.raw.functions.channels.EditAdmin(
                channel=channel_peer,
                user_id=my_peer,
                admin_rights=session_admin_rights,
                rank="Owner"
            )
        )

        bot_user = await client.get_users(BOT_USERNAME)
        bot_peer = await client.resolve_peer(bot_user.id)
        
        await client.invoke(
            pyrogram.raw.functions.channels.InviteToChannel(
                channel=channel_peer,
                users=[bot_peer]
            )
        )

        await client.invoke(
            pyrogram.raw.functions.channels.EditAdmin(
                channel=channel_peer,
                user_id=bot_peer,
                admin_rights=bot_admin_rights,
                rank="Assistant"
            )
        )

        sender_user = message.from_user
        sender_peer = await client.resolve_peer(sender_user.id)
        
        await client.invoke(
            pyrogram.raw.functions.channels.EditAdmin(
                channel=channel_peer,
                user_id=sender_peer,
                admin_rights=shuify_admin_rights,
                rank="Middleman"
            )
        )

        photo_path = None
        async for photo in client.get_chat_photos(bot_user.id, limit=1):
            photo_path = await client.download_media(photo.file_id, file_name=TEMP_PHOTO)
            break
        
        if photo_path and os.path.exists(photo_path):
            await asyncio.sleep(2)
            uploaded_file = await client.save_file(photo_path)
            await client.invoke(
                pyrogram.raw.functions.channels.EditPhoto(
                    channel=channel_peer,
                    photo=pyrogram.raw.types.InputChatUploadedPhoto(file=uploaded_file)
                )
            )
            os.remove(photo_path)

        invite_link = await client.export_chat_invite_link(full_chat_id)
        await status_msg.edit(invite_link)

    except Exception as e:
        await status_msg.edit(f"Error: {str(e)}")


@app.on_message(filters.text & filters.command("end", prefixes=".") & filters.user(7913633925) & filters.group)
async def end_deal_group(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        chat = await client.get_chat(chat_id)
        current_title = chat.title
        
        deal_num = "N/A"
        if "Deal" in current_title:
            parts = current_title.split("|")[0].strip().split()
            if len(parts) > 1:
                deal_num = parts[1]

        new_title = f"Deal {deal_num} | Completed"

        await client.set_chat_title(chat_id=chat_id, title=new_title)

        await client.set_chat_permissions(
            chat_id=chat_id,
            permissions=pyrogram.types.ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
        )
        
        await message.reply(
            "The group is now locked. 🔒\n"
            "It will be automatically deleted within a few hours. ⏳\n\n"
            "Have a nice day. Bey 👋"
        )
        
        await asyncio.sleep(21600)
        
        await client.delete_channel(chat_id)
        
    except Exception as e:
        await message.reply(f"Error ending deal: {str(e)}")

@app.on_message(filters.text & filters.command("unlock", prefixes=".") & filters.user(7913633925) & filters.group)
async def unlock_deal_group(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await client.set_chat_permissions(
            chat_id=chat_id,
            permissions=pyrogram.types.ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        
        await message.reply("The group has been unlocked. You can send messages now.")
        
    except Exception as e:
        await message.reply(f"Error unlocking deal: {str(e)}")

app.run()