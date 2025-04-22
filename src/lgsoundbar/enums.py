"""
Enumerations used by the LG Soundbar library
"""

from enum import Enum


class Equalizer(Enum):
    """
    Equalization modes available on LG soundbars.

    Values correspond to the identifiers used by the LG API.
    """

    STANDARD = 0
    BASS = 1
    FLAT = 2
    BOOST = 3
    TREBLE_BASS = 4
    USER_EQ = 5
    MUSIC = 6
    CINEMA = 7
    NIGHT = 8
    NEWS = 9
    VOICE = 10
    IA_SOUND = 11
    ASC = 12
    MOVIE = 13
    BASS_BLAST = 14
    DOLBY_ATMOS = 15
    DTS_VIRTUAL_X = 16
    BASS_BOOST_PLUS = 17
    DTS_X = 18

    @classmethod
    def get_name(cls, value: int) -> str:
        """Retrieves the name of the equalization mode from its value."""
        eq_names = {
            cls.STANDARD.value: "Standard",
            cls.BASS.value: "Bass",
            cls.FLAT.value: "Flat",
            cls.BOOST.value: "Boost",
            cls.TREBLE_BASS.value: "Treble and Bass",
            cls.USER_EQ.value: "User",
            cls.MUSIC.value: "Music",
            cls.CINEMA.value: "Cinema",
            cls.NIGHT.value: "Night",
            cls.NEWS.value: "News",
            cls.VOICE.value: "Voice",
            cls.IA_SOUND.value: "ia_sound",
            cls.ASC.value: "Adaptive Sound Control",
            cls.MOVIE.value: "Movie",
            cls.BASS_BLAST.value: "Bass Blast",
            cls.DOLBY_ATMOS.value: "Dolby Atmos",
            cls.DTS_VIRTUAL_X.value: "DTS Virtual X",
            cls.BASS_BOOST_PLUS.value: "Bass Boost Plus",
            cls.DTS_X.value: "DTS X",
        }
        return eq_names.get(value, f"Unknown Equalizer ({value})")


class Function(Enum):
    """
    Functions available on LG soundbars.

    Values correspond to the identifiers used by the LG API.
    """

    WIFI = 0
    BLUETOOTH = 1
    PORTABLE = 2
    AUX = 3
    OPTICAL = 4
    CP = 5
    HDMI = 6
    ARC = 7
    SPOTIFY = 8
    OPTICAL_2 = 9
    HDMI_2 = 10
    HDMI_3 = 11
    LG_TV = 12
    MIC = 13
    C4A = 14
    OPTICAL_HDMIARC = 15
    LG_OPTICAL = 16
    FM = 17
    USB = 18
    USB_2 = 19

    @classmethod
    def get_name(cls, value: int) -> str:
        """Retrieves the name of the function from its value."""
        function_names = {
            cls.WIFI.value: "Wifi",
            cls.BLUETOOTH.value: "Bluetooth",
            cls.PORTABLE.value: "Portable",
            cls.AUX.value: "Aux",
            cls.OPTICAL.value: "Optical",
            cls.CP.value: "CP",
            cls.HDMI.value: "HDMI",
            cls.ARC.value: "ARC",
            cls.SPOTIFY.value: "Spotify",
            cls.OPTICAL_2.value: "Optical2",
            cls.HDMI_2.value: "HDMI2",
            cls.HDMI_3.value: "HDMI3",
            cls.LG_TV.value: "LG TV",
            cls.MIC.value: "Mic",
            cls.C4A.value: "Chromecast",
            cls.OPTICAL_HDMIARC.value: "Optical/HDMI ARC",
            cls.LG_OPTICAL.value: "LG Optical",
            cls.FM.value: "FM",
            cls.USB.value: "USB",
            cls.USB_2.value: "USB2",
        }
        return function_names.get(value, f"Unknown Function ({value})")
