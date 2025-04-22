"""
Tests for the communication module of the LG Soundbar library
"""

import json
import socket
import struct
from unittest.mock import MagicMock, patch

import pytest

from lgsoundbar.communication import CommunicationError, SoundbarCommunicator


class TestSoundbarCommunicator:
    """Test the SoundbarCommunicator class"""

    @patch("socket.socket")
    def test_init_connects_to_host(self, mock_socket):
        """Test that initialization connects to the host"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance

        # Execute
        communicator = SoundbarCommunicator(host="192.168.1.1", port=1234)

        # Verify
        mock_socket.assert_called_once()
        mock_sock_instance.settimeout.assert_called_once_with(5.0)
        mock_sock_instance.connect.assert_called_once_with(("192.168.1.1", 1234))
        assert communicator.host == "192.168.1.1"
        assert communicator.port == 1234

    @patch("socket.socket")
    def test_init_connection_error(self, mock_socket):
        """Test connection error handling during initialization"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.connect.side_effect = socket.error("Connection refused")

        # Execute & Verify
        with pytest.raises(CommunicationError) as exc_info:
            SoundbarCommunicator(host="192.168.1.1")

        assert "Failed to connect" in str(exc_info.value)

    @patch("socket.socket")
    def test_close(self, mock_socket):
        """Test closing the connection"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Execute
        communicator.close()

        # Verify
        mock_sock_instance.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        mock_sock_instance.close.assert_called_once()
        assert communicator.socket is None

    @patch("socket.socket")
    def test_encrypt_decrypt_cycle(self, mock_socket):
        """Test that encryption followed by decryption returns the original data"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Source data
        test_data = {"cmd": "get", "msg": "PRODUCT_INFO"}
        json_data = json.dumps(test_data)

        # Execute
        encrypted = communicator._encrypt(json_data)
        # Extract just the encrypted part (without header)
        encrypted_payload = encrypted[5:]
        decrypted = communicator._decrypt(encrypted_payload)

        # Verify
        assert json.loads(decrypted) == test_data

    @patch("socket.socket")
    def test_encrypt_produces_valid_format(self, mock_socket):
        """Test that encrypted data has the correct format"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Source data (ensure multiple of 16 bytes with padding)
        test_data = '{"test": "value"}'

        # Execute
        encrypted = communicator._encrypt(test_data)

        # Verify
        # Check header format (0x10 followed by 4 bytes length)
        assert encrypted[0] == 0x10
        payload_length = struct.unpack(">I", encrypted[1:5])[0]
        # Check that length is accurate
        assert len(encrypted) - 5 == payload_length
        # Check payload is multiple of 16 (AES block size)
        assert payload_length % 16 == 0

    @patch("socket.socket")
    def test_decrypt_invalid_data(self, mock_socket):
        """Test decryption of invalid data"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Execute & Verify
        with pytest.raises(CommunicationError) as exc_info:
            communicator._decrypt(b"invalid_length")

        assert "Invalid encrypted data length" in str(exc_info.value)

    @patch("socket.socket")
    def test_send_message(self, mock_socket):
        """Test sending a message"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock the encrypt method to return a predictable value
        test_packet = b"\x10\x00\x00\x00\x10" + (b"\x00" * 16)
        communicator._encrypt = MagicMock(return_value=test_packet)

        # Execute
        test_message = {"cmd": "get", "msg": "PRODUCT_INFO"}
        communicator.send_message(test_message)

        # Verify
        communicator._encrypt.assert_called_once_with(json.dumps(test_message))
        mock_sock_instance.sendall.assert_called_once_with(test_packet)

    @patch("socket.socket")
    def test_send_message_error(self, mock_socket):
        """Test error handling when sending a message"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # First send fails, second succeeds
        mock_sock_instance.sendall.side_effect = [socket.error("Send failed"), None]

        # Execute
        test_message = {"cmd": "get", "msg": "PRODUCT_INFO"}
        communicator.send_message(test_message)

        # Verify
        # Should have called connect twice (initial + reconnect after error)
        assert mock_sock_instance.connect.call_count == 2
        # Should have attempted to send twice
        assert mock_sock_instance.sendall.call_count == 2

    @patch("socket.socket")
    def test_send_message_persistent_error(self, mock_socket):
        """Test handling of persistent errors when sending a message"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Both sends fail
        mock_sock_instance.sendall.side_effect = socket.error("Send failed")

        # Execute & Verify
        with pytest.raises(CommunicationError) as exc_info:
            test_message = {"cmd": "get", "msg": "PRODUCT_INFO"}
            communicator.send_message(test_message)

        assert "Failed to send message" in str(exc_info.value)
        assert mock_sock_instance.sendall.call_count == 2

    @patch("socket.socket")
    def test_receive_message_success(self, mock_socket):
        """Test successful message reception"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock successful message reception
        mock_sock_instance.recv.side_effect = [
            b"\x10",  # Message header
            b"\x00\x00\x00\x10",  # Length (16 bytes)
            b"0123456789ABCDEF",  # Encrypted payload
        ]

        # Mock decrypt method
        test_message = {"status": "OK", "data": {"value": 123}}
        communicator._decrypt = MagicMock(return_value=json.dumps(test_message))

        # Execute
        result = communicator.receive_message()

        # Verify
        assert result == test_message
        communicator._decrypt.assert_called_once_with(b"0123456789ABCDEF")

    @patch("socket.socket")
    def test_receive_message_invalid_marker(self, mock_socket):
        """Test reception with invalid message marker"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock invalid message marker
        mock_sock_instance.recv.return_value = b"\x11"  # Invalid marker (not 0x10)

        # Execute
        result = communicator.receive_message()

        # Verify
        assert result is None
        mock_sock_instance.recv.assert_called_once_with(1)

    @patch("socket.socket")
    def test_receive_message_incomplete_length(self, mock_socket):
        """Test reception with incomplete length header"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock incomplete length header
        mock_sock_instance.recv.side_effect = [
            b"\x10",  # Valid marker
            b"\x00\x00",  # Incomplete length (should be 4 bytes)
        ]

        # Execute
        result = communicator.receive_message()

        # Verify
        assert result is None
        assert mock_sock_instance.recv.call_count == 2

    @patch("socket.socket")
    def test_receive_message_incomplete_payload(self, mock_socket):
        """Test reception with incomplete payload"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock incomplete payload
        mock_sock_instance.recv.side_effect = [
            b"\x10",  # Valid marker
            b"\x00\x00\x00\x10",  # Length (16 bytes)
            b"01234567",  # Only 8 bytes (incomplete)
            b"",  # No more data
        ]

        # Execute
        result = communicator.receive_message()

        # Verify
        assert result is None
        assert mock_sock_instance.recv.call_count == 4

    @patch("socket.socket")
    def test_receive_message_json_error(self, mock_socket):
        """Test reception with invalid JSON data"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock valid message format but invalid JSON content
        mock_sock_instance.recv.side_effect = [
            b"\x10",  # Valid marker
            b"\x00\x00\x00\x10",  # Length (16 bytes)
            b"0123456789ABCDEF",  # Encrypted payload
        ]

        # Mock decrypt to return invalid JSON
        communicator._decrypt = MagicMock(return_value="{ invalid json")

        # Execute & Verify
        with pytest.raises(CommunicationError) as exc_info:
            communicator.receive_message()

        assert "Failed to decode message" in str(exc_info.value)

    @patch("socket.socket")
    def test_receive_message_connection_closed(self, mock_socket):
        """Test reception when connection is closed"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock empty response (connection closed)
        mock_sock_instance.recv.return_value = b""

        # Execute
        result = communicator.receive_message()

        # Verify connection was closed and reopened
        assert result is None
        assert mock_sock_instance.close.call_count == 1
        assert mock_sock_instance.connect.call_count == 2  # Initial + reconnect

    @patch("socket.socket")
    def test_receive_message_socket_error(self, mock_socket):
        """Test reception with socket error"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock socket error
        mock_sock_instance.recv.side_effect = socket.error("Connection reset")

        # Execute & Verify
        with pytest.raises(CommunicationError) as exc_info:
            communicator.receive_message()

        assert "Failed to receive message" in str(exc_info.value)
        # Verify reconnection was attempted
        assert mock_sock_instance.close.call_count == 1
        assert mock_sock_instance.connect.call_count == 2  # Initial + reconnect

    @patch("socket.socket")
    def test_receive_message_timeout(self, mock_socket):
        """Test reception timeout"""
        # Setup
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        communicator = SoundbarCommunicator(host="192.168.1.1")

        # Mock socket timeout
        mock_sock_instance.recv.side_effect = socket.timeout("Read timed out")

        # Execute
        result = communicator.receive_message()

        # Verify timeout was handled gracefully
        assert result is None
        # No reconnection should be attempted for timeouts
        assert mock_sock_instance.close.call_count == 0
