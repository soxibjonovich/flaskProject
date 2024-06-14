import random
from typing import List, Union
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession

api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'


async def get_devices(hash: str) -> Union[List[types.Authorization], str]:
    client = TelegramClient(StringSession(hash), api_id, api_hash)

    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        devices = await client(functions.account.GetAuthorizationsRequest())
        available_devices = []
        for device in devices.authorizations:
            if device.device_model != 'PC 64bit':
                available_devices.append(device)
        if not available_devices:
            available_devices.append("PC 64bit")

        return [devices.authorizations, random.choice(available_devices)]


async def get_devices_with_info(hash: str):
    client = TelegramClient(StringSession(hash), api_id, api_hash)

    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        devices = await client(functions.account.GetAuthorizationsRequest())
        available_devices = []
        for device in devices.authorizations:
            if device.device_model != 'PC 64bit':
                available_devices.append(device)
        if not available_devices:
            available_devices.append("PC 64bit")

        return [devices.authorizations, random.choice(available_devices), me]
