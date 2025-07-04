from abc import ABC, abstractmethod


class MachineStateHandler(ABC):
    """State Pattern implementation for machine state management"""
    
    @abstractmethod
    def handle_start_request(self, machine):
        """Handle request to start the machine"""
        pass
    
    @abstractmethod
    def handle_stop_request(self, machine):
        """Handle request to stop the machine"""
        pass
    
    @abstractmethod
    def handle_maintenance_request(self, machine):
        """Handle request for maintenance"""
        pass
    
    @abstractmethod
    def handle_error(self, machine, error_message):
        """Handle error state"""
        pass


class IdleStateHandler(MachineStateHandler):
    """Handler for machines in IDLE state"""
    
    def handle_start_request(self, machine):
        """Handle start request when idle"""
        print(f"Starting {machine.name} from IDLE state")
        from core.machine import MachineState
        machine.set_state(MachineState.ACTIVE)
        return True
    
    def handle_stop_request(self, machine):
        """Handle stop request when already idle"""
        print(f"{machine.name} is already in IDLE state")
        return False
    
    def handle_maintenance_request(self, machine):
        """Handle maintenance request when idle"""
        print(f"Moving {machine.name} to MAINTENANCE state")
        from core.machine import MachineState
        machine.set_state(MachineState.MAINTENANCE)
        return True
    
    def handle_error(self, machine, error_message):
        """Handle error when idle"""
        print(f"Error in {machine.name} while IDLE: {error_message}")
        from core.machine import MachineState
        machine.set_state(MachineState.ERROR)
        return True


class ActiveStateHandler(MachineStateHandler):
    """Handler for machines in ACTIVE state"""
    
    def handle_start_request(self, machine):
        """Handle start request when already active"""
        print(f"{machine.name} is already in ACTIVE state")
        return False
    
    def handle_stop_request(self, machine):
        """Handle stop request when active"""
        print(f"Stopping {machine.name} from ACTIVE state")
        from core.machine import MachineState
        machine.set_state(MachineState.IDLE)
        return True
    
    def handle_maintenance_request(self, machine):
        """Handle maintenance request when active"""
        print(f"Cannot move {machine.name} to MAINTENANCE while ACTIVE. Stop first.")
        return False
    
    def handle_error(self, machine, error_message):
        """Handle error when active"""
        print(f"Error in {machine.name} while ACTIVE: {error_message}")
        from core.machine import MachineState
        machine.set_state(MachineState.ERROR)
        # Log error details
        machine.update_performance_data("last_error", error_message)
        return True


class MaintenanceStateHandler(MachineStateHandler):
    """Handler for machines in MAINTENANCE state"""
    
    def handle_start_request(self, machine):
        """Handle start request when in maintenance"""
        print(f"Cannot start {machine.name} while in MAINTENANCE state")
        return False
    
    def handle_stop_request(self, machine):
        """Handle stop request when in maintenance"""
        print(f"Maintenance completed for {machine.name}, returning to IDLE state")
        from core.machine import MachineState
        machine.set_state(MachineState.IDLE)
        return True
    
    def handle_maintenance_request(self, machine):
        """Handle maintenance request when already in maintenance"""
        print(f"{machine.name} is already in MAINTENANCE state")
        return False
    
    def handle_error(self, machine, error_message):
        """Handle error when in maintenance"""
        print(f"Error in {machine.name} while in MAINTENANCE: {error_message}")
        from core.machine import MachineState
        machine.set_state(MachineState.ERROR)
        # Log error details
        machine.update_performance_data("maintenance_error", error_message)
        return True


class ErrorStateHandler(MachineStateHandler):
    """Handler for machines in ERROR state"""
    
    def handle_start_request(self, machine):
        """Handle start request when in error state"""
        print(f"Cannot start {machine.name} while in ERROR state. Resolve error first.")
        return False
    
    def handle_stop_request(self, machine):
        """Handle stop request when in error state"""
        print(f"{machine.name} is already stopped due to ERROR")
        return False
    
    def handle_maintenance_request(self, machine):
        """Handle maintenance request when in error state"""
        print(f"Moving {machine.name} from ERROR to MAINTENANCE state for repairs")
        from core.machine import MachineState
        machine.set_state(MachineState.MAINTENANCE)
        return True
    
    def handle_error(self, machine, error_message):
        """Handle additional error when already in error state"""
        print(f"Additional error in {machine.name}: {error_message}")
        # Log additional error details
        machine.update_performance_data("additional_error", error_message)
        return True


class MachineStateContext:
    """Context for managing machine state transitions"""
    
    def __init__(self, machine):
        self.machine = machine
        self._states = {
            "IDLE": IdleStateHandler(),
            "ACTIVE": ActiveStateHandler(),
            "MAINTENANCE": MaintenanceStateHandler(),
            "ERROR": ErrorStateHandler()
        }
    
    def get_state_handler(self):
        """Get the appropriate handler for current state"""
        from core.machine import MachineState
        state_name = self.machine.state.name
        return self._states.get(state_name)
    
    def handle_start(self):
        """Handle start request based on current state"""
        return self.get_state_handler().handle_start_request(self.machine)
    
    def handle_stop(self):
        """Handle stop request based on current state"""
        return self.get_state_handler().handle_stop_request(self.machine)
    
    def handle_maintenance(self):
        """Handle maintenance request based on current state"""
        return self.get_state_handler().handle_maintenance_request(self.machine)
    
    def handle_error(self, error_message):
        """Handle error based on current state"""
        return self.get_state_handler().handle_error(self.machine, error_message)
