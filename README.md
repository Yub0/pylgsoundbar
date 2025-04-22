# Python LG Soundbar

A Python library for controlling LG soundbars via network connection.

## Installation

```bash
# With pip
pip install python-lgsoundbar

# With Poetry
poetry add python-lgsoundbar
```

## Development

This project uses Poetry for dependency management.

```bash
# Install dependencies
poetry install

# Run linting
poetry run black .
poetry run flake8
poetry run pylint src/lgsoundbar
```

## Usage

```python
from lgsoundbar import LGSoundbarClient, Equalizer, Function

# Create a client instance
client = LGSoundbarClient("192.168.1.100")  # Replace with your soundbar's IP

# Get soundbar information
client.get_product_info()
client.get_settings()

# Control volume
client.set_volume(15)
client.set_mute(True)
client.set_mute(False)

# Change input source
client.set_function(Function.BLUETOOTH)
client.set_function(Function.HDMI)

# Change equalization mode
client.set_equalizer(Equalizer.MOVIE)
client.set_equalizer(Equalizer.MUSIC)

# Adjust sound settings
client.set_woofer_level(3)
client.set_night_mode(True)

# Close the connection when done
client.close()
```

## Features

- Control volume, mute, input source
- Change equalization modes
- Adjust speaker levels (woofer, rear, top, center)
- Toggle sound processing features (night mode, auto volume, DRC)
- Modify device settings (TV remote, auto power, auto display)
- Get device information and status

## License

MIT