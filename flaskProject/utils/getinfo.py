import random

from telethon.sessions import StringSession
from telethon import types, errors, functions, TelegramClient

api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'


async def get_info(hash: str, device_model: str = None, random_device: bool = False):
    client = TelegramClient(StringSession(hash), api_id=api_id, api_hash=api_hash, device_model=device_model)

    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()

        devices = await client(functions.account.GetAuthorizationsRequest())
        await client.disconnect()

        if random_device:
            available_devices = []
            for device in devices.authorizations:
                if device.device_model != "PC 64bit":
                    available_devices.append(device.device_model)

            return [me, random.choice(available_devices)]
        return [me, devices.authorizations]
