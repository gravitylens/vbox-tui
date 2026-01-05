# VBox TUI v0.2.0 Release Notes

## New Features

### VM Export to OVA Format
The headline feature of this release is the ability to export VMs to OVA (Open Virtualization Format) files directly from the TUI!

**Key capabilities:**
- **Press `x`** to export the selected VM
- **OVF Version Selection**: Choose between OVF 0.9, 1.0, or 2.0 formats
- **Manifest Generation**: Automatic integrity verification manifest included
- **File Browser**: Easy file selection with integrated file browser
- **Progress Tracking**: Real-time export progress with visual feedback
- **Cancellable**: Stop exports at any time with automatic cleanup
- **Enter Key Support**: Press Enter to start export from the configuration dialog
- **Auto-close**: Progress modal automatically closes after successful export

**Export workflow:**
1. Select a VM and press `x`
2. Configure output path and OVF version
3. Press Enter or click Export
4. Monitor progress with animated indicator
5. Cancel anytime or wait for completion

Exported OVA files can be imported into VirtualBox, VMware, and other virtualization platforms.

## Bug Fixes
- Fixed clean exit after export cancellation
- Improved subprocess cleanup on application exit
- Enhanced error handling and reporting during export operations

## Documentation
- Updated README with comprehensive export documentation
- Added detailed architecture section listing all screen components
- Clarified keyboard shortcuts and usage patterns

## Technical Improvements
- Implemented proper subprocess termination using threading events
- Added progress modal with full-width styling
- Enhanced worker task management for long-running operations
- Improved modal screen handling and auto-dismiss functionality

---

## Installation

Download the binary for your platform from the assets below.

**Linux:**
```bash
wget https://github.com/yourusername/vbox-tui/releases/download/v0.2.0/vbox-tui-0.2.0-linux-x86_64.tar.gz
tar -xzf vbox-tui-0.2.0-linux-x86_64.tar.gz
chmod +x vbox-tui
sudo mv vbox-tui /usr/local/bin/
```

**From source:**
```bash
git clone https://github.com/yourusername/vbox-tui.git
cd vbox-tui
git checkout v0.2.0
pip install -r requirements.txt
python -m src.vbox_tui.app
```

## Requirements
- Python 3.8+
- VirtualBox with VBoxManage CLI
- Linux, macOS, or Windows

---

**Full Changelog**: https://github.com/yourusername/vbox-tui/compare/v0.1.0...v0.2.0
