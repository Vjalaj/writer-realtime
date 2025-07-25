# Writer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Professional real-time text editor with live collaboration**

</div>

---

## Features

- **Real-time collaboration** - Multiple users edit simultaneously
- **Auto-save** - Changes saved automatically every 500ms
- **Live statistics** - Word count, character count, line count
- **Online users** - See how many people are connected
- **Mobile optimized** - Perfect for phones and tablets
- **Glass-morphism UI** - Modern, beautiful interface
- **Zero configuration** - Works out of the box

## Installation

```bash
git clone https://github.com/Vjalaj/writer-realtime.git
cd writer-realtime
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in your browser.

## Usage

1. Start the server on your computer
2. Open the URL on any device (phone, tablet, laptop)
3. Start writing - everything saves automatically
4. Share the URL with others for real-time collaboration

## Technical Stack

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: Vanilla JavaScript + WebSockets
- **Storage**: Local file system
- **Real-time**: WebSocket connections

## File Structure

```
writer-realtime/
├── app.py              # Flask application
├── templates/
│   └── index.html     # Web interface
├── static/
│   └── favicon.svg    # App icon
├── requirements.txt   # Dependencies
└── README.md         # This file
```

## Network Access

To access from other devices on your network:
```bash
# Find your IP address
ipconfig  # Windows
ifconfig  # Mac/Linux

# Access from other devices
http://YOUR_IP_ADDRESS:5000
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made for writers who value simplicity and collaboration**

[⭐ Star](https://github.com/Vjalaj/writer-realtime) • [🍴 Fork](https://github.com/Vjalaj/writer-realtime/fork) • [🐛 Issues](https://github.com/Vjalaj/writer-realtime/issues)

</div>