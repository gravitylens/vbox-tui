"""Export progress screen."""
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Static, ProgressBar, Button
from textual.binding import Binding


class ExportProgressScreen(ModalScreen):
    """Modal screen showing export progress."""
    
    CSS = """
    ExportProgressScreen {
        align: center middle;
    }
    
    #dialog {
        width: 70;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
        layout: vertical;
    }
    
    #dialog > * {
        width: 100%;
    }
    
    #title {
        margin-bottom: 1;
    }
    
    #path {
        margin-bottom: 1;
    }
    
    ProgressBar {
        width: 100% !important;
        min-width: 100% !important;
    }
    
    ProgressBar > * {
        width: 100% !important;
    }
    
    ProgressBar Bar {
        width: 100% !important;
    }
    
    .full-width {
        width: 100% !important;
    }
    
    #progress {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        margin: 0;
    }
    
    #status {
        margin-top: 1;
        margin-bottom: 1;
        text-align: center;
    }
    
    #action-button {
        width: 100%;
    }
    
    .success {
        color: $success;
    }
    
    .error {
        color: $error;
    }
    """
    
    def __init__(self, vm_name: str, output_path: str):
        super().__init__()
        self.vm_name = vm_name
        self.output_path = output_path
        self.completed = False
        self.error_message = None
        self.cancel_callback = None
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static(f"[bold cyan]Exporting VM:[/bold cyan] {self.vm_name}", id="title")
            yield Static(f"Output: {self.output_path}", id="path")
            yield ProgressBar(id="progress", total=None, show_eta=False, show_percentage=False, classes="full-width")
            yield Static("Exporting... This may take several minutes.", id="status")
            yield Button("Cancel", id="action-button", variant="error")
    
    def on_mount(self) -> None:
        """Start the progress bar animation."""
        progress = self.query_one("#progress", ProgressBar)
        progress.update(total=None)  # Indeterminate mode
        # Force width after mount
        self.call_after_refresh(self._set_progress_width)
    
    def _set_progress_width(self) -> None:
        """Set progress bar width after refresh."""
        progress = self.query_one("#progress", ProgressBar)
        progress.styles.width = "100%"
    
    def update_status(self, message: str, is_error: bool = False) -> None:
        """Update the status message."""
        status = self.query_one("#status", Static)
        if is_error:
            status.update(f"[bold red]{message}[/bold red]")
            status.add_class("error")
        else:
            status.update(message)
    
    def mark_complete(self, success: bool, message: str = None) -> None:
        """Mark the export as complete."""
        self.completed = True
        progress = self.query_one("#progress", ProgressBar)
        status = self.query_one("#status", Static)
        action_btn = self.query_one("#action-button", Button)
        
        if success:
            progress.update(progress=100, total=100)  # Show full bar
            status.update(f"[bold green]✓ {message or 'Export completed successfully!'}[/bold green]")
            status.add_class("success")
            # Auto-dismiss after a brief moment
            self.set_timer(2, self._auto_dismiss)
            action_btn.display = False  # Hide button on success
        else:
            progress.remove()  # Remove progress bar on error
            self.error_message = message
            # Escape message for Rich markup
            if message:
                escaped_msg = message.replace("[", "\\[").replace("]", "\\]")
                status.update(f"[bold red]✗ Export failed:[/bold red]\n{escaped_msg}")
            else:
                status.update("[bold red]✗ Export failed[/bold red]")
            status.add_class("error")
            
            # Change to Close button on error
            action_btn.label = "Close"
            action_btn.variant = "primary"
            action_btn.focus()
    
    def _auto_dismiss(self) -> None:
        """Timer callback to auto-dismiss the modal."""
        self.dismiss(True)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle action button (Cancel or Close)."""
        if event.button.id == "action-button":
            if not self.completed:
                # Still exporting - cancel it
                if self.cancel_callback:
                    self.cancel_callback()
                self.dismiss(False)
            else:
                # Export finished with error - just close
                self.dismiss(False)
