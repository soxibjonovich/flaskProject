import random
from typing import List, Union, Dict, Any
from datetime import datetime
from telethon import types, errors, TelegramClient, functions
from telethon.sessions import StringSession

api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'


async def invite_followers(
        hashes: List[str],
        from_group: str,
        to_group: str,
        date: str
):
    if not from_group or not to_group:
        return ['error', 'one of group info not filled']

    if from_group == to_group:
        return ['error', 'groups are same']

    try:
        input_date = datetime.strptime(date, '%m/%d/%Y')
        today_date = datetime.now().date()
        if input_date.date() == today_date:
            return ['error', 'date must not same with today\'s date']
    except ValueError:
        return ['error', 'incorrect date format, should be MM/DD/YYYY']

    users = []
    max_export_followers = 10_000
    max_invite = 10

    for idx, hash in enumerate(hashes):
        client = TelegramClient(StringSession(hash), api_id, api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                continue

            # Get the group entity
            from_group_entity = await client.get_entity(from_group)
            to_group_entity = await client.get_entity(to_group)

            # Calculate the segment for this hash
            offset = idx * max_invite
            limit = max_invite

            participants = await client(functions.channels.GetParticipantsRequest(
                channel=from_group_entity,
                filter=types.ChannelParticipantsRecent(),
                offset=offset,
                limit=limit,
                hash=0
            ))

            for user in participants.users:
                if len(users) >= max_export_followers:
                    break
                users.append(user)

            for user in users[idx * max_invite:(idx + 1) * max_invite]:
                try:
                    try:
                        await client(functions.channels.JoinChannelRequest(to_group_entity))
                    except errors.InviteRequestSentError:
                        continue
                    await client(functions.channels.InviteToChannelRequest(
                        channel=to_group_entity,
                        users=[user]
                    ))
                except errors.BotGroupsBlockedError:
                    continue
                except errors.ChatAdminRequiredError:
                    continue
                except errors.UserChannelsTooMuchError:
                    continue
                except errors.ChannelPrivateError:
                    return {
                        "error": "The specified channel is private and you don't have permission to access it. "
                                 "Another reason could be that you might be banned from it."
                    }
                except errors.ChatInvalidError:
                    return {
                        "error": "Belgilangan chat yaroqsiz."
                    }
                except errors.UserNotMutualContactError:
                    continue
                except errors.UserPrivacyRestrictedError:
                    continue
                except errors.UserKickedError:
                    continue
                except errors.InputUserDeactivatedError:
                    continue
                except errors.FloodWaitError as e:
                    return {
                        "error": f"Flud! {e.seconds} dan so'ng urinib ko'ring"
                    }
                except errors.UserBannedInChannelError:
                    continue
                except errors.PeerFloodError:
                    continue
                except Exception as e:
                    print(e)
                    return {
                        "error": f"Platforma bilan nosozlik"
                    }

        except errors.RPCError as e:
            return ['error', f'Error: {e}']
        except ValueError:
            return ['error', 'Username is not correct']
        finally:
            await client.disconnect()

    return ['success', users] if len(users) > 0 else ['error', 'No followers invited']
