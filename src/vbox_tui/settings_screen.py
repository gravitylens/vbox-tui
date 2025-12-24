"""Settings screen for application configuration."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, Input, Static
from textual.binding import Binding
from textual import work
import asyncio

from .vbox import VBoxManager


class SettingsScreen(Screen):
    """Screen for editing application settings."""
    
    CSS = """
    SettingsScreen {
        align: center middle;
    }
    
    #settings-container {
        width: 70%;
        max-width: 80;
        max-height: 80%;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
        overflow-y: auto;
    }
    
    .settings-row {
        height: auto;
        margin: 1 0;
    }
    
    .settings-label {
        width: 25;
        padding: 0 1;
    }
    
    Input {
        width: 1fr;
    }
    
    #button-row {
        margin-top: 2;
        height: auto;
        align: center middle;
    }
    
    #button-row Button {
        min-height: 3;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, vbox: VBoxManager):
        super().__init__()
        self.vbox = vbox
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="settings-container"):
            yield Label("[bold cyan]VirtualBox Settings[/bold cyan]\n")
            
            with Horizontal(classes="settings-row"):
                yield Label("Default VM Folder:", classes="settings-label")
                yield Input(placeholder="/path/to/vms", id="input-machine-folder")
            
            yield Static("\n[dim]This is where new VMs will be created by default[/dim]")
            
            with Horizontal(id="button-row"):
                yield Button("Save", variant="success", id="btn-save")
                yield Button("Cancel", variant="default", id="btn-cancel")
            
            # Spacer to ensure buttons are visible when scrolled
            yield Static("\n\n\n")
    
    def on_mount(self) -> None:
        """Load current settings."""
        self.load_settings()
    
    @work(exclusive=True)
    async def load_settings(self) -> None:
        """Load current VirtualBox settings."""
        try:
            folder = await asyncio.to_thread(self.vbox.get_default_machine_folder)
            self.query_one("#input-machine-folder", Input).value = folder
        except Exception as e:
            self.notify(f"Error loading settings: {e}", severity="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-save":
            self.action_save()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
    
    @work(exclusive=True)
    async def action_save(self) -> None:
        """Save settings."""
        try:
            machine_folder = self.query_one("#input-machine-folder", Input).value.strip()
            
            if not machine_folder:
                self.notify("Machine folder cannot be empty", severity="error")
                return
            
            # Expand user path
            import os
            machine_folder = os.path.expanduser(machine_folder)
            
            # Check if path exists
            if not os.path.exists(machine_folder):
                self.notify(f"Path does not exist: {machine_folder}", severity="error")
                return
            
            if not os.path.isdir(machine_folder):
                self.notify(f"Path is not a directory: {machine_folder}", severity="error")
                return
            
            self.notify("Saving settings...")
            await asyncio.to_thread(self.vbox.set_default_machine_folder, machine_folder)
            self.notify("Settings saved successfully!", severity="information")
            self.dismiss(True)
            
        except Exception as e:
            self.notify(f"Error saving settings: {e}", severity="error", timeout=5)
    
    def action_cancel(self) -> None:
        """Cancel and close the screen."""
        self.dismiss(False)
