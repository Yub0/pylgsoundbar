"""
Communication module for the LG Soundbar API

Handles encrypted communications with the LG soundbar device
"""

import json
import logging
import socket
import struct
from typing import Any, Dict, Optional

from Crypto.Cipher import AES


class CommunicationError(Exception):
    """Exception raised for errors in the communication with the soundbar"""


class SoundbarCommunicator:
    """
    Handles encrypted communications with an LG soundbar

    Implements the protocol used by LG soundbars, which consists of:
    - A binary header (4 bytes)
    - AES-encrypted payload containing a JSON message
    - An AES key derived from a shared secret key
    """

    # Encryption settings matching the original implementation
    DEFAULT_KEY = b"T^&*J%^7tr~4^%^&I(o%^!jIJ__+a0 k"
    DEFAULT_IV = b"'%^Ur7gy$~t+f)%@"

    def __init__(
        self,
        host: str,
        port: int = 9741,
        key: bytes = DEFAULT_KEY,
        iv: bytes = DEFAULT_IV,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize a communicator for an LG soundbar

        Args:
            host: IP address of the soundbar
            port: TCP port of the soundbar (default 9741)
            key: Encryption key (default is the common LG key)
            iv: Initialization vector for CBC mode
            logger: Logger for debug messages
        """
        self.host = host
        self.port = port
        self.key = key
        self.iv = iv
        self.logger = logger or logging.getLogger(__name__)
        self.socket = None
        self._connect()

    def _connect(self) -> None:
        """Establish a TCP connection with the soundbar"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.logger.debug("Connected to %s:%d", self.host, self.port)
        except socket.error as exc:
            self.logger.error(
                "Failed to connect to %s:%d: %s", self.host, self.port, str(exc)
            )
            raise CommunicationError(f"Failed to connect: {exc}") from exc

    def close(self) -> None:
        """Close the TCP connection"""
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            self.socket.close()
            self.socket = None
            self.logger.debug("Disconnected from %s:%d", self.host, self.port)

    def _encrypt(self, data: str) -> bytes:
        """
        Encrypt data using AES in CBC mode with PKCS7 padding

        Args:
            data: JSON string to encrypt

        Returns:
            Encrypted data with header
        """
        # Add PKCS7 padding
        pad_len = 16 - (len(data) % 16)
        padded_data = data
        for _ in range(pad_len):
            padded_data += chr(pad_len)

        # Encode to bytes
        data_bytes = padded_data.encode("utf-8")

        # Encrypt using AES-CBC
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted_data = cipher.encrypt(data_bytes)

        # Create header with length
        length = len(encrypted_data)
        prelude = bytearray([0x10, 0x00, 0x00, 0x00, length])

        return prelude + encrypted_data

    def _decrypt(self, data: bytes) -> str:
        """
        Decrypt data using AES in CBC mode

        Args:
            data: Encrypted data

        Returns:
            Decrypted data as string
        """
        if not data or len(data) % 16 != 0:
            raise CommunicationError(f"Invalid encrypted data length: {len(data)}")

        # Decrypt using AES-CBC
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_data = cipher.decrypt(data)

        # Remove PKCS7 padding
        padding = decrypted_data[-1:]
        decrypted_data = decrypted_data[: -ord(padding)]

        return str(decrypted_data, "utf-8")

    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message to the soundbar

        Args:
            message: Dictionary to send as JSON
        """
        if not self.socket:
            self._connect()

        # Convert message to JSON
        json_data = json.dumps(message)
        self.logger.debug("Sending message: %s", message)

        # Encrypt the JSON data and get the packet
        packet = self._encrypt(json_data)

        try:
            # Send the full packet
            self.socket.sendall(packet)
        except socket.error as exc:
            self.logger.error("Error sending message: %s", exc)
            self.close()
            self._connect()
            try:
                self.socket.sendall(packet)
            except socket.error as exc:
                self.logger.error("Failed second attempt: %s", exc)
                raise CommunicationError(f"Failed to send message: {exc}") from exc

    def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        Receive a message from the soundbar

        Returns:
            Decoded JSON message or None if no complete message was received
        """
        if not self.socket:
            self._connect()

        try:
            # First read 1 byte to check message type
            first_byte = self.socket.recv(1)
            if not first_byte:
                self.logger.debug("Connection closed")
                self.close()
                self._connect()
                return None

            # Check for valid message marker
            if first_byte[0] != 0x10:
                self.logger.debug(
                    "Received invalid message marker: %s", first_byte.hex()
                )
                return None

            # Read 4 byte length header
            length_bytes = self.socket.recv(4)
            if len(length_bytes) < 4:
                self.logger.debug("Received incomplete length header")
                return None

            # Parse big-endian length value
            length = struct.unpack(">I", length_bytes)[0]

            # Read the encrypted payload
            encrypted_data = b""
            while len(encrypted_data) < length:
                chunk = self.socket.recv(length - len(encrypted_data))
                if not chunk:
                    break
                encrypted_data += chunk

            # Validate payload
            if len(encrypted_data) != length:
                self.logger.warning(
                    "Received incomplete payload: %d bytes instead of %d",
                    len(encrypted_data),
                    length,
                )
                return None

            # Check for valid AES block size
            if len(encrypted_data) % 16 != 0:
                self.logger.warning(
                    "Invalid encrypted data length (not a multiple of 16)"
                )
                return None

            # Decrypt the payload and parse the JSON data
            response = self._decrypt(encrypted_data)
            message = json.loads(response)
            self.logger.debug("Received message: %s", str(message))
            return message

        except socket.timeout:
            # Timeout is normal in asynchronous reception
            return None
        except socket.error as socket_exc:
            self.logger.error("Error receiving message: %s", str(socket_exc))
            self.close()
            self._connect()
            raise CommunicationError(
                f"Failed to receive message: {socket_exc}"
            ) from socket_exc
        except (json.JSONDecodeError, UnicodeDecodeError) as decode_exc:
            self.logger.error("Error decoding message: %s", str(decode_exc))
            raise CommunicationError(
                f"Failed to decode message: {decode_exc}"
            ) from decode_exc
