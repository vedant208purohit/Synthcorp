from abc import ABC, abstractmethod


class ModernControlInterface:
    """Modern control interface for new machines"""
    
    def start(self):
        """Start the machine"""
        print("Starting machine with modern control interface")
        return True
    
    def stop(self):
        """Stop the machine"""
        print("Stopping machine with modern control interface")
        return True
    
    def diagnose(self):
        """Run diagnostics"""
        print("Running diagnostics with modern control interface")
        return {"status": "operational"}


class LegacyMachine:
    """Legacy machine with incompatible interface"""
    
    def __init__(self, machine_id, name):
        self.machine_id = machine_id
        self.name = name
        self.running = False
    
    def power_on(self):
        """Legacy method for starting the machine"""
        print(f"Powering on legacy machine {self.name}")
        self.running = True
    
    def power_off(self):
        """Legacy method for stopping the machine"""
        print(f"Powering off legacy machine {self.name}")
        self.running = False
    
    def check_status(self):
        """Legacy method for checking machine status"""
        status = "running" if self.running else "stopped"
        print(f"Legacy machine {self.name} status: {status}")
        return status


class MachineControlInterface(ABC):
    """Abstract interface for machine control"""
    
    @abstractmethod
    def start_operation(self):
        pass
    
    @abstractmethod
    def stop_operation(self):
        pass
    
    @abstractmethod
    def run_diagnostics(self):
        pass


class LegacyMachineAdapter(MachineControlInterface):
    """Adapter Pattern implementation for legacy machines"""
    
    def __init__(self, legacy_machine):
        self.legacy_machine = legacy_machine
        self.machine_id = legacy_machine.machine_id
        self.name = f"Adapted-{legacy_machine.name}"
    
    def start_operation(self):
        """Adapt start operation to legacy power_on method"""
        print(f"Adapter: starting operation for {self.name}")
        self.legacy_machine.power_on()
        return True
    
    def stop_operation(self):
        """Adapt stop operation to legacy power_off method"""
        print(f"Adapter: stopping operation for {self.name}")
        self.legacy_machine.power_off()
        return True
    
    def run_diagnostics(self):
        """Adapt run_diagnostics to legacy check_status method"""
        print(f"Adapter: running diagnostics for {self.name}")
        status = self.legacy_machine.check_status()
        return {"legacy_status": status}
