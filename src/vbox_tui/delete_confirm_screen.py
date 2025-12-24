"""Confirmation screen for deleting VMs."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, Static, Checkbox
from textual.binding import Binding
import logging

from .vbox import VM

logger = logging.getLogger(__name__)


class DeleteConfirmScreen(Screen):
    """Screen to confirm VM deletion."""
    
    CSS = """
    DeleteConfirmScreen {
        align: center middle;
    }
    
    #confirm-container {
        width: 60;
        height: auto;
        border: solid $error;
        padding: 2;
        background: $surface;
    }
    
    #warning {
        color: $error;
        text-align: center;
        margin: 1 0;
    }
    
    #vm-info {
        text-align: center;
        margin: 1 0;
    }
    
    #checkbox-row {
        margin: 2 0;
        align: center middle;
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
    
    def __init__(self, vm: VM):
        super().__init__()
        self.vm = vm
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="confirm-container"):
            yield Label("[bold red]⚠ DELETE VIRTUAL MACHINE ⚠[/bold red]", id="warning")
            
            yield Label(
                f"[bold cyan]{self.vm.name}[/bold cyan]\n"
                f"[dim]UUID: {self.vm.uuid}[/dim]",
                id="vm-info"
            )
            
            yield Static("\nAre you sure you want to delete this VM?\n")
            
            with Horizontal(id="checkbox-row"):
                yield Checkbox("Delete all files (disk images, etc.)", id="delete-files", value=True)
            
            yield Static(
                "[dim]Warning: If you choose to delete files, all VM data\n"
                "including virtual disks will be permanently removed![/dim]"
            )
            
            with Horizontal(id="button-row"):
                yield Button("Delete VM", variant="error", id="btn-confirm")
                yield Button("Cancel", variant="default", id="btn-cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-confirm":
            delete_files = self.query_one("#delete-files", Checkbox).value
            self.dismiss(delete_files)
        elif event.button.id == "btn-cancel":
            self.dismiss(None)
    
    def action_cancel(self) -> None:
        """Cancel and close the screen."""
        self.dismiss(None)
