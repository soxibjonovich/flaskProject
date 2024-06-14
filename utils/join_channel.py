from typing import List
from telethon import TelegramClient, functions, errors, types
from telethon.sessions import StringSession

api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'


async def join_channel(hashes: List[str], channel_username: str) -> dict:
    count = 0

    for hash in hashes:
        client = TelegramClient(StringSession(hash), api_id, api_hash)

        await client.connect()

        if await client.is_user_authorized():
            me = await client.get_me()

            if me:
                try:
                    if channel_username.startswith("https://t.me"):
                        hash = channel_username[14:]
                        result = await client(functions.messages.ImportChatInviteRequest(
                            hash=hash
                        ))
                    else:
                        result = await client(functions.channels.JoinChannelRequest(
                            channel=channel_username
                        ))

                        print(result)
                        await client.disconnect()
                        return {
                            "success": f"Muvoffaqqiyatli bajarildi {count}"
                        }
                    count += 1
                except errors.ChannelsTooMuchError:
                    continue
                except errors.ChannelInvalidError:
                    await client.disconnect()
                    return {
                        "danger": "Invalid channel information provided."
                    }
                except errors.ChannelPrivateError:
                    await client.disconnect()
                    return {
                        "danger": "The channel you are trying to join is private."
                    }
                except errors.InviteHashInvalidError:
                    await client.disconnect()
                    return {
                        "danger": "The invite link is invalid."
                    }
                except errors.InviteHashExpiredError:
                    await client.disconnect()
                    return {
                        "danger": "The invite link has expired."
                    }
                except errors.InviteRequestSentError:
                    return {
                        "success": f"So'rov {count} ta profil tomonidan muvoffaqiyatli jo'natildi"
                    }
                except Exception as e:
                    await client.disconnect()
                    return {
                        "danger": f"An unexpected error occurred: {str(e)}"
                    }
        else:
            await client.disconnect()
            return {
                "danger": "User not authorized."
            }