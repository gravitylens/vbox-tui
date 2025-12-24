"""Screen for creating new VMs."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, Input, Static, Select
from textual.binding import Binding
from textual import work
import asyncio

from .vbox import VBoxManager
from .file_browser import FileBrowser


class CreateVMScreen(Screen):
    """Screen for creating a new VM."""
    
    CSS = """
    CreateVMScreen {
        align: center middle;
    }
    
    #create-container {
        width: 90%;
        max-width: 100;
        height: 90%;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
        overflow-y: auto;
    }
    
    .create-row {
        height: auto;
        margin: 1 0;
    }
    
    .section-header {
        margin-top: 1;
        margin-bottom: 1;
    }
    
    .create-label {
        width: 25;
        padding: 0 1;
    }
    
    Input {
        width: 1fr;
    }
    
    Select {
        width: 1fr;
    }
    
    #iso-row {
        height: auto;
        margin: 1 0;
    }
    
    #iso-row Input {
        width: 1fr;
    }
    
    #iso-row Button {
        width: 12;
        min-width: 12;
        margin-left: 1;
    }
    
    #button-row {
        margin-top: 2;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    # Common OS types in VirtualBox
    OS_TYPES = [
        ("Ubuntu (64-bit)", "Ubuntu_64"),
        ("Ubuntu (32-bit)", "Ubuntu_32"),
        ("Debian (64-bit)", "Debian_64"),
        ("Debian (32-bit)", "Debian_32"),
        ("Fedora (64-bit)", "Fedora_64"),
        ("Red Hat (64-bit)", "RedHat_64"),
        ("Windows 11 (64-bit)", "Windows11_64"),
        ("Windows 10 (64-bit)", "Windows10_64"),
        ("Windows 10 (32-bit)", "Windows10"),
        ("Windows 8.1 (64-bit)", "Windows81_64"),
        ("Windows 7 (64-bit)", "Windows7_64"),
        ("macOS (64-bit)", "MacOS_64"),
        ("Arch Linux (64-bit)", "ArchLinux_64"),
        ("Other Linux (64-bit)", "Linux_64"),
        ("Other Linux (32-bit)", "Linux"),
    ]
    
    # Network adapter types
    NETWORK_TYPES = [
        ("NAT", "nat"),
        ("Bridged Adapter", "bridged"),
        ("Internal Network", "intnet"),
        ("Host-only Adapter", "hostonly"),
        ("Not attached", "none"),
    ]
    
    # Graphics controllers
    GRAPHICS_CONTROLLERS = [
        ("VBoxVGA", "VBoxVGA"),
        ("VMSVGA", "VMSVGA"),
        ("VBoxSVGA", "VBoxSVGA"),
        ("None", "None"),
    ]
    
    # Chipset types
    CHIPSET_TYPES = [
        ("PIIX3", "piix3"),
        ("ICH9", "ich9"),
    ]
    
    # Firmware types  
    FIRMWARE_TYPES = [
        ("BIOS", "bios"),
        ("EFI", "efi"),
    ]
    
    def __init__(self, vbox: VBoxManager):
        super().__init__()
        self.vbox = vbox
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="create-container"):
            yield Label("[bold cyan]Create New Virtual Machine[/bold cyan]\n")
            
            # Basic settings
            yield Label("[bold yellow]Basic Settings[/bold yellow]", classes="section-header")
            
            with Horizontal(classes="create-row"):
                yield Label("VM Name:", classes="create-label")
                yield Input(placeholder="My Virtual Machine", id="input-name")
            
            with Horizontal(classes="create-row"):
                yield Label("OS Type:", classes="create-label")
                yield Select(
                    options=[(label, value) for label, value in self.OS_TYPES],
                    id="select-ostype",
                    allow_blank=False,
                    value="Ubuntu_64"
                )
            
            with Horizontal(classes="create-row"):
                yield Label("Description:", classes="create-label")
                yield Input(placeholder="Optional description", id="input-description")
            
            # Hardware settings
            yield Label("\n[bold yellow]Hardware[/bold yellow]", classes="section-header")
            
            with Horizontal(classes="create-row"):
                yield Label("Memory (MB):", classes="create-label")
                yield Input(placeholder="2048", id="input-memory", value="2048")
            
            with Horizontal(classes="create-row"):
                yield Label("CPUs:", classes="create-label")
                yield Input(placeholder="2", id="input-cpus", value="2")
            
            with Horizontal(classes="create-row"):
                yield Label("CPU Execution Cap (%):", classes="create-label")
                yield Input(placeholder="100", id="input-cpuexecutioncap", value="100")
            
            with Horizontal(classes="create-row"):
                yield Label("VRAM (MB):", classes="create-label")
                yield Input(placeholder="128", id="input-vram", value="128")
            
            # System settings
            yield Label("\n[bold yellow]System[/bold yellow]", classes="section-header")
            
            with Horizontal(classes="create-row"):
                yield Label("Chipset:", classes="create-label")
                yield Select(
                    options=[(label, value) for label, value in self.CHIPSET_TYPES],
                    id="select-chipset",
                    allow_blank=False,
                    value="piix3"
                )
            
            with Horizontal(classes="create-row"):
                yield Label("Firmware:", classes="create-label")
                yield Select(
                    options=[(label, value) for label, value in self.FIRMWARE_TYPES],
                    id="select-firmware",
                    allow_blank=False,
                    value="bios"
                )
            
            # Graphics settings
            yield Label("\n[bold yellow]Graphics[/bold yellow]", classes="section-header")
            
            with Horizontal(classes="create-row"):
                yield Label("Graphics Controller:", classes="create-label")
                yield Select(
                    options=[(label, value) for label, value in self.GRAPHICS_CONTROLLERS],
                    id="select-graphics",
                    allow_blank=False,
                    value="VMSVGA"
                )
            
            with Horizontal(classes="create-row"):
                yield Label("3D Acceleration:", classes="create-label")
                yield Select(
                    options=[("Enabled", "on"), ("Disabled", "off")],
                    id="select-3d",
                    allow_blank=False,
                    value="off"
                )
            
            # Storage settings
            yield Label("\n[bold yellow]Storage[/bold yellow]", classes="section-header")
            
            with Horizontal(classes="create-row"):
                yield Label("Disk Size (MB):", classes="create-label")
                yield Input(placeholder="20480", id="input-disk", value="20480")
            
            with Horizontal(id="iso-row"):
                yield Label("ISO Image:", classes="create-label")
                yield Input(placeholder="/path/to/image.iso (optional)", id="input-iso")
                yield Button("Browse...", id="btn-browse")
            
            # Network settings
            yield Label("\n[bold yellow]Network[/bold yellow]", classes="section-header")
            
            with Horizontal(classes="create-row"):
                yield Label("Adapter 1:", classes="create-label")
                yield Select(
                    options=[(label, value) for label, value in self.NETWORK_TYPES],
                    id="select-network",
                    allow_blank=False,
                    value="nat"
                )
            
            yield Static("\n[dim]Note: ISO will be attached to DVD drive if provided[/dim]")
            
            with Horizontal(id="button-row"):
                yield Button("Create", variant="success", id="btn-create")
                yield Button("Cancel", variant="default", id="btn-cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-create":
            self.action_create()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-browse":
            self.action_browse()
    
    @work(exclusive=True)
    async def action_create(self) -> None:
        """Create the new VM."""
        try:
            # Get values from inputs
            name = self.query_one("#input-name", Input).value.strip()
            if not name:
                self.notify("VM name is required", severity="error")
                return
            
            description = self.query_one("#input-description", Input).value.strip()
            ostype = self.query_one("#select-ostype", Select).value
            memory = self.query_one("#input-memory", Input).value.strip()
            cpus = self.query_one("#input-cpus", Input).value.strip()
            cpuexecutioncap = self.query_one("#input-cpuexecutioncap", Input).value.strip()
            vram = self.query_one("#input-vram", Input).value.strip()
            chipset = self.query_one("#select-chipset", Select).value
            firmware = self.query_one("#select-firmware", Select).value
            graphics = self.query_one("#select-graphics", Select).value
            accelerate3d = self.query_one("#select-3d", Select).value
            disk_size = self.query_one("#input-disk", Input).value.strip()
            iso_path = self.query_one("#input-iso", Input).value.strip()
            network_type = self.query_one("#select-network", Select).value
            
            # Validate inputs
            try:
                memory_int = int(memory)
                cpus_int = int(cpus)
                cpuexecutioncap_int = int(cpuexecutioncap)
                vram_int = int(vram)
                disk_size_int = int(disk_size)
            except ValueError:
                self.notify("All numeric fields must be valid integers", severity="error")
                return
            
            self.notify(f"Creating VM '{name}'...")
            
            # Create the VM
            await asyncio.to_thread(
                self.vbox.create_vm,
                name=name,
                ostype=ostype,
                memory=memory_int,
                cpus=cpus_int,
                vram=vram_int,
                disk_size=disk_size_int,
                iso_path=iso_path if iso_path else None,
                network_type=network_type,
                description=description if description else None,
                cpuexecutioncap=cpuexecutioncap_int,
                chipset=chipset,
                firmware=firmware,
                graphics_controller=graphics,
                accelerate3d=accelerate3d
            )
            
            self.notify(f"VM '{name}' created successfully!", severity="information")
            self.dismiss(True)
            
        except Exception as e:
            self.notify(f"Error creating VM: {e}", severity="error", timeout=5)
    
    @work
    async def action_browse(self) -> None:
        """Open file browser to select an ISO file."""
        # Get current ISO path if any
        current_path = self.query_one("#input-iso", Input).value.strip()
        
        # Open file browser
        result = await self.app.push_screen_wait(FileBrowser(current_path or None))
        
        # Update input field if a file was selected
        if result:
            self.query_one("#input-iso", Input).value = result
    
    def action_cancel(self) -> None:
        """Cancel and close the screen."""
        self.dismiss(False)
