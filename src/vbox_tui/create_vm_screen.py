"""Screen for creating new VMs."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, Input, Static, Select
from textual.binding import Binding
from textual import work
import asyncio

from .vbox import VBoxManager


class CreateVMScreen(Screen):
    """Screen for creating a new VM."""
    
    CSS = """
    CreateVMScreen {
        align: center middle;
    }
    
    #create-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }
    
    .create-row {
        height: auto;
        margin: 1 0;
    }
    
    .create-label {
        width: 20;
        padding: 0 1;
    }
    
    Input {
        width: 1fr;
    }
    
    Select {
        width: 1fr;
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
    
    def __init__(self, vbox: VBoxManager):
        super().__init__()
        self.vbox = vbox
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="create-container"):
            yield Label("[bold cyan]Create New Virtual Machine[/bold cyan]\n")
            
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
                yield Label("Memory (MB):", classes="create-label")
                yield Input(placeholder="2048", id="input-memory", value="2048")
            
            with Horizontal(classes="create-row"):
                yield Label("CPUs:", classes="create-label")
                yield Input(placeholder="2", id="input-cpus", value="2")
            
            with Horizontal(classes="create-row"):
                yield Label("VRAM (MB):", classes="create-label")
                yield Input(placeholder="128", id="input-vram", value="128")
            
            with Horizontal(classes="create-row"):
                yield Label("Disk Size (MB):", classes="create-label")
                yield Input(placeholder="20480", id="input-disk", value="20480")
            
            yield Static("\n[dim]Note: This creates a VM with a dynamically allocated disk[/dim]")
            
            with Horizontal(id="button-row"):
                yield Button("Create", variant="success", id="btn-create")
                yield Button("Cancel", variant="default", id="btn-cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-create":
            self.action_create()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
    
    @work(exclusive=True)
    async def action_create(self) -> None:
        """Create the new VM."""
        try:
            # Get values from inputs
            name = self.query_one("#input-name", Input).value.strip()
            if not name:
                self.notify("VM name is required", severity="error")
                return
            
            ostype = self.query_one("#select-ostype", Select).value
            memory = self.query_one("#input-memory", Input).value.strip()
            cpus = self.query_one("#input-cpus", Input).value.strip()
            vram = self.query_one("#input-vram", Input).value.strip()
            disk_size = self.query_one("#input-disk", Input).value.strip()
            
            # Validate inputs
            try:
                memory_int = int(memory)
                cpus_int = int(cpus)
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
                disk_size=disk_size_int
            )
            
            self.notify(f"VM '{name}' created successfully!", severity="information")
            self.dismiss(True)
            
        except Exception as e:
            self.notify(f"Error creating VM: {e}", severity="error", timeout=5)
    
    def action_cancel(self) -> None:
        """Cancel and close the screen."""
        self.dismiss(False)
