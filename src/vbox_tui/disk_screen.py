"""Disk management screen."""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, DataTable, Input, Select
from textual.binding import Binding
from textual import work
import os

from .vbox import VBoxManager, VM
from .file_browser import FileBrowser


class CreateDiskScreen(Screen):
    """Modal for creating a new disk."""
    
    CSS = """
    CreateDiskScreen {
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
            yield Static(f"Create New Disk for {self.vm.name}", classes="title")
            yield Static("\nDisk Name:")
            yield Input(placeholder="e.g., data-disk.vdi", id="name-input")
            yield Static("\nSize (GB):")
            yield Input(placeholder="e.g., 10", id="size-input", value="10")
            with Horizontal(id="buttons"):
                yield Button("Create & Attach", variant="primary", id="create-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    async def on_mount(self) -> None:
        self.query_one("#name-input", Input).focus()
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-btn":
            name = self.query_one("#name-input", Input).value.strip()
            size = self.query_one("#size-input", Input).value.strip()
            
            if not name:
                self.notify("Please enter a disk name", severity="error")
                return
            
            try:
                size_gb = float(size)
                if size_gb <= 0:
                    raise ValueError()
                size_mb = int(size_gb * 1024)
            except ValueError:
                self.notify("Please enter a valid size in GB", severity="error")
                return
            
            self.dismiss({"name": name, "size": size_mb})
        else:
            self.dismiss(None)
    
    def action_cancel(self) -> None:
        self.dismiss(None)


class AttachDiskScreen(Screen):
    """Modal for attaching an existing disk."""
    
    CSS = """
    AttachDiskScreen {
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
    
    .path-line {
        color: $text-muted;
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
        self.selected_path = None
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static(f"Attach Disk to {self.vm.name}", classes="title")
            yield Static("\nSelect disk file to attach:")
            yield Static("No file selected", id="path-display", classes="path-line")
            yield Button("Browse...", variant="default", id="browse-btn")
            with Horizontal(id="buttons"):
                yield Button("Attach", variant="primary", id="attach-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse-btn":
            result = await self.app.push_screen_wait(FileBrowser())
            if result:
                self.selected_path = result
                # Shorten path for display
                display_path = result
                if len(result) > 50:
                    display_path = "..." + result[-47:]
                self.query_one("#path-display", Static).update(display_path)
        elif event.button.id == "attach-btn":
            if not self.selected_path:
                self.notify("Please select a disk file", severity="error")
                return
            
            self.dismiss({"path": self.selected_path})
        else:
            self.dismiss(None)
    
    def action_cancel(self) -> None:
        self.dismiss(None)


class DetachDiskScreen(Screen):
    """Modal for confirming disk detachment."""
    
    CSS = """
    DetachDiskScreen {
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
    
    def __init__(self, disk_path: str):
        super().__init__()
        self.disk_path = disk_path
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Detach Disk", classes="title")
            # Shorten path for display
            display_path = self.disk_path
            if len(self.disk_path) > 60:
                display_path = "..." + self.disk_path[-57:]
            yield Static(f"\nDetach disk:\n{display_path}?")
            yield Static("\nThe disk file will not be deleted.")
            with Horizontal(id="buttons"):
                yield Button("Detach", variant="error", id="detach-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "detach-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_cancel(self) -> None:
        self.dismiss(False)


class DiskScreen(Screen):
    """Screen for managing VM disks."""
    
    CSS = """
    DiskScreen {
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
    
    #disk-table {
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
    """
    
    BINDINGS = [
        Binding("escape", "close", "Close", priority=True),
        Binding("n", "create_disk", "New Disk"),
        Binding("a", "attach_disk", "Attach"),
        Binding("d", "detach_disk", "Detach"),
    ]
    
    def __init__(self, vm: VM, vbox: VBoxManager):
        super().__init__()
        self.vm = vm
        self.vbox = vbox
        self.disks = []
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="container"):
            yield Static(f"Disks: {self.vm.name}", id="title")
            table = DataTable(id="disk-table", cursor_type="row")
            table.add_columns("Controller", "Port", "Device", "Size", "Path")
            yield table
            with Horizontal(id="buttons"):
                yield Button("New Disk (n)", variant="primary", id="new-btn")
                yield Button("Attach Existing (a)", variant="success", id="attach-btn")
                yield Button("Detach (d)", variant="error", id="detach-btn")
                yield Button("Close (Esc)", variant="default", id="close-btn")
        yield Footer()
    
    async def on_mount(self) -> None:
        self.refresh_disks()
    
    @work
    async def refresh_disks(self) -> None:
        """Refresh the disk list."""
        table = self.query_one("#disk-table", DataTable)
        table.clear()
        
        self.disks = await self.run_in_thread(self.vbox.list_disks, self.vm)
        
        if not self.disks:
            table.add_row("", "", "", "No disks attached", "")
        else:
            for disk in self.disks:
                path = disk.get("path", "")
                # Shorten path for display
                display_path = path
                if len(path) > 50:
                    display_path = "..." + path[-47:]
                
                table.add_row(
                    disk.get("controller", ""),
                    disk.get("port", ""),
                    disk.get("device", ""),
                    disk.get("size", ""),
                    display_path
                )
    
    def get_selected_disk(self):
        """Get the currently selected disk."""
        table = self.query_one("#disk-table", DataTable)
        if not self.disks or table.cursor_row >= len(self.disks):
            return None
        return self.disks[table.cursor_row]
    
    def action_create_disk(self) -> None:
        """Create a new disk."""
        if self.vm.is_running:
            self.notify("Power off the VM before managing disks", severity="warning")
            return
        self._create_disk_worker()
    
    @work
    async def _create_disk_worker(self) -> None:
        """Worker to create a new disk."""
        create_screen = CreateDiskScreen(self.vm, self.vbox)
        result = await self.app.push_screen_wait(create_screen)
        
        if result:
            try:
                # Get VM folder
                vm_info = await self.run_in_thread(self.vbox.get_vm_info, self.vm)
                vm_folder = os.path.dirname(vm_info.get("CfgFile", ""))
                
                if not vm_folder:
                    vm_folder = self.vbox.get_default_machine_folder()
                    vm_folder = os.path.join(vm_folder, self.vm.name)
                
                disk_path = os.path.join(vm_folder, result["name"])
                
                self.notify(f"Creating {result['size'] // 1024}GB disk...")
                await self.run_in_thread(
                    self.vbox.create_disk,
                    disk_path,
                    result["size"],
                    "VDI"
                )
                
                # Find next available port on SATA Controller
                used_ports = set()
                for disk in self.disks:
                    if disk.get("controller") == "SATA Controller":
                        used_ports.add(int(disk.get("port", 0)))
                
                next_port = 0
                while next_port in used_ports:
                    next_port += 1
                
                # Attach the new disk
                self.notify(f"Attaching disk to port {next_port}...")
                await self.run_in_thread(
                    self.vbox.attach_disk,
                    self.vm,
                    "SATA Controller",
                    next_port,
                    0,
                    disk_path
                )
                
                self.notify("Disk created and attached successfully", severity="information")
                self.refresh_disks()
            except Exception as e:
                self.notify(f"Failed to create disk: {e}", severity="error")
    
    def action_attach_disk(self) -> None:
        """Attach an existing disk."""
        if self.vm.is_running:
            self.notify("Power off the VM before managing disks", severity="warning")
            return
        self._attach_disk_worker()
    
    @work
    async def _attach_disk_worker(self) -> None:
        """Worker to attach an existing disk."""
        attach_screen = AttachDiskScreen(self.vm, self.vbox)
        result = await self.app.push_screen_wait(attach_screen)
        
        if result:
            try:
                # Find next available port on SATA Controller
                used_ports = set()
                for disk in self.disks:
                    if disk.get("controller") == "SATA Controller":
                        used_ports.add(int(disk.get("port", 0)))
                
                next_port = 0
                while next_port in used_ports:
                    next_port += 1
                
                self.notify(f"Attaching disk to port {next_port}...")
                await self.run_in_thread(
                    self.vbox.attach_disk,
                    self.vm,
                    "SATA Controller",
                    next_port,
                    0,
                    result["path"]
                )
                self.notify("Disk attached successfully", severity="information")
                self.refresh_disks()
            except Exception as e:
                self.notify(f"Failed to attach disk: {e}", severity="error")
    
    def action_detach_disk(self) -> None:
        """Detach the selected disk."""
        if self.vm.is_running:
            self.notify("Power off the VM before managing disks", severity="warning")
            return
            
        disk = self.get_selected_disk()
        if not disk:
            self.notify("No disk selected", severity="warning")
            return
        
        self._detach_disk_worker(disk)
    
    @work
    async def _detach_disk_worker(self, disk: dict) -> None:
        """Worker to detach a disk."""
        detach_screen = DetachDiskScreen(disk.get("path", "Unknown"))
        result = await self.app.push_screen_wait(detach_screen)
        
        if result:
            try:
                self.notify("Detaching disk...")
                await self.run_in_thread(
                    self.vbox.detach_disk,
                    self.vm,
                    disk["controller"],
                    int(disk["port"]),
                    int(disk["device"])
                )
                self.notify("Disk detached successfully", severity="information")
                self.refresh_disks()
            except Exception as e:
                self.notify(f"Failed to detach disk: {e}", severity="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "new-btn":
            self.action_create_disk()
        elif event.button.id == "attach-btn":
            self.action_attach_disk()
        elif event.button.id == "detach-btn":
            self.action_detach_disk()
        elif event.button.id == "close-btn":
            self.action_close()
    
    def action_close(self) -> None:
        self.dismiss()
    
    async def run_in_thread(self, func, *args):
        """Run a blocking function in a thread."""
        import asyncio
        return await asyncio.to_thread(func, *args)
