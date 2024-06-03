import random
from typing import List, Union
from datetime import datetime
from telethon import types, errors, TelegramClient, functions
from telethon.sessions import StringSession


async def extractFollowers(
        hashes: List[str],
        from_group: str,
        to_group: str,
        date: str
) -> Union[List[str], Union[str, List[types.User], TelegramClient]]:
    api_id = 6539950
    api_hash = '111b6f6f44ba09b5858f9fee99a97322'

    if from_group == '' or to_group == '':
        return ['error', 'one of group info not filled']

    if from_group == to_group:
        return ['error', 'groups are same']

    try:
        input_date = datetime.strptime(date, '%m/%d/%Y')
        today_date = datetime.now().date()
        if input_date.date() == today_date:
            return ['error', 'date must same with today\'s date']
    except ValueError:
        return ['error', 'incorrect date format, should be MM/DD/YYYY']

    if len(hashes):
        return ['error', 'Error while extracting followers']

    count = 0
    hash_index = 1
    users = []
    max_export = 10
    followers_count = 0
    max_export_folowers = 10_000
    for hash in hashes:
        client = TelegramClient(StringSession(hash), api_id, api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                continue

            from_g_entity = await client.get_entity(from_group)
            from_g_entity_full = await client(
                functions.channels.GetFullChannelRequest(
                    channel=types.InputChannel(
                        channel_id=from_g_entity.id,
                        access_hash=from_g_entity.access_hash
                    )
                ))
            followers_count = from_g_entity_full.full_chat.participants_count
            participants = await client(
                functions.channels.GetParticipantsRequest(
                    channel=types.InputChannel(from_g_entity.id, from_g_entity.access_hash),
                    filter=types.ChannelParticipantsRecent(),
                    offset=count,
                    limit=max_export,
                    hash=0
                ))
            users.extend(participants.users)
            count += len(participants.users)

            hash_index += 1
        except errors.RPCError as e:
            return ['error', f'RPCError: {e}']
        finally:
            await client.disconnect()

async def inviteFollowers(
        users: List[types.User],
        client: TelegramClient,
        to_group: str
):
    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        from_g_entity = await client.get_entity(to_group)

        await client(functions.channels.JoinChannelRequest(
            types.InputChannel(
                from_g_entity.id, from_g_entity.access_hash
            )
        ))

        for user in users:
            try:
                await client(functions.channels.InviteToChannelRequest(
                    channel=types.InputChannel(from_g_entity.id, from_g_entity.access_hash),
                    users=[types.InputUser(user.id, user.access_hash)]
                ))
            except errors.BotGroupsBlockedError:
                continue
            except errors.ChatAdminRequiredError:
                continue
            except errors.UserChannelsTooMuchError:
                continue
