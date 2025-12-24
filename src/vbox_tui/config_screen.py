"""Configuration screen for VM settings."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Button, Label, Input, Static, Select
from textual.binding import Binding
from textual import work
import asyncio

from .vbox import VBoxManager, VM
from .file_browser import FileBrowser


class ConfigScreen(Screen):
    """Screen for editing VM configuration."""
    
    NETWORK_TYPES = [
        ("NAT", "nat"),
        ("Bridged", "bridged"),
        ("Internal", "intnet"),
        ("Host-only", "hostonly"),
        ("None", "none"),
    ]
    
    CSS = """
    ConfigScreen {
        align: center middle;
    }
    
    #config-container {
        width: 80;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }
    
    .config-row {
        height: auto;
        margin: 1 0;
    }
    
    .config-label {
        width: 20;
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
    
    def __init__(self, vm: VM, vbox: VBoxManager):
        super().__init__()
        self.vm = vm
        self.vbox = vbox
        self.vm_info = {}
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="config-container"):
            yield Label(f"[bold cyan]Configure: {self.vm.name}[/bold cyan]")
            yield Label(f"[dim]UUID: {self.vm.uuid}[/dim]\n")
            
            with Horizontal(classes="config-row"):
                yield Label("Memory (MB):", classes="config-label")
                yield Input(placeholder="2048", id="input-memory")
            
            with Horizontal(classes="config-row"):
                yield Label("CPUs:", classes="config-label")
                yield Input(placeholder="2", id="input-cpus")
            
            with Horizontal(classes="config-row"):
                yield Label("VRAM (MB):", classes="config-label")
                yield Input(placeholder="128", id="input-vram")
            
            with Horizontal(classes="config-row"):
                yield Label("Boot Device:", classes="config-label")
                yield Input(placeholder="disk", id="input-boot")
            
            with Horizontal(id="iso-row"):
                yield Label("ISO Image:", classes="config-label")
                yield Input(placeholder="/path/to/image.iso (optional)", id="input-iso")
                yield Button("Browse...", id="btn-browse")
            
            with Horizontal(classes="config-row"):
                yield Label("Network:", classes="config-label")
                yield Select(
                    options=[(label, value) for label, value in self.NETWORK_TYPES],
                    id="select-network",
                    allow_blank=False,
                    value="nat"
                )
            
            yield Static("\n[dim]Note: VM must be powered off to change settings[/dim]")
            
            with Horizontal(id="button-row"):
                yield Button("Save", variant="success", id="btn-save")
                yield Button("Cancel", variant="default", id="btn-cancel")
    
    def on_mount(self) -> None:
        """Load current VM settings."""
        self.load_vm_info()
    
    @work(exclusive=True)
    async def load_vm_info(self) -> None:
        """Load VM information and populate inputs."""
        try:
            self.vm_info = await asyncio.to_thread(self.vbox.get_vm_info, self.vm)
            
            # Populate inputs with current values
            if "memory" in self.vm_info:
                self.query_one("#input-memory", Input).value = self.vm_info["memory"]
            if "cpus" in self.vm_info:
                self.query_one("#input-cpus", Input).value = self.vm_info["cpus"]
            if "vram" in self.vm_info:
                self.query_one("#input-vram", Input).value = self.vm_info["vram"]
            if "boot1" in self.vm_info:
                self.query_one("#input-boot", Input).value = self.vm_info["boot1"]
            
            # Load DVD drive info
            dvd_key = '"SATA Controller-ImageUUID-1-0"'
            if dvd_key in self.vm_info and self.vm_info[dvd_key] != "none":
                # Try to get the ISO path
                iso_key = '"SATA Controller-1-0"'
                if iso_key in self.vm_info:
                    iso_path = self.vm_info[iso_key]
                    if iso_path and iso_path != "none" and iso_path != "emptydrive":
                        self.query_one("#input-iso", Input).value = iso_path
            
            # Load network configuration
            if "nic1" in self.vm_info:
                network_type = self.vm_info["nic1"]
                self.query_one("#select-network", Select).value = network_type
        except Exception as e:
            self.notify(f"Error loading VM info: {e}", severity="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-save":
            self.action_save()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-browse":
            self.action_browse()
    
    @work(exclusive=True)
    async def action_save(self) -> None:
        """Save configuration changes."""
        if self.vm.is_running:
            self.notify("Cannot modify running VM. Stop it first.", severity="error")
            return
        
        try:
            # Get values from inputs
            memory = self.query_one("#input-memory", Input).value.strip()
            cpus = self.query_one("#input-cpus", Input).value.strip()
            vram = self.query_one("#input-vram", Input).value.strip()
            boot = self.query_one("#input-boot", Input).value.strip()
            iso_path = self.query_one("#input-iso", Input).value.strip()
            network_type = self.query_one("#select-network", Select).value
            
            # Apply changes
            changes_made = False
            if memory and memory != self.vm_info.get("memory", ""):
                await asyncio.to_thread(self.vbox.modify_vm, self.vm, "memory", memory)
                changes_made = True
            
            if cpus and cpus != self.vm_info.get("cpus", ""):
                await asyncio.to_thread(self.vbox.modify_vm, self.vm, "cpus", cpus)
                changes_made = True
            
            if vram and vram != self.vm_info.get("vram", ""):
                await asyncio.to_thread(self.vbox.modify_vm, self.vm, "vram", vram)
                changes_made = True
            
            if boot and boot != self.vm_info.get("boot1", ""):
                await asyncio.to_thread(self.vbox.modify_vm, self.vm, "boot1", boot)
                changes_made = True
            
            # Handle ISO attachment/detachment
            current_iso = ""
            iso_key = '"SATA Controller-1-0"'
            if iso_key in self.vm_info:
                current_iso = self.vm_info[iso_key]
                if current_iso in ["none", "emptydrive"]:
                    current_iso = ""
            
            if iso_path != current_iso:
                await asyncio.to_thread(self.vbox.attach_iso, self.vm, iso_path if iso_path else None)
                changes_made = True
            
            # Handle network configuration
            if network_type and network_type != self.vm_info.get("nic1", ""):
                await asyncio.to_thread(self.vbox.modify_vm, self.vm, "nic1", network_type)
                changes_made = True
            
            if changes_made:
                self.notify("Configuration saved successfully", severity="information")
            else:
                self.notify("No changes to save", severity="information")
            
            self.dismiss(True)
        except Exception as e:
            self.notify(f"Error saving configuration: {e}", severity="error", timeout=5)
    
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
