"""Confirmation screen for force poweroff."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, Static
from textual.binding import Binding

from .vbox import VM


class ForcePoweroffScreen(Screen):
    """Screen to confirm force poweroff."""
    
    CSS = """
    ForcePoweroffScreen {
        align: center middle;
    }
    
    #confirm-container {
        width: 60;
        height: auto;
        border: solid $warning;
        padding: 2;
        background: $surface;
    }
    
    #warning {
        color: $warning;
        text-align: center;
        margin: 1 0;
    }
    
    #vm-info {
        text-align: center;
        margin: 1 0;
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
            yield Label("[bold yellow]⚠ FORCE POWEROFF ⚠[/bold yellow]", id="warning")
            
            yield Label(
                f"[bold cyan]{self.vm.name}[/bold cyan]\n"
                f"[dim]State: {self.vm.state}[/dim]",
                id="vm-info"
            )
            
            yield Static(
                "\nThis will immediately power off the VM without\n"
                "giving the operating system time to shut down properly.\n"
            )
            
            yield Static(
                "[dim]Warning: This may result in data loss or corruption.\n"
                "Use this only if the VM is not responding to a normal shutdown.[/dim]"
            )
            
            with Horizontal(id="button-row"):
                yield Button("Force Poweroff", variant="error", id="btn-confirm")
                yield Button("Cancel", variant="default", id="btn-cancel")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        elif event.button.id == "btn-cancel":
            self.dismiss(False)
    
    def action_cancel(self) -> None:
        """Cancel and close the screen."""
        self.dismiss(False)
