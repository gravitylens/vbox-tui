"""Simple file browser screen for selecting ISO files."""
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, DirectoryTree, Static
from textual.binding import Binding


class FileBrowser(Screen):
    """Screen for browsing and selecting a file."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
    ]
    
    CSS = """
    FileBrowser {
        align: center middle;
    }
    
    #browser-container {
        width: 80%;
        max-height: 80%;
        border: solid $accent;
        padding: 1 2;
        background: $surface;
    }
    
    #browser-header {
        height: 3;
        margin-bottom: 1;
    }
    
    DirectoryTree {
        height: 1fr;
        margin: 1 0;
    }
    
    #browser-footer {
        height: auto;
        margin-top: 1;
    }
    
    #button-row {
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
    
    def __init__(self, initial_path: str = None):
        """Initialize the file browser.
        
        Args:
            initial_path: Initial path to show in the browser
        """
        super().__init__()
        self.initial_path = initial_path or str(Path.home())
        self.selected_path = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="browser-container"):
            with Vertical(id="browser-header"):
                yield Label("[bold cyan]Select ISO File[/bold cyan]")
                yield Static("[dim]Press Enter to select, Escape to cancel[/dim]")
            
            yield DirectoryTree(self.initial_path)
            
            with Vertical(id="browser-footer"):
                yield Static(f"Selected: [cyan]{self.selected_path or 'None'}[/cyan]", id="selected-file")
                with Horizontal(id="button-row"):
                    yield Button("Select", variant="success", id="btn-select")
                    yield Button("Cancel", variant="default", id="btn-cancel")
                
                # Spacer to ensure buttons are visible
                yield Static("\n\n")
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection in the tree."""
        self.selected_path = str(event.path)
        self.query_one("#selected-file", Static).update(
            f"Selected: [cyan]{self.selected_path}[/cyan]"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-select":
            self.action_select()
        elif event.button.id == "btn-cancel":
            self.action_cancel()
    
    def action_select(self) -> None:
        """Select the current file and close."""
        if self.selected_path:
            self.dismiss(self.selected_path)
        else:
            self.notify("Please select a file first", severity="warning")
    
    def action_cancel(self) -> None:
        """Cancel and close the screen."""
        self.dismiss(None)
