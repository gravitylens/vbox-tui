# VirtualBox TUI

A modern Terminal User Interface (TUI) for managing VirtualBox virtual machines, built with Python and Textual.

![VirtualBox TUI](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 📊 **VM Overview**: See all your VMs at a glance with status indicators
- ▶️ **Start/Stop VMs**: Quick controls to start, stop, pause, and resume VMs
- 💾 **Save State**: Save VM state for quick resume later
- ⚙️ **Configuration**: Edit VM settings (memory, CPUs, VRAM, etc.)
- 🎨 **Modern UI**: Clean, colorful interface built with Textual
- ⌨️ **Keyboard Shortcuts**: Fast navigation and control
- 🔄 **Real-time Updates**: Automatic refresh of VM status

## Requirements

- Python 3.8 or higher
- VirtualBox installed with `VBoxManage` CLI available
- Linux, macOS, or Windows

## Installation

### Option 1: Install with pip (development mode)

```bash
cd vbox-tui
pip install -e .
```

### Option 2: Install dependencies only

```bash
cd vbox-tui
pip install -r requirements.txt
```

## Usage

### If installed with pip:

```bash
vbox-tui
```

### If running from source:

```bash
python -m vbox_tui.app
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑`/`↓` | Navigate VM list |
| `s` | Start selected VM |
| `t` | Stop selected VM (ACPI shutdown) |
| `p` | Pause/Resume selected VM |
| `v` | Save VM state |
| `h` | Toggle headless/GUI mode |
| `c` | Configure selected VM |
| `r` | Refresh VM list |
| `q` | Quit application |

## VM States

The TUI displays VMs with status icons:

- ▶ Running
- ⏸ Paused
- 💾 Saved
- ⏹ Powered Off
- ○ Other states

## Configuration Changes

To modify VM settings:

1. Select a VM from the list
2. Press `c` or click the "Config" button
3. Edit the desired settings (memory, CPUs, VRAM, boot device)
4. Click "Save" or press Enter

**Note:** VMs must be powered off to change most settings.

## Architecture

The project is structured as follows:

```
vbox-tui/
├── src/
│   └── vbox_tui/
│       ├── __init__.py       # Package initialization
│       ├── app.py            # Main Textual application
│       ├── vbox.py           # VBoxManage wrapper
│       └── config_screen.py  # Configuration screen
├── pyproject.toml            # Project metadata
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Development

### Running in development mode:

```bash
cd vbox-tui
python -m vbox_tui.app
```

### Key Components:

- **VBoxManager**: Python wrapper around VBoxManage CLI
- **VBoxTUI**: Main Textual application with VM table and controls
- **ConfigScreen**: Modal screen for editing VM configuration
- **VMInfoPanel**: Detailed information panel for selected VM

## Troubleshooting

### VBoxManage not found

Make sure VirtualBox is installed and `VBoxManage` is in your PATH:

```bash
VBoxManage --version
```

### Permission errors

On Linux, you may need to be in the `vboxusers` group:

```bash
sudo usermod -a -G vboxusers $USER
```

Then log out and back in.

### VMs not showing up

Try refreshing the VM list with `r` or check that VirtualBox can see your VMs:

```bash
VBoxManage list vms
```

## License

MIT License - feel free to use and modify as needed.

## Future Enhancements

- [ ] Create new VMs
- [ ] Clone VMs
- [ ] Delete VMs
- [ ] Snapshot management
- [ ] VM import/export
- [ ] Network configuration
- [ ] Storage management
- [ ] Log viewer
- [ ] Performance metrics

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
