"""Snapshot management screen."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, DataTable, Input
from textual.binding import Binding
from textual import work

from .vbox import VBoxManager, VM


class TakeSnapshotScreen(Screen):
    """Modal for taking a snapshot."""
    
    CSS = """
    TakeSnapshotScreen {
        align: center middle;
    }
    
    #dialog {
        width: 60;
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
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, vm: VM, vbox: VBoxManager):
        super().__init__()
        self.vm = vm
        self.vbox = vbox
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static(f"Take Snapshot of {self.vm.name}", classes="title")
            yield Static("\nSnapshot Name:")
            yield Input(placeholder="e.g., Before Update", id="name-input")
            yield Static("\nDescription (optional):")
            yield Input(placeholder="Description of this snapshot", id="desc-input")
            with Horizontal(id="buttons"):
                yield Button("Take Snapshot", variant="primary", id="take-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    async def on_mount(self) -> None:
        self.query_one("#name-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "take-btn":
            name = self.query_one("#name-input", Input).value.strip()
            desc = self.query_one("#desc-input", Input).value.strip()
            
            if not name:
                self.notify("Please enter a snapshot name", severity="error")
                return
            
            self.dismiss({"name": name, "description": desc})
        else:
            self.dismiss(None)
    
    def action_cancel(self) -> None:
        self.dismiss(None)


class DeleteSnapshotScreen(Screen):
    """Modal for confirming snapshot deletion."""
    
    CSS = """
    DeleteSnapshotScreen {
        align: center middle;
    }
    
    #dialog {
        width: 50;
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
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, snapshot_name: str):
        super().__init__()
        self.snapshot_name = snapshot_name
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Delete Snapshot", classes="title")
            yield Static(f"\nAre you sure you want to delete the snapshot:\n'{self.snapshot_name}'?")
            yield Static("\nThis action cannot be undone.")
            with Horizontal(id="buttons"):
                yield Button("Delete", variant="error", id="delete-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_cancel(self) -> None:
        self.dismiss(False)


class SnapshotScreen(Screen):
    """Screen for managing VM snapshots."""
    
    CSS = """
    SnapshotScreen {
        background: $surface;
    }
    
    #container {
        width: 100%;
        height: 100%;
        border: solid $accent;
        padding: 1;
    }
    
    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #snapshot-table {
        height: 1fr;
        margin-bottom: 1;
    }
    
    #buttons {
        height: auto;
        width: 100%;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    
    .current-indicator {
        color: $success;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("escape", "close", "Close", priority=True),
        Binding("t", "take_snapshot", "Take Snapshot"),
        Binding("r", "restore_snapshot", "Restore"),
        Binding("d", "delete_snapshot", "Delete"),
    ]
    
    def __init__(self, vm: VM, vbox: VBoxManager):
        super().__init__()
        self.vm = vm
        self.vbox = vbox
        self.snapshots = []
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="container"):
            yield Static(f"Snapshots: {self.vm.name}", id="title")
            table = DataTable(id="snapshot-table", cursor_type="row")
            table.add_columns("", "Name", "UUID")
            yield table
            with Horizontal(id="buttons"):
                yield Button("Take Snapshot (t)", variant="primary", id="take-btn")
                yield Button("Restore (r)", variant="success", id="restore-btn")
                yield Button("Delete (d)", variant="error", id="delete-btn")
                yield Button("Close (Esc)", variant="default", id="close-btn")
        yield Footer()
    
    async def on_mount(self) -> None:
        self.refresh_snapshots()
    
    @work
    async def refresh_snapshots(self) -> None:
        """Refresh the snapshot list."""
        table = self.query_one("#snapshot-table", DataTable)
        table.clear()
        
        self.snapshots = await self.run_in_thread(self.vbox.list_snapshots, self.vm)
        
        if not self.snapshots:
            table.add_row("", "No snapshots", "")
        else:
            for snapshot in self.snapshots:
                indicator = "●" if snapshot.get("current") else ""
                table.add_row(
                    indicator,
                    snapshot.get("name", ""),
                    snapshot.get("uuid", "")[:8] + "..."
                )
    
    def get_selected_snapshot(self):
        """Get the currently selected snapshot."""
        table = self.query_one("#snapshot-table", DataTable)
        if not self.snapshots or table.cursor_row >= len(self.snapshots):
            return None
        return self.snapshots[table.cursor_row]
    
    def action_take_snapshot(self) -> None:
        """Take a new snapshot."""
        self._take_snapshot_worker()
    
    @work
    async def _take_snapshot_worker(self) -> None:
        """Worker to take a new snapshot."""
        take_screen = TakeSnapshotScreen(self.vm, self.vbox)
        result = await self.app.push_screen_wait(take_screen)
        
        if result:
            try:
                self.notify(f"Taking snapshot '{result['name']}'...")
                await self.run_in_thread(
                    self.vbox.take_snapshot,
                    self.vm,
                    result["name"],
                    result.get("description", "")
                )
                self.notify(f"Snapshot '{result['name']}' created", severity="information")
                self.refresh_snapshots()
            except Exception as e:
                self.notify(f"Failed to take snapshot: {e}", severity="error")
    
    def action_restore_snapshot(self) -> None:
        """Restore to the selected snapshot."""
        snapshot = self.get_selected_snapshot()
        if not snapshot:
            self.notify("No snapshot selected", severity="warning")
            return
        
        # Check if VM is running
        if self.vm.is_running:
            self.notify("Cannot restore while VM is running. Stop the VM first.", severity="error")
            return
        
        self._restore_snapshot_worker(snapshot)
    
    @work
    async def _restore_snapshot_worker(self, snapshot: dict) -> None:
        """Worker to restore a snapshot."""
        try:
            self.notify(f"Restoring to snapshot '{snapshot['name']}'...")
            await self.run_in_thread(
                self.vbox.restore_snapshot,
                self.vm,
                snapshot["uuid"]
            )
            self.notify(f"Restored to snapshot '{snapshot['name']}'", severity="information")
            self.refresh_snapshots()
        except Exception as e:
            self.notify(f"Failed to restore snapshot: {e}", severity="error")
    
    def action_delete_snapshot(self) -> None:
        """Delete the selected snapshot."""
        snapshot = self.get_selected_snapshot()
        if not snapshot:
            self.notify("No snapshot selected", severity="warning")
            return
        
        self._delete_snapshot_worker(snapshot)
    
    @work
    async def _delete_snapshot_worker(self, snapshot: dict) -> None:
        """Worker to delete a snapshot."""
        delete_screen = DeleteSnapshotScreen(snapshot["name"])
        result = await self.app.push_screen_wait(delete_screen)
        
        if result:
            try:
                self.notify(f"Deleting snapshot '{snapshot['name']}'...")
                await self.run_in_thread(
                    self.vbox.delete_snapshot,
                    self.vm,
                    snapshot["uuid"]
                )
                self.notify(f"Snapshot '{snapshot['name']}' deleted", severity="information")
                self.refresh_snapshots()
            except Exception as e:
                self.notify(f"Failed to delete snapshot: {e}", severity="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "take-btn":
            self.action_take_snapshot()
        elif event.button.id == "restore-btn":
            self.action_restore_snapshot()
        elif event.button.id == "delete-btn":
            self.action_delete_snapshot()
        elif event.button.id == "close-btn":
            self.action_close()
    
    def action_close(self) -> None:
        self.dismiss()
    
    async def run_in_thread(self, func, *args):
        """Run a blocking function in a thread."""
        import asyncio
        return await asyncio.to_thread(func, *args)
