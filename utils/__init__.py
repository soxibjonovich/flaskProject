import random
import string

from .group2group import invite_followers
from .getnumber import send_code, get_hash
from .getdevices import get_devices
from .cleaner import delete_file
from .join_channel import join_channel
from .leave import leave
from .getinfo import get_info
from .paginator import paginate
from .get_code import get_code


def generate_random_password(length=5):
    """
    Generates a random password with the specified length.

    Args:
        length (int): Length of the password to generate. Default is 5.

    Returns:
        str: Randomly generated password.
    """
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password


__all__ = [
    "invite_followers",
    "send_code",
    "get_hash",
    "get_devices",
    "generate_random_password",
    "join_channel",
    "leave",
    "get_info",
    "delete_file",
    "paginate",
    "get_code"
]
