# VirtualBox TUI

A modern Terminal User Interface (TUI) for managing VirtualBox virtual machines, built with Python and Textual.

![VirtualBox TUI](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

![main screen](images/vbox-tui.png)

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
| `e` | Settings (configure default VM folder) |
| `s` | Start selected VM (headless) |
| `t` | Stop selected VM (ACPI shutdown) |
| `f` | Force poweroff selected VM |
| `p` | Pause/Resume selected VM |
| `v` | Save VM state |
| `g` | Show/reconnect to VM GUI window |
| `h` | SSH to VM (requires Guest Additions and guest IP) |
| `c` | Configure selected VM |
| `m` | Manage snapshots |
| `k` | Manage disks |
| `x` | Export VM to OVA |
| `d` | Delete selected VM |
| `q` | Quit application |

The VM list automatically refreshes every 10 seconds to show current status.

VMs are always started in headless mode. Use `g` to open the GUI console window.

## Snapshot Management

![image](images/snapshots.png)

Press `m` to manage snapshots for the selected VM. In the snapshot screen you can:

- **Take Snapshot (t)**: Create a new snapshot with name and description
- **Restore (r)**: Restore the VM to a selected snapshot (VM must be powered off)
- **Delete (d)**: Delete a snapshot
- **Current Snapshot**: Indicated with a ● marker

Snapshots allow you to save the current state of a VM and restore to it later. They're useful for:
- Before making system changes
- Creating restore points
- Testing configurations safely

## Disk Management

![image](images/disks.png)

Press `k` to manage disks for the selected VM. In the disk screen you can:

- **New Disk (n)**: Create a new virtual disk and attach it
  - Specify name, size (in MB), and format (VDI/VMDK/VHD)
  - Disk is created in the VM's folder
  - Automatically attached to the next available SATA port
- **Attach (a)**: Attach an existing disk file
  - Browse for disk file (.vdi, .vmdk, .vhd, etc.)
  - Select controller, port, and device number
- **Detach (d)**: Detach a disk from the VM
  - Disk file is not deleted, only detached

**Note**: VM should be powered off before attaching/detaching disks.

## VM Export

![image](images/export.png)

Press `x` to export the selected VM to OVA (Open Virtualization Format Archive) format. The export process:

1. **Configure Export**: Specify output location, OVF version, and options
   - **Output Location**: Path for the .ova file (use Browse button or press Tab to navigate)
   - **Enter Key**: Press Enter to start the export (same as clicking Export button)
   - **OVF Version**: Choose the format version:
     - **OVF 0.9**: Legacy format for older virtualization software
     - **OVF 1.0**: Widely compatible format
     - **OVF 2.0**: Recommended modern format with best feature support
   - **Manifest**: Automatically includes a manifest file for integrity verification

2. **Export Progress**: A progress modal displays during export
   - Shows export status with animated progress indicator
   - **Cancel Button**: Stop the export at any time (will clean up partial files)
   - **Auto-close**: Modal automatically closes 2 seconds after successful completion
   - Export time varies based on VM disk size

The exported OVA file can be imported into VirtualBox or other virtualization platforms like VMware, supporting VM portability and backup.

**Important Notes:**
- VMs must be powered off before exporting
- You can cancel exports at any time using the Cancel button
- Partial export files are automatically cleaned up if cancelled
- The application can be quit safely during export (will cancel the export automatically)

## Settings

Press `e` to access the settings screen where you can configure:

- **Default VM Folder**: Where new VMs will be created (changes VirtualBox's global setting)

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
│       ├── __init__.py                  # Package initialization
│       ├── app.py                       # Main Textual application
│       ├── vbox.py                      # VBoxManage wrapper
│       ├── config_screen.py             # VM configuration screen
│       ├── create_vm_screen.py          # New VM creation dialog
│       ├── settings_screen.py           # Application settings
│       ├── snapshot_screen.py           # Snapshot management
│       ├── disk_screen.py               # Disk management
│       ├── export_screen.py             # VM export configuration
│       ├── export_progress_screen.py    # Export progress modal
│       ├── file_browser.py              # File/folder browser
│       ├── delete_confirm_screen.py     # VM deletion confirmation
│       └── force_poweroff_screen.py     # Force poweroff confirmation
├── pyproject.toml                       # Project metadata
├── requirements.txt                     # Python dependencies
├── build-binary.sh                      # Binary build script
└── README.md                            # This file
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
- **CreateVMScreen**: Wizard for creating new VMs
- **SnapshotScreen**: Snapshot management interface
- **DiskScreen**: Disk attachment and management
- **ExportScreen**: VM export configuration dialog
- **ExportProgressScreen**: Progress modal for export operations
- **SettingsScreen**: Application settings editor
- **FileBrowser**: Generic file/folder selection dialog

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
- Additional network configuration options
- Advanced storage management
- Log viewer
- Performance metrics
- VM grouping and organization

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
