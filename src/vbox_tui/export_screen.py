"""VM export screen."""
import os
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, Input, Select
from textual.binding import Binding

from .vbox import VBoxManager, VM
from .file_browser import FileBrowser


class ExportScreen(Screen):
    """Screen for exporting a VM to OVA format."""
    
    CSS = """
    ExportScreen {
        align: center middle;
    }
    
    #dialog {
        width: 80;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1;
    }
    
    #buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    Input {
        margin: 1 0;
    }
    
    Select {
        margin: 1 0;
        width: 100%;
    }
    
    .label {
        margin-top: 1;
    }
    
    .info {
        color: $text-muted;
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, vm: VM, vbox: VBoxManager):
        super().__init__()
        self.vm = vm
        self.vbox = vbox
        self.selected_path = None
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static(f"[bold cyan]Export VM:[/bold cyan] {self.vm.name}", classes="title")
            yield Static(
                "Export this VM to an OVA file that can be imported into VirtualBox or other virtualization software.",
                classes="info"
            )
            
            yield Static("Output File:", classes="label")
            with Horizontal():
                yield Input(
                    placeholder=f"/path/to/{self.vm.name}.ova",
                    id="path-input",
                    value=os.path.expanduser(f"~/{self.vm.name}.ova")
                )
                yield Button("Browse...", id="browse-btn", variant="default")
            
            yield Static("OVF Version:", classes="label")
            yield Select(
                options=[
                    ("OVF 0.9 (legacy)", "0.9"),
                    ("OVF 1.0", "1.0"),
                    ("OVF 2.0 (recommended)", "2.0"),
                ],
                value="2.0",
                id="ovf-select"
            )
            
            yield Static("Options:", classes="label")
            yield Static("✓ Include manifest file (for integrity verification)", classes="info")
            
            with Horizontal(id="buttons"):
                yield Button("Export", variant="primary", id="export-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    async def on_mount(self) -> None:
        """Focus the path input on mount."""
        self.query_one("#path-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "export-btn":
            await self._handle_export()
        elif event.button.id == "browse-btn":
            await self._handle_browse()
        else:
            self.dismiss(None)
    
    async def _handle_browse(self) -> None:
        """Open file browser to select output location."""
        # Get current path or use home directory
        current_path = self.query_one("#path-input", Input).value
        if current_path:
            start_path = os.path.dirname(current_path) or os.path.expanduser("~")
        else:
            start_path = os.path.expanduser("~")
        
        # Open file browser
        file_browser = FileBrowser(start_path=start_path, select_file=True)
        result = await self.app.push_screen_wait(file_browser)
        
        if result:
            # Ensure .ova extension
            if not result.endswith('.ova'):
                result += '.ova'
            self.query_one("#path-input", Input).value = result
    
    async def _handle_export(self) -> None:
        """Handle the export action."""
        output_path = self.query_one("#path-input", Input).value.strip()
        ovf_version = self.query_one("#ovf-select", Select).value
        
        if not output_path:
            self.notify("Please enter an output file path", severity="error")
            return
        
        # Expand user home directory
        output_path = os.path.expanduser(output_path)
        
        # Ensure .ova extension
        if not output_path.endswith('.ova'):
            output_path += '.ova'
        
        # Check if file already exists
        if os.path.exists(output_path):
            self.notify(
                f"File already exists: {output_path}\nPlease choose a different location.",
                severity="error",
                timeout=5
            )
            return
        
        # Check if parent directory exists
        parent_dir = os.path.dirname(output_path)
        if parent_dir and not os.path.exists(parent_dir):
            self.notify(
                f"Directory does not exist: {parent_dir}",
                severity="error",
                timeout=5
            )
            return
        
        # Return the export configuration
        self.dismiss({
            "output_path": output_path,
            "ovf_version": ovf_version,
            "manifest": True
        })
    
    def action_cancel(self) -> None:
        """Cancel and close the screen."""
        self.dismiss(None)
