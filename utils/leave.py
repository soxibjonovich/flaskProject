from telethon import TelegramClient, errors, types, functions
from telethon.sessions import StringSession
import logging

api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'


async def leave(hash: str, link: str):
    client = TelegramClient(StringSession(hash), api_id, api_hash)

    await client.connect()

    try:
        if await client.is_user_authorized():
            me = await client.get_me()

            if me:
                entity = await client.get_entity(link)
                await client(functions.channels.LeaveChannelRequest(
                    channel=types.InputChannel(entity.id, entity.access_hash)
                ))
    except errors.ChannelInvalidError:
        logging.error("Invalid channel object.")
    except errors.ChannelPrivateError:
        logging.error("The channel specified is private and you lack permission to access it.")
    except errors.ChannelPublicGroupNaError:
        logging.error("Channel/supergroup not available.")
    except errors.UserCreatorError:
        logging.error("You can't leave this channel, because you're its creator.")
        return {"danger": "Siz bu kanaldan chiqolmaysiz, chunki siz uning yaratuvchisiz."}
    except errors.UserNotParticipantError:
        logging.error("The target user is not a member of the specified megagroup or channel.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
    finally:
        await client.disconnect()
