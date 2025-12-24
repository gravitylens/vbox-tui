"""Main Textual application for VirtualBox TUI."""
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, DataTable, Static, Button
from textual.binding import Binding
from textual.reactive import reactive
from textual import work
from textual.worker import Worker, WorkerState
from rich.text import Text
import asyncio
import logging

from .vbox import VBoxManager, VM
from .config_screen import ConfigScreen
from .create_vm_screen import CreateVMScreen

# Set up logging
logging.basicConfig(
    filename='/tmp/vbox-tui-debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VMInfoPanel(Static):
    """Panel showing detailed information about selected VM."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vm: VM | None = None
    
    def update_vm(self, vm: VM | None, detailed_info: dict = None):
        """Update the panel with VM information."""
        self.vm = vm
        if not vm:
            self.update("No VM selected")
            return
        
        info_text = f"""[bold cyan]{vm.name}[/bold cyan]
[dim]UUID:[/dim] {vm.uuid}
[dim]State:[/dim] {vm.status_icon} {vm.state.upper()}
[dim]Memory:[/dim] {vm.memory} MB
[dim]CPUs:[/dim] {vm.cpus}
[dim]OS Type:[/dim] {vm.os_type}
"""
        
        if detailed_info:
            info_text += "\n[bold]Additional Info:[/bold]\n"
            for key in ["boot1", "vram", "nic1"]:
                if key in detailed_info:
                    info_text += f"[dim]{key}:[/dim] {detailed_info[key]}\n"
        
        self.update(info_text)


class VBoxTUI(App):
    """A Textual TUI for managing VirtualBox VMs."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 2fr 1fr;
    }
    
    #vm-table {
        height: 100%;
    }
    
    #info-panel {
        height: 100%;
        border: solid $accent;
        padding: 1;
    }
    
    DataTable {
        height: 100%;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("n", "new_vm", "New VM"),
        Binding("s", "start_vm", "Start"),
        Binding("t", "stop_vm", "Stop"),
        Binding("f", "force_poweroff", "Force Poweroff"),
        Binding("p", "pause_vm", "Pause/Resume"),
        Binding("v", "save_state", "Save State"),
        Binding("g", "show_gui", "Show GUI"),
        Binding("h", "toggle_headless", "Toggle Headless"),
        Binding("c", "config", "Config"),
        Binding("d", "delete_vm", "Delete"),
    ]
    
    TITLE = "VirtualBox TUI"
    
    selected_vm: reactive[VM | None] = reactive(None)
    headless_mode: reactive[bool] = reactive(True)
    
    def __init__(self):
        super().__init__()
        self.vbox = VBoxManager()
        self.vms: list[VM] = []
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        
        table = DataTable(id="vm-table", cursor_type="row")
        table.add_columns("", "Name", "State", "Memory", "CPUs", "OS Type")
        yield table
        
        yield VMInfoPanel(id="info-panel")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Load VMs when app starts."""
        self.refresh_vms()
        # Set up automatic refresh every 3 seconds
        self.set_interval(3, self.refresh_vms)
    
    @work(exclusive=True)
    async def refresh_vms(self) -> None:
        """Refresh the VM list."""
        try:
            # Run in thread pool to avoid blocking
            self.vms = await asyncio.to_thread(self.vbox.list_vms)
            self.update_table()
        except Exception as e:
            self.notify(f"Error loading VMs: {e}", severity="error", timeout=5)
    
    def update_table(self) -> None:
        """Update the data table with current VMs."""
        table = self.query_one("#vm-table", DataTable)
        table.clear()
        
        for vm in self.vms:
            status_style = self._get_status_style(vm.state)
            table.add_row(
                vm.status_icon,
                vm.name,
                Text(vm.state.upper(), style=status_style),
                f"{vm.memory} MB",
                str(vm.cpus),
                vm.os_type,
                key=vm.uuid
            )
        
        # Update status
        mode = "headless" if self.headless_mode else "GUI"
        self.sub_title = f"{len(self.vms)} VMs | Mode: {mode}"
    
    def _get_status_style(self, state: str) -> str:
        """Get color style for VM state."""
        styles = {
            "running": "bold green",
            "paused": "yellow",
            "saved": "cyan",
            "poweroff": "dim",
            "aborted": "red",
        }
        return styles.get(state, "white")
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the table."""
        uuid = event.row_key.value
        self.selected_vm = next((vm for vm in self.vms if vm.uuid == uuid), None)
        
        if self.selected_vm:
            self.update_info_panel()
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row highlight (cursor movement) in the table."""
        if event.row_key is not None:
            uuid = event.row_key.value
            self.selected_vm = next((vm for vm in self.vms if vm.uuid == uuid), None)
            
            if self.selected_vm:
                self.update_info_panel()
    
    @work(exclusive=True)
    async def update_info_panel(self) -> None:
        """Update the info panel with detailed VM info."""
        if not self.selected_vm:
            return
        
        info_panel = self.query_one("#info-panel", VMInfoPanel)
        
        try:
            detailed_info = await asyncio.to_thread(
                self.vbox.get_vm_info, 
                self.selected_vm
            )
            info_panel.update_vm(self.selected_vm, detailed_info)
        except Exception as e:
            info_panel.update_vm(self.selected_vm)
            self.notify(f"Error loading VM details: {e}", severity="warning")
    
    def action_toggle_headless(self) -> None:
        """Toggle headless/GUI mode."""
        self.headless_mode = not self.headless_mode
        mode = "headless" if self.headless_mode else "GUI"
        self.notify(f"Start mode: {mode}")
        self.update_table()
    
    @work(exclusive=True)
    async def action_start_vm(self) -> None:
        """Start the selected VM."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        if self.selected_vm.is_running:
            self.notify(f"{self.selected_vm.name} is already running", severity="warning")
            return
        
        try:
            self.notify(f"Starting {self.selected_vm.name}...")
            await asyncio.to_thread(
                self.vbox.start_vm, 
                self.selected_vm, 
                self.headless_mode
            )
            self.notify(f"{self.selected_vm.name} started", severity="information")
            await asyncio.sleep(1)
            self.refresh_vms()
        except Exception as e:
            self.notify(f"Error starting VM: {e}", severity="error", timeout=5)
    
    @work(exclusive=True)
    async def action_stop_vm(self) -> None:
        """Stop the selected VM."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        if not self.selected_vm.is_running:
            self.notify(f"{self.selected_vm.name} is not running", severity="warning")
            return
        
        try:
            self.notify(f"Stopping {self.selected_vm.name}...")
            await asyncio.to_thread(self.vbox.stop_vm, self.selected_vm)
            self.notify(f"Shutdown signal sent to {self.selected_vm.name}", severity="information")
            await asyncio.sleep(2)
            self.refresh_vms()
        except Exception as e:
            self.notify(f"Error stopping VM: {e}", severity="error", timeout=5)
    
    def action_force_poweroff(self) -> None:
        """Force poweroff the selected VM."""
        self._force_poweroff_worker()
    
    @work(exclusive=True)
    async def _force_poweroff_worker(self) -> None:
        """Worker for force poweroff with confirmation."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        if not self.selected_vm.is_running and self.selected_vm.state != "paused":
            self.notify(f"{self.selected_vm.name} is not running", severity="warning")
            return
        
        # Confirm force poweroff
        from .force_poweroff_screen import ForcePoweroffScreen
        confirm_screen = ForcePoweroffScreen(self.selected_vm)
        result = await self.app.push_screen_wait(confirm_screen)
        
        if result:  # If user confirmed
            await self._do_force_poweroff()
    
    async def _do_force_poweroff(self) -> None:
        """Actually force poweroff the VM."""
        if not self.selected_vm:
            return
        
        vm_name = self.selected_vm.name
        
        try:
            self.notify(f"Force powering off {vm_name}...", severity="warning")
            await asyncio.to_thread(self.vbox.stop_vm, self.selected_vm, force=True)
            self.notify(f"{vm_name} powered off", severity="information")
            await asyncio.sleep(1)
            self.refresh_vms()
        except Exception as e:
            self.notify(f"Error powering off VM: {e}", severity="error", timeout=5)
    
    @work(exclusive=True)
    async def action_pause_vm(self) -> None:
        """Pause or resume the selected VM."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        try:
            if self.selected_vm.state == "paused":
                self.notify(f"Resuming {self.selected_vm.name}...")
                await asyncio.to_thread(self.vbox.resume_vm, self.selected_vm)
                self.notify(f"{self.selected_vm.name} resumed", severity="information")
            elif self.selected_vm.is_running:
                self.notify(f"Pausing {self.selected_vm.name}...")
                await asyncio.to_thread(self.vbox.pause_vm, self.selected_vm)
                self.notify(f"{self.selected_vm.name} paused", severity="information")
            else:
                self.notify("VM must be running to pause", severity="warning")
            
            await asyncio.sleep(1)
            self.refresh_vms()
        except Exception as e:
            self.notify(f"Error pausing/resuming VM: {e}", severity="error", timeout=5)
    
    @work(exclusive=True)
    async def action_save_state(self) -> None:
        """Save VM state."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        if not self.selected_vm.is_running:
            self.notify(f"{self.selected_vm.name} is not running", severity="warning")
            return
        
        try:
            self.notify(f"Saving state of {self.selected_vm.name}...")
            await asyncio.to_thread(self.vbox.save_state, self.selected_vm)
            self.notify(f"State saved for {self.selected_vm.name}", severity="information")
            await asyncio.sleep(1)
            self.refresh_vms()
        except Exception as e:
            self.notify(f"Error saving state: {e}", severity="error", timeout=5)
    
    @work(exclusive=True)
    async def action_show_gui(self) -> None:
        """Show/reconnect to VM GUI window."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        try:
            self.notify(f"Opening GUI for {self.selected_vm.name}...")
            await asyncio.to_thread(self.vbox.show_vm, self.selected_vm)
            self.notify(f"GUI window opened for {self.selected_vm.name}", severity="information")
        except Exception as e:
            self.notify(f"Error showing GUI: {e}", severity="error", timeout=5)
    
    async def action_config(self) -> None:
        """Open config screen."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        config_screen = ConfigScreen(self.selected_vm, self.vbox)
        result = await self.push_screen(config_screen)
        
        if result:  # If changes were saved
            self.refresh_vms()
    async def action_new_vm(self) -> None:
        """Open create VM screen."""
        create_screen = CreateVMScreen(self.vbox)
        result = await self.push_screen(create_screen)
        
        if result:  # If VM was created
            self.refresh_vms()
    
    def action_delete_vm(self) -> None:
        """Delete the selected VM."""
        self._delete_vm_worker()
    
    @work(exclusive=True)
    async def _delete_vm_worker(self) -> None:
        """Worker to handle VM deletion with confirmation."""
        if not self.selected_vm:
            self.notify("No VM selected", severity="warning")
            return
        
        # Confirm deletion
        from .delete_confirm_screen import DeleteConfirmScreen
        confirm_screen = DeleteConfirmScreen(self.selected_vm)
        result = await self.app.push_screen_wait(confirm_screen)
        
        if result is not None:  # If user confirmed (result is True or False)
            await self._do_delete_vm(result)
    
    async def _do_delete_vm(self, delete_files: bool) -> None:
        """Actually delete the VM."""
        if not self.selected_vm:
            return
        
        vm_name = self.selected_vm.name
        
        try:
            self.notify(f"Deleting VM '{vm_name}'...", severity="information")
            
            await asyncio.to_thread(
                self.vbox.delete_vm,
                self.selected_vm,
                delete_files
            )
            
            files_msg = "with files" if delete_files else "(keeping files)"
            self.notify(f"VM '{vm_name}' deleted {files_msg}", severity="information")
            self.selected_vm = None
            await asyncio.sleep(1)
            self.refresh_vms()
        except Exception as e:
            self.notify(f"Error deleting VM: {str(e)}", severity="error", timeout=10)
    
    # Button handlers
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "btn-new":
            self.action_new_vm()
        elif button_id == "btn-start":
            self.action_start_vm()
        elif button_id == "btn-stop":
            self.action_stop_vm()
        elif button_id == "btn-pause":
            self.action_pause_vm()
        elif button_id == "btn-save":
            self.action_save_state()
        elif button_id == "btn-config":
            self.action_config()


def main():
    """Run the application."""
    app = VBoxTUI()
    app.run()


if __name__ == "__main__":
    main()
