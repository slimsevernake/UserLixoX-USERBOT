import os
from config import sudoers
from database import Config
from pyrogram import errors, Client, filters
from pyromod.helpers import ikb, array_chunk
from utils import info

@Client.on_callback_query(filters.sudoers & filters.regex('^setting_env'))
async def on_setting_env(client, query):
    if query.message:
        query.message.chat.cancel_listener()
    lang = query.lang
    buttons = []
    async for row in Config.all():
        btn = (f'👁‍🗨 {row.key}', f'view_env {row.key}')
        if query.message and query.message.from_user.id == info['bot'].id:
            btn = (f'📝 {row.key}', f'edit_env {row.key}')
        buttons.append(btn)
    lines = array_chunk(buttons, 2)
    lines.append([(lang.back, 'settings')])
    keyboard = ikb(lines)
    await query.edit(lang.settings_env_text, keyboard)

@Client.on_callback_query(filters.sudoers & filters.regex('^edit_env (?P<key>.+)'))
async def on_edit(client, query):
    lang = query.lang
    key = query.matches[0]['key']
    value = (await Config.get_or_none(key=key)).value
    
    text = lang.edit_env_text(
        key=key,
        value=value
    )
    keyboard = ikb([
        [(lang.back, 'setting_env')]
    ])
    last_msg = await query.edit(text, keyboard)
    
    try:
        while True:
            msg = await query.from_user.listen(filters.text & ~filters.edited, None)
            await last_msg.remove_keyboard()
            await Config.get(key=key).update(value=msg.text)
            text = lang.edit_env_text(
                key=key,
                value=msg.text
            )
            keyboard = ikb([
                [(lang.back, 'setting_env')]
            ])
            last_msg = await msg.reply_text(text, reply_markup=keyboard)
    except errors.ListenerCanceled:
        pass

@Client.on_callback_query(filters.sudoers & filters.regex('^view_env (?P<key>.+)'))
async def on_view(client, query):
    key = query.matches[0]['key']
    value = (await Config.get_or_none(key=key)).value
    await query.answer(value, show_alert=True)