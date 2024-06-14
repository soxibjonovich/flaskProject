from typing import Union, Dict, Tuple
from telethon import TelegramClient, functions, types, errors
from telethon.sessions import StringSession
import logging

api_id = 6539950
api_hash = '111b6f6f44ba09b5858f9fee99a97322'


async def send_code(username: str, number: str) -> Union[Dict[str, Union[str, TelegramClient]], Tuple[str, str]]:
    """sumary_line
    Send code to the number
    Keyword arguments:
    argument -- description
    Return: 
        Error:
            Dict[str, str]
        Success:
            Dict[str, Union[str, TelegramClient]]
            str -> session_hash
            str -> phone_code_hash
            TelegramClient -> client
    """

    client = TelegramClient(f"sessions/{username}", api_id, api_hash)

    await client.connect()
    try:
        # response = await client(functions.auth.SendCodeRequest(
        #     phone_number=number,
        #     api_id=api_id,
        #     api_hash=api_hash,
        #     settings=types.CodeSettings(
        #         current_number=False,
        #         allow_app_hash=True,
        #         allow_missed_call=False,
        #         allow_firebase=False,
        #         unknown_number=True,
        #         token='login_token',
        #         app_sandbox=False
        #     )
        # ))
        response = await client.send_code_request(phone=number)
        print(response)
        return {
            # "session_hash": session_hash,
            "phone_code_hash": response.phone_code_hash,
            "client": client
        }
    except errors.AuthRestartError:
        logging.error("Error: Attempting to re-add number")
        return {"error": "Raqamni qaytadan qoshishga harakat qilaman"}
    except errors.PhoneNumberBannedError:
        logging.error("Error: Number is banned")
        return {"error": "Raqam ban olgan"}
    except errors.PhoneNumberInvalidError:
        logging.error("Error: Invalid phone number")
        return {"error": "Raqam xato kiritilgan"}
    finally:
        await client.disconnect()


async def get_hash(dataname: str, phone: str, phone_code_hash: str, code: str, edit_password: bool = False, new_password="",
                   password: str = "") -> Union[str, Dict[str, str]]:
    client = TelegramClient(f"sessions/{dataname}", api_id, api_hash)
    await client.connect()

    try:
        code = code.replace("-", "")
        result = await client.sign_in(
            phone=phone,
            code=int(code),
            phone_code_hash=phone_code_hash
        )

        print(result)
    except errors.PhoneCodeEmptyError:
        logging.error("Error: Phone code is empty")
        return {"error": "Kod xato kiritilgan"}
    except errors.PhoneCodeExpiredError:
        logging.error("Error: Phone code is expired")
        return {"error": "Kod eskirdi"}
    except errors.PhoneCodeInvalidError:
        logging.error("Error: Phone code is invalid")
        return {"error": "Kod xato kiritilgan"}
    except errors.SessionPasswordNeededError:
        await client.sign_in(
            password=password
        )
        if edit_password:
            await client.edit_2fa(current_password=password, new_password=new_password, hint="2 bosqichli parol")

    result = StringSession.save(client.session)
    await client.disconnect()
    return result
