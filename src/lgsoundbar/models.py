"""
Data models for the LG Soundbar API
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class MessageType(Enum):
    """Type of message exchanged with the LG soundbar"""

    GET = "get"
    SET = "set"


class MessageTarget(Enum):
    """Target endpoints for messages sent to the LG soundbar"""

    EQ_VIEW_INFO = "EQ_VIEW_INFO"
    SPK_LIST_VIEW_INFO = "SPK_LIST_VIEW_INFO"
    PLAY_INFO = "PLAY_INFO"
    FUNC_VIEW_INFO = "FUNC_VIEW_INFO"
    SETTING_VIEW_INFO = "SETTING_VIEW_INFO"
    PRODUCT_INFO = "PRODUCT_INFO"
    C4A_SETTING_INFO = "C4A_SETTING_INFO"
    RADIO_VIEW_INFO = "RADIO_VIEW_INFO"
    SHARE_AP_INFO = "SHARE_AP_INFO"
    UPDATE_VIEW_INFO = "UPDATE_VIEW_INFO"
    BUILD_INFO_DEV = "BUILD_INFO_DEV"
    OPTION_INFO_DEV = "OPTION_INFO_DEV"
    MAC_INFO_DEV = "MAC_INFO_DEV"
    MEM_MON_DEV = "MEM_MON_DEV"
    TEST_DEV = "TEST_DEV"
    TEST_TONE_REQ = "TEST_TONE_REQ"
    FACTORY_SET_REQ = "FACTORY_SET_REQ"


@dataclass
class SoundbarMessage:
    """
    Message to be sent to the LG soundbar

    Represents the structure of JSON messages sent to the device.
    """

    cmd: MessageType
    msg: MessageTarget
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the message to a dictionary for JSON serialization"""
        result = {
            "cmd": self.cmd.value,
            "msg": self.msg.value,
        }

        if self.data:
            result["data"] = self.data

        return result
