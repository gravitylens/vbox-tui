"""VirtualBox management module using VBoxManage CLI."""
import subprocess
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class VM:
    """Represents a VirtualBox virtual machine."""
    name: str
    uuid: str
    state: str
    memory: int = 0
    cpus: int = 0
    os_type: str = ""
    
    @property
    def is_running(self) -> bool:
        return self.state == "running"
    
    @property
    def status_icon(self) -> str:
        """Return a visual indicator for VM state."""
        if self.state == "running":
            return "▶"
        elif self.state == "paused":
            return "⏸"
        elif self.state == "saved":
            return "💾"
        elif self.state == "poweroff":
            return "⏹"
        else:
            return "○"


class VBoxManager:
    """Interface to VirtualBox via VBoxManage CLI."""
    
    def __init__(self):
        self._check_vboxmanage()
    
    def _check_vboxmanage(self):
        """Verify VBoxManage is available."""
        try:
            subprocess.run(
                ["VBoxManage", "--version"],
                capture_output=True,
                check=True,
                text=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("VBoxManage not found. Is VirtualBox installed?")
    
    def _run_command(self, args: List[str], timeout: int = 30) -> str:
        """Run a VBoxManage command and return output."""
        try:
            result = subprocess.run(
                ["VBoxManage"] + args,
                capture_output=True,
                check=True,
                text=True,
                timeout=timeout
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"VBoxManage command timed out after {timeout} seconds")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"VBoxManage error: {e.stderr}")
    
    def list_vms(self) -> List[VM]:
        """List all VMs with their current state."""
        vms = []
        
        # Get all VMs with their UUIDs
        output = self._run_command(["list", "vms"])
        vm_pattern = re.compile(r'"(.+?)"\s+\{(.+?)\}')
        
        for line in output.splitlines():
            match = vm_pattern.match(line)
            if match:
                name, uuid = match.groups()
                state = self._get_vm_state(uuid)
                vm = VM(name=name, uuid=uuid, state=state)
                
                # Get additional info
                try:
                    vm.memory = self._get_vm_memory(uuid)
                    vm.cpus = self._get_vm_cpus(uuid)
                    vm.os_type = self._get_vm_os_type(uuid)
                except:
                    pass  # If we can't get info, continue with defaults
                
                vms.append(vm)
        
        return vms
    
    def _get_vm_state(self, uuid: str) -> str:
        """Get the current state of a VM."""
        try:
            output = self._run_command(["showvminfo", uuid, "--machinereadable"])
            for line in output.splitlines():
                if line.startswith("VMState="):
                    state = line.split("=", 1)[1].strip('"')
                    return state
        except:
            pass
        return "unknown"
    
    def _get_vm_memory(self, uuid: str) -> int:
        """Get VM memory in MB."""
        try:
            output = self._run_command(["showvminfo", uuid, "--machinereadable"])
            for line in output.splitlines():
                if line.startswith("memory="):
                    return int(line.split("=", 1)[1])
        except:
            pass
        return 0
    
    def _get_vm_cpus(self, uuid: str) -> int:
        """Get number of CPUs."""
        try:
            output = self._run_command(["showvminfo", uuid, "--machinereadable"])
            for line in output.splitlines():
                if line.startswith("cpus="):
                    return int(line.split("=", 1)[1])
        except:
            pass
        return 0
    
    def _get_vm_os_type(self, uuid: str) -> str:
        """Get OS type."""
        try:
            output = self._run_command(["showvminfo", uuid, "--machinereadable"])
            for line in output.splitlines():
                if line.startswith("ostype="):
                    return line.split("=", 1)[1].strip('"')
        except:
            pass
        return ""
    
    def start_vm(self, vm: VM, headless: bool = True) -> None:
        """Start a VM."""
        vm_type = "headless" if headless else "gui"
        self._run_command(["startvm", vm.uuid, "--type", vm_type])
    
    def stop_vm(self, vm: VM, force: bool = False) -> None:
        """Stop a VM (ACPI shutdown or poweroff)."""
        if force:
            self._run_command(["controlvm", vm.uuid, "poweroff"])
        else:
            self._run_command(["controlvm", vm.uuid, "acpipowerbutton"])
    
    def pause_vm(self, vm: VM) -> None:
        """Pause a running VM."""
        self._run_command(["controlvm", vm.uuid, "pause"])
    
    def resume_vm(self, vm: VM) -> None:
        """Resume a paused VM."""
        self._run_command(["controlvm", vm.uuid, "resume"])
    
    def save_state(self, vm: VM) -> None:
        """Save VM state and stop it."""
        self._run_command(["controlvm", vm.uuid, "savestate"])
    
    def reset_vm(self, vm: VM) -> None:
        """Reset a VM (hard reboot)."""
        self._run_command(["controlvm", vm.uuid, "reset"])
    
    def show_vm(self, vm: VM) -> None:
        """Show/reconnect to a VM's GUI window."""
        # For running VMs, this will open/reconnect to the GUI
        # VBoxManage showvminfo can be used with --details to show the window
        # But the proper way is to use VBoxManage controlvm <vm> show
        # However, if the VM is already running, we can use startvm with type gui
        # which will show the existing VM window
        if vm.is_running or vm.state == "paused":
            # For already running VMs, VBoxHeadless or gui frontend will reconnect
            self._run_command(["startvm", vm.uuid, "--type", "separate"])
        else:
            # Start the VM with GUI
            self._run_command(["startvm", vm.uuid, "--type", "gui"])
    
    def get_vm_info(self, vm: VM) -> Dict[str, str]:
        """Get detailed VM information."""
        output = self._run_command(["showvminfo", vm.uuid, "--machinereadable"])
        info = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                info[key] = value.strip('"')
        return info
    
    def modify_vm(self, vm: VM, setting: str, value: str) -> None:
        """Modify a VM setting."""
        self._run_command(["modifyvm", vm.uuid, f"--{setting}", value])
        # If setting network to bridged, also set the bridge adapter
        if setting == "nic1" and value.lower() == "bridged":
            interfaces = self.get_bridged_interfaces()
            if interfaces:
                # Prefer physical interfaces (eno, eth, wlan) over virtual ones
                physical = [i for i in interfaces if i.startswith(("eno", "eth", "wlan", "enp"))]
                bridge_if = physical[0] if physical else interfaces[0]
                self._run_command(["modifyvm", vm.uuid, "--bridgeadapter1", bridge_if])
    
    def get_guest_ip(self, vm: VM) -> Optional[str]:
        """Get the guest IP address from VirtualBox guest properties.
        
        Requires VirtualBox Guest Additions to be installed in the guest.
        Returns None if Guest Additions is not installed or no IP is available.
        """
        try:
            output = self._run_command(["guestproperty", "get", vm.uuid, "/VirtualBox/GuestInfo/Net/0/V4/IP"])
            for line in output.splitlines():
                if "Value:" in line:
                    return line.split(":", 1)[1].strip()
        except:
            pass
        return None
    
    def get_bridged_interfaces(self) -> List[str]:
        """Get list of available bridged network interfaces."""
        output = self._run_command(["list", "bridgedifs"])
        interfaces = []
        for line in output.splitlines():
            if line.startswith("Name:"):
                interface = line.split(":", 1)[1].strip()
                interfaces.append(interface)
        return interfaces
    
    def get_default_machine_folder(self) -> str:
        """Get the default machine folder setting."""
        output = self._run_command(["list", "systemproperties"])
        for line in output.splitlines():
            if "Default machine folder:" in line:
                return line.split(":", 1)[1].strip()
        return ""
    
    def set_default_machine_folder(self, path: str) -> None:
        """Set the default machine folder."""
        self._run_command(["setproperty", "machinefolder", path])
    
    def attach_iso(self, vm: VM, iso_path: str = None) -> None:
        """Attach or detach an ISO to/from the DVD drive.
        
        Args:
            vm: The VM to modify
            iso_path: Path to ISO file, or None/empty to eject
        """
        import os
        
        # Determine the medium parameter
        if iso_path and os.path.exists(iso_path):
            medium = iso_path
        else:
            medium = "emptydrive"
        
        # Attach to port 1 (DVD drive) on SATA Controller
        self._run_command([
            "storageattach", vm.uuid,
            "--storagectl", "SATA Controller",
            "--port", "1",
            "--device", "0",
            "--type", "dvddrive",
            "--medium", medium
        ])
    
    def create_vm(self, name: str, ostype: str, memory: int, cpus: int, vram: int, disk_size: int, 
                  iso_path: str = None, network_type: str = "nat", description: str = None,
                  cpuexecutioncap: int = 100, chipset: str = "piix3", firmware: str = "bios",
                  graphics_controller: str = "VMSVGA", accelerate3d: str = "off") -> None:
        """Create a new VM with comprehensive configuration."""
        # Create the VM
        output = self._run_command(["createvm", "--name", name, "--ostype", ostype, "--register"])
        
        # Extract UUID from output
        uuid_pattern = re.compile(r'UUID:\s+(.+)')
        match = uuid_pattern.search(output)
        if not match:
            raise RuntimeError("Could not extract VM UUID from createvm output")
        
        uuid = match.group(1).strip()
        
        try:
            # Configure basic settings
            self._run_command(["modifyvm", uuid, "--memory", str(memory)])
            self._run_command(["modifyvm", uuid, "--cpus", str(cpus)])
            self._run_command(["modifyvm", uuid, "--cpuexecutioncap", str(cpuexecutioncap)])
            self._run_command(["modifyvm", uuid, "--vram", str(vram)])
            
            # System settings
            self._run_command(["modifyvm", uuid, "--chipset", chipset])
            self._run_command(["modifyvm", uuid, "--firmware", firmware])
            
            # Graphics settings
            self._run_command(["modifyvm", uuid, "--graphicscontroller", graphics_controller])
            self._run_command(["modifyvm", uuid, "--accelerate3d", accelerate3d])
            
            # Description
            if description:
                self._run_command(["modifyvm", uuid, "--description", description])
            
            # Boot order
            self._run_command(["modifyvm", uuid, "--boot1", "disk"])
            self._run_command(["modifyvm", uuid, "--boot2", "dvd"])
            self._run_command(["modifyvm", uuid, "--boot3", "none"])
            self._run_command(["modifyvm", uuid, "--boot4", "none"])
            
            # Add network adapter
            if network_type and network_type.lower() != "none":
                self._run_command(["modifyvm", uuid, "--nic1", network_type.lower()])
                # For bridged network, set the bridge adapter to first available interface
                if network_type.lower() == "bridged":
                    interfaces = self.get_bridged_interfaces()
                    if interfaces:
                        # Prefer physical interfaces (eno, eth, wlan) over virtual ones
                        physical = [i for i in interfaces if i.startswith(("eno", "eth", "wlan", "enp"))]
                        bridge_if = physical[0] if physical else interfaces[0]
                        self._run_command(["modifyvm", uuid, "--bridgeadapter1", bridge_if])
            
            # Create storage controller
            self._run_command([
                "storagectl", uuid,
                "--name", "SATA Controller",
                "--add", "sata",
                "--controller", "IntelAhci",
                "--portcount", "2"
            ])
            
            # Get the VM's folder to place the disk in the right location
            vm_info = self.get_vm_info(VM(name=name, uuid=uuid, state="poweroff"))
            vm_folder = vm_info.get("CfgFile", "").rsplit("/", 1)[0] if "CfgFile" in vm_info else ""
            
            # Create and attach hard disk with full path
            if vm_folder:
                disk_path = f"{vm_folder}/{name}.vdi"
            else:
                disk_path = f"{name}.vdi"
            
            self._run_command([
                "createmedium", "disk",
                "--filename", disk_path,
                "--size", str(disk_size),
                "--format", "VDI",
                "--variant", "Standard"
            ])
            
            self._run_command([
                "storageattach", uuid,
                "--storagectl", "SATA Controller",
                "--port", "0",
                "--device", "0",
                "--type", "hdd",
                "--medium", disk_path
            ])
            
            # Attach ISO if provided
            if iso_path:
                import os
                if os.path.exists(iso_path):
                    self._run_command([
                        "storageattach", uuid,
                        "--storagectl", "SATA Controller",
                        "--port", "1",
                        "--device", "0",
                        "--type", "dvddrive",
                        "--medium", iso_path
                    ])
                else:
                    # Still create the VM with empty DVD drive
                    self._run_command([
                        "storageattach", uuid,
                        "--storagectl", "SATA Controller",
                        "--port", "1",
                        "--device", "0",
                        "--type", "dvddrive",
                        "--medium", "emptydrive"
                    ])
            else:
                # Add empty DVD drive
                self._run_command([
                    "storageattach", uuid,
                    "--storagectl", "SATA Controller",
                    "--port", "1",
                    "--device", "0",
                    "--type", "dvddrive",
                    "--medium", "emptydrive"
                ])
            
        except Exception as e:
            # If configuration fails, try to unregister and delete the VM
            try:
                self._run_command(["unregistervm", uuid, "--delete"])
            except:
                pass
            raise RuntimeError(f"Failed to configure VM: {e}")
    
    def delete_vm(self, vm: VM, delete_files: bool = True) -> None:
        """Delete a VM and optionally its files."""
        if delete_files:
            self._run_command(["unregistervm", vm.uuid, "--delete"])
        else:
            self._run_command(["unregistervm", vm.uuid])
    
    def list_snapshots(self, vm: VM) -> List[Dict[str, str]]:
        """List all snapshots for a VM."""
        try:
            output = self._run_command(["snapshot", vm.uuid, "list", "--machinereadable"])
            snapshots = []
            
            # Parse the output to extract snapshot information
            current_snapshot = {}
            for line in output.splitlines():
                if line.startswith("SnapshotName"):
                    match = re.match(r'SnapshotName(?:-(\d+))?="(.+)"', line)
                    if match:
                        idx = match.group(1) or "0"
                        name = match.group(2)
                        if idx not in [s.get("idx") for s in snapshots]:
                            snapshots.append({"idx": idx, "name": name})
                        else:
                            for s in snapshots:
                                if s["idx"] == idx:
                                    s["name"] = name
                                    break
                elif line.startswith("SnapshotUUID"):
                    match = re.match(r'SnapshotUUID(?:-(\d+))?="(.+)"', line)
                    if match:
                        idx = match.group(1) or "0"
                        uuid = match.group(2)
                        for s in snapshots:
                            if s["idx"] == idx:
                                s["uuid"] = uuid
                                break
                elif line.startswith("CurrentSnapshotUUID"):
                    match = re.match(r'CurrentSnapshotUUID="(.+)"', line)
                    if match:
                        current_uuid = match.group(1)
                        for s in snapshots:
                            if s.get("uuid") == current_uuid:
                                s["current"] = True
            
            return snapshots
        except (subprocess.CalledProcessError, RuntimeError):
            # No snapshots exist
            return []
    
    def take_snapshot(self, vm: VM, name: str, description: str = "") -> None:
        """Take a snapshot of a VM."""
        cmd = ["snapshot", vm.uuid, "take", name]
        if description:
            cmd.extend(["--description", description])
        self._run_command(cmd)
    
    def restore_snapshot(self, vm: VM, snapshot_uuid: str) -> None:
        """Restore a VM to a snapshot."""
        self._run_command(["snapshot", vm.uuid, "restore", snapshot_uuid])
    
    def delete_snapshot(self, vm: VM, snapshot_uuid: str) -> None:
        """Delete a snapshot."""
        self._run_command(["snapshot", vm.uuid, "delete", snapshot_uuid])
    
    def list_storage_controllers(self, vm: VM) -> List[Dict[str, str]]:
        """List storage controllers for a VM."""
        output = self._run_command(["showvminfo", vm.uuid, "--machinereadable"])
        controllers = []
        
        for line in output.splitlines():
            if line.startswith("storagecontrollername"):
                match = re.match(r'storagecontrollername(\d+)="(.+)"', line)
                if match:
                    idx = match.group(1)
                    name = match.group(2)
                    controllers.append({"idx": idx, "name": name})
            elif line.startswith("storagecontrollertype"):
                match = re.match(r'storagecontrollertype(\d+)="(.+)"', line)
                if match:
                    idx = match.group(1)
                    ctrl_type = match.group(2)
                    for ctrl in controllers:
                        if ctrl["idx"] == idx:
                            ctrl["type"] = ctrl_type
        
        return controllers
    
    def list_disks(self, vm: VM) -> List[Dict[str, str]]:
        """List all hard disk attachments for a VM (excludes DVD drives)."""
        output = self._run_command(["showvminfo", vm.uuid, "--machinereadable"])
        disks = []
        
        # First pass: collect all storage attachment info
        for line in output.splitlines():
            # Look for lines like: "SATA-0-0"="/path/to/disk.vdi"
            # or "IDE-1-0"="/path/to/disk.vdi"
            if line.startswith('"') and '="' in line:
                match = re.match(r'"([A-Za-z ]+)-(\d+)-(\d+)"="(.+)"', line)
                if match:
                    controller = match.group(1)
                    port = match.group(2)
                    device = match.group(3)
                    path = match.group(4)
                    
                    # Skip empty, "none", or DVD/ISO files
                    if not path or path.lower() == "none":
                        continue
                    if path.lower().endswith('.iso'):
                        continue
                    
                    # Check if this attachment is a hard disk by looking at the type
                    type_key = f'"{controller}-{port}-{device}-type"'
                    is_hdd = False
                    for type_line in output.splitlines():
                        if type_line.startswith(type_key):
                            if '"hdd"' in type_line.lower():
                                is_hdd = True
                            break
                    
                    # Only add if it's explicitly a hard disk or we can't determine the type
                    # (assume it's a disk if it has a disk-like extension)
                    disk_extensions = ['.vdi', '.vmdk', '.vhd', '.qcow', '.qcow2', '.img']
                    has_disk_ext = any(path.lower().endswith(ext) for ext in disk_extensions)
                    
                    if is_hdd or has_disk_ext:
                        disks.append({
                            "controller": controller,
                            "port": port,
                            "device": device,
                            "path": path
                        })
        
        # Get size info for each disk
        for disk in disks:
            try:
                medium_output = self._run_command(["showmediuminfo", "disk", disk["path"]])
                for line in medium_output.splitlines():
                    if line.startswith("Capacity:"):
                        disk["size"] = line.split(":", 1)[1].strip()
                        break
            except:
                disk["size"] = "Unknown"
        
        return disks
    
    def attach_disk(self, vm: VM, controller: str, port: int, device: int, disk_path: str) -> None:
        """Attach a disk to a VM."""
        self._run_command([
            "storageattach", vm.uuid,
            "--storagectl", controller,
            "--port", str(port),
            "--device", str(device),
            "--type", "hdd",
            "--medium", disk_path
        ])
    
    def detach_disk(self, vm: VM, controller: str, port: int, device: int) -> None:
        """Detach a disk from a VM."""
        self._run_command([
            "storageattach", vm.uuid,
            "--storagectl", controller,
            "--port", str(port),
            "--device", str(device),
            "--type", "hdd",
            "--medium", "none"
        ])
    
    def create_disk(self, path: str, size_mb: int, format: str = "VDI") -> None:
        """Create a new virtual disk."""
        self._run_command([
            "createmedium", "disk",
            "--filename", path,
            "--size", str(size_mb),
            "--format", format
        ])

