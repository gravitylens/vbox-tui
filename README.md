# VirtualBox TUI

A modern Terminal User Interface (TUI) for managing VirtualBox virtual machines, built with Python and Textual.

![VirtualBox TUI](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **VM Overview**: See all your VMs at a glance with status indicators
- **Start/Stop VMs**: Quick controls to start, stop, pause, and resume VMs
- **Save State**: Save VM state for quick resume later
- **Configuration**: Edit VM settings (memory, CPUs, VRAM, etc.)
- **Modern UI**: Clean, colorful interface built with Textual
- **Keyboard Shortcuts**: Fast navigation and control
- **Real-time Updates**: Automatic refresh of VM status

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

### Option 3: Use pre-built binary

Download the latest binary from the [Releases](https://github.com/gravitylens/vbox-tui/releases) page and make it executable:

```bash
chmod +x vbox-tui
sudo mv vbox-tui /usr/local/bin/
```

## Building from Source

### Standard Installation

```bash
git clone https://github.com/gravitylens/vbox-tui.git
cd vbox-tui
pip install -r requirements.txt
python -m src.vbox_tui.app
```

### Building Binary Distribution

To create a standalone binary:

```bash
pip install pyinstaller
./build-binary.sh
```

The binary will be created in `dist/vbox-tui` and can be distributed without Python dependencies.


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
| `n` | Create new VM |
| `s` | Start selected VM (headless) |
| `t` | Stop selected VM (ACPI shutdown) |
| `f` | Force poweroff selected VM |
| `p` | Pause/Resume selected VM |
| `v` | Save VM state |
| `g` | Show/reconnect to VM GUI window |
| `c` | Configure selected VM |
| `d` | Delete selected VM |
| `q` | Quit application |

The VM list automatically refreshes every 10 seconds to show current status.

VMs are always started in headless mode. Use `g` to open the GUI console window.

## VM States

The TUI displays VMs with status icons:

- Running
- Paused
- Saved
- Powered Off
- Other states

## Configuration Changes

To modify VM settings:

1. Select a VM from the list
2. Press `c` to open the configuration screen
3. Edit the desired settings (memory, CPUs, VRAM, boot device, ISO attachment, network)
4. Click "Save" or press Enter

**Note:** VMs must be powered off to change most settings.

## Reconnecting to VM GUI

If you've lost connection to a running VM's GUI window (e.g., the window was closed but the VM is still running), you can reconnect by:

1. Select the VM from the list
2. Press `g` to show/reconnect to the GUI window

This works for VMs in running or paused states and will open a new window showing the VM's display.

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

The VM list automatically refreshes every 10 seconds. If VMs still aren't showing up, check that VirtualBox can see your VMs:

```bash
VBoxManage list vms
```

## License

MIT License - feel free to use and modify as needed.

## Future Enhancements

- Clone VMs
- Snapshot management
- VM import/export
- Network configuration
- Storage management
- Log viewer
- Performance metrics

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
