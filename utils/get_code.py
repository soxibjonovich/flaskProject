import datetime
from re import search
from telethon import TelegramClient, errors, types, functions, events
from telethon.sessions import StringSession


api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'


async def get_code(stringSession: str, device_model: str=None):
    async with TelegramClient(StringSession(stringSession), api_id, api_hash, device_model=device_model) as client:
        if await client.is_user_authorized():
            me = await client.get_me()

            if me:
                codes = []
                async for message in client.iter_messages(entity=777000, limit=1, offset_date=datetime.datetime.utcnow()):
                    text = message.text
                    verify_code = search(r'\d+', text)
                    if verify_code and all(term not in text for term in ['Yangi login', 'New login', 'Новый логин']):
                        codes.append(verify_code.group())

                return codes[0]
