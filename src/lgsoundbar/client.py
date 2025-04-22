"""
Main client for the LG Soundbar API

Provides a user-friendly interface for controlling LG soundbars
"""

import logging
from threading import Thread
from typing import Any, Callable, Dict, Optional, Union

from lgsoundbar.communication import CommunicationError, SoundbarCommunicator
from lgsoundbar.enums import Equalizer, Function
from lgsoundbar.models import MessageTarget, MessageType, SoundbarMessage


# Type for callback functions receiving messages from the soundbar
CallbackType = Callable[[Dict[str, Any]], None]


class LGSoundbarClient:
    """
    Client for controlling an LG soundbar via its network API

    This class provides simple methods to control all soundbar functions,
    using encrypted communication over TCP.
    """

    def __init__(
        self,
        host: str,
        port: int = 9741,
        callback: Optional[CallbackType] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize a client to control an LG soundbar

        Args:
            host: IP address of the soundbar
            port: TCP port of the soundbar (default 9741)
            callback: Function called when asynchronous messages are received
            logger: Logger for debug messages
        """
        self.logger = logger or logging.getLogger(__name__)
        self.callback = callback
        self._listening = False

        # Initialize communicator
        self._communicator = SoundbarCommunicator(host, port)

        # Start listener thread if a callback is provided
        if callback:
            self._listening = True
            self._listener_thread = Thread(target=self._listener, daemon=True)
            self._listener_thread.start()

    def _listener(self) -> None:
        """Listener thread for asynchronous messages from the soundbar"""
        while self._listening:
            try:
                message = self._communicator.receive_message()
                if message and self.callback:
                    self.callback(message)
            except CommunicationError as exc:
                self.logger.warning(f"Error in listener loop: {exc}")

    def close(self) -> None:
        """Close the connection with the soundbar"""
        self._listening = False
        self._communicator.close()

    def _send_message(self, message: SoundbarMessage) -> None:
        """
        Send a formatted message to the soundbar

        Args:
            message: Message to send
        """
        self._communicator.send_message(message.to_dict())

    def _get_info(self, target: MessageTarget) -> None:
        """
        Send an information request to the soundbar

        Args:
            target: Type of information requested
        """
        message = SoundbarMessage(cmd=MessageType.GET, msg=target)
        self._send_message(message)

    def _set_setting(self, setting_name: str, value: Any) -> None:
        """
        Modify a soundbar setting

        Args:
            setting_name: Name of the setting to modify
            value: New value for the setting
        """
        message = SoundbarMessage(
            cmd=MessageType.SET,
            msg=MessageTarget.SETTING_VIEW_INFO,
            data={setting_name: value},
        )
        self._send_message(message)

    # Methods for getting information

    def get_equalizer_info(self) -> None:
        """Request equalizer information"""
        self._get_info(MessageTarget.EQ_VIEW_INFO)

    def get_speaker_info(self) -> None:
        """Request speaker information"""
        self._get_info(MessageTarget.SPK_LIST_VIEW_INFO)

    def get_playback_info(self) -> None:
        """Request current playback information"""
        self._get_info(MessageTarget.PLAY_INFO)

    def get_function_info(self) -> None:
        """Request information about the current function/input"""
        self._get_info(MessageTarget.FUNC_VIEW_INFO)

    def get_settings(self) -> None:
        """Request settings information"""
        self._get_info(MessageTarget.SETTING_VIEW_INFO)

    def get_product_info(self) -> None:
        """Request product information"""
        self._get_info(MessageTarget.PRODUCT_INFO)

    def get_chromecast_info(self) -> None:
        """Request Chromecast information"""
        self._get_info(MessageTarget.C4A_SETTING_INFO)

    def get_radio_info(self) -> None:
        """Request radio information"""
        self._get_info(MessageTarget.RADIO_VIEW_INFO)

    def get_access_point_info(self) -> None:
        """Request access point information"""
        self._get_info(MessageTarget.SHARE_AP_INFO)

    def get_update_info(self) -> None:
        """Request update information"""
        self._get_info(MessageTarget.UPDATE_VIEW_INFO)

    def get_build_info(self) -> None:
        """Request software build information"""
        self._get_info(MessageTarget.BUILD_INFO_DEV)

    def get_option_info(self) -> None:
        """Request option information"""
        self._get_info(MessageTarget.OPTION_INFO_DEV)

    def get_mac_info(self) -> None:
        """Request MAC address information"""
        self._get_info(MessageTarget.MAC_INFO_DEV)

    def get_memory_monitor_info(self) -> None:
        """Request memory usage information"""
        self._get_info(MessageTarget.MEM_MON_DEV)

    def get_test_info(self) -> None:
        """Request test information"""
        self._get_info(MessageTarget.TEST_DEV)

    # Methods for modifying settings

    def set_equalizer(self, equalizer: Union[Equalizer, int]) -> None:
        """
        Set the equalization mode

        Args:
            equalizer: Equalization mode to activate (enum or integer value)
        """
        eq_value = equalizer.value if isinstance(equalizer, Equalizer) else equalizer
        message = SoundbarMessage(
            cmd=MessageType.SET,
            msg=MessageTarget.EQ_VIEW_INFO,
            data={"i_curr_eq": eq_value},
        )
        self._send_message(message)

    def set_function(self, function: Union[Function, int]) -> None:
        """
        Set the input source

        Args:
            function: Input source to activate (enum or integer value)
        """
        func_value = function.value if isinstance(function, Function) else function
        message = SoundbarMessage(
            cmd=MessageType.SET,
            msg=MessageTarget.FUNC_VIEW_INFO,
            data={"i_curr_func": func_value},
        )
        self._send_message(message)

    def set_volume(self, level: int) -> None:
        """
        Set the volume level

        Args:
            level: Volume level to set
        """
        message = SoundbarMessage(
            cmd=MessageType.SET,
            msg=MessageTarget.SPK_LIST_VIEW_INFO,
            data={"i_vol": level},
        )
        self._send_message(message)

    def set_mute(self, muted: bool) -> None:
        """
        Enable or disable mute mode

        Args:
            muted: True to enable mute, False to disable
        """
        message = SoundbarMessage(
            cmd=MessageType.SET,
            msg=MessageTarget.SPK_LIST_VIEW_INFO,
            data={"b_mute": muted},
        )
        self._send_message(message)

    def set_name(self, name: str) -> None:
        """
        Set the soundbar name

        Args:
            name: New name for the soundbar
        """
        message = SoundbarMessage(
            cmd=MessageType.SET,
            msg=MessageTarget.SETTING_VIEW_INFO,
            data={"s_user_name": name},
        )
        self._send_message(message)

    # Methods for audio settings

    def set_night_mode(self, enabled: bool) -> None:
        """
        Enable or disable night mode

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_night_mode", enabled)

    def set_auto_volume(self, enabled: bool) -> None:
        """
        Enable or disable automatic volume

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_auto_vol", enabled)

    def set_dynamic_range_control(self, enabled: bool) -> None:
        """
        Enable or disable Dynamic Range Control (DRC)

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_drc", enabled)

    def set_neuralx(self, enabled: bool) -> None:
        """
        Enable or disable NeuralX mode

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_neuralx", enabled)

    def set_av_sync(self, value: int) -> None:
        """
        Set audio/video synchronization

        Args:
            value: Synchronization value
        """
        self._set_setting("i_av_sync", value)

    def set_woofer_level(self, level: int) -> None:
        """
        Set the subwoofer level

        Args:
            level: Subwoofer level
        """
        self._set_setting("i_woofer_level", level)

    def set_rear_speakers_enabled(self, enabled: bool) -> None:
        """
        Enable or disable rear speakers

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_rear", enabled)

    def set_rear_speakers_level(self, level: int) -> None:
        """
        Set the rear speakers level

        Args:
            level: Rear speakers level
        """
        self._set_setting("i_rear_level", level)

    def set_top_speakers_level(self, level: int) -> None:
        """
        Set the top speakers level

        Args:
            level: Top speakers level
        """
        self._set_setting("i_top_level", level)

    def set_center_speaker_level(self, level: int) -> None:
        """
        Set the center speaker level

        Args:
            level: Center speaker level
        """
        self._set_setting("i_center_level", level)

    # Methods for other settings

    def set_tv_remote_control(self, enabled: bool) -> None:
        """
        Enable or disable TV remote control

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_tv_remote", enabled)

    def set_auto_power(self, enabled: bool) -> None:
        """
        Enable or disable automatic power on

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_auto_power", enabled)

    def set_auto_display(self, enabled: bool) -> None:
        """
        Enable or disable automatic display

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_auto_display", enabled)

    def set_bluetooth_standby(self, enabled: bool) -> None:
        """
        Enable or disable Bluetooth standby

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_bt_standby", enabled)

    def set_bluetooth_restriction(self, enabled: bool) -> None:
        """
        Enable or disable Bluetooth connection restriction

        Args:
            enabled: True to enable, False to disable
        """
        self._set_setting("b_conn_bt_limit", enabled)

    def set_sleep_timer(self, minutes: int) -> None:
        """
        Set the sleep timer

        Args:
            minutes: Time in minutes before sleep (0 to disable)
        """
        self._set_setting("i_sleep_time", minutes)

    # Methods for special actions

    def run_test_tone(self) -> None:
        """Launch the test tone"""
        message = SoundbarMessage(cmd=MessageType.SET, msg=MessageTarget.TEST_TONE_REQ)
        self._send_message(message)

    def factory_reset(self) -> None:
        """Reset the soundbar to factory settings"""
        message = SoundbarMessage(
            cmd=MessageType.SET, msg=MessageTarget.FACTORY_SET_REQ
        )
        self._send_message(message)
