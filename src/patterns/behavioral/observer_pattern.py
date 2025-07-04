from abc import ABC, abstractmethod


class MachineObserver(ABC):
    """Observer Pattern: Abstract base class for machine observers"""
    
    @abstractmethod
    def update(self, machine, message):
        """Update method called by observed machines"""
        pass


class MaintenanceEngineer(MachineObserver):
    """Observer that monitors machines for maintenance needs"""
    
    def __init__(self, name):
        self.name = name
        self.alerts = []
        self.machine_states = {}
    
    def update(self, machine, message):
        """Receive update from observed machine"""
        print(f"[ALERT] Engineer {self.name} notified: {machine.name} - {message}")
        self.alerts.append({
            "time": self._get_timestamp(),
            "machine_id": machine.machine_id,
            "machine_name": machine.name,
            "message": message
        })
        
        # Track machine state changes
        self.machine_states[machine.machine_id] = machine.state
        
        # Check if maintenance is needed
        if "Error" in message or "error" in message or machine.state.name == "ERROR" or machine.state.name == "MAINTENANCE":
            print(f"[URGENT] Engineer {self.name} needs to check machine {machine.name} immediately!")
    
    def get_alerts(self):
        """Get all received alerts"""
        return self.alerts
    
    def get_machine_status(self, machine_id):
        """Get tracked status of a specific machine"""
        return self.machine_states.get(machine_id)
    
    def _get_timestamp(self):
        """Helper to get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ProductionManager(MachineObserver):
    """Observer that monitors production statistics"""
    
    def __init__(self, name):
        self.name = name
        self.production_stats = {}
    
    def update(self, machine, message):
        """Receive update from observed machine"""
        machine_id = machine.machine_id
        
        # Initialize stats for new machines
        if machine_id not in self.production_stats:
            self.production_stats[machine_id] = {
                "name": machine.name,
                "updates": [],
                "performance_data": {}
            }
        
        # Log the update
        self.production_stats[machine_id]["updates"].append({
            "time": self._get_timestamp(),
            "message": message
        })
        
        # Update performance data if available
        performance_data = machine.get_performance_data()
        if performance_data:
            self.production_stats[machine_id]["performance_data"] = performance_data
        
        # Only print production relevant messages (not every state change)
        if ("count" in message or "produced" in message or 
            "assembled" in message or "packaged" in message):
            print(f"[PRODUCTION] Manager {self.name} notified: {machine.name} - {message}")
    
    def get_production_stats(self):
        """Get production statistics for all machines"""
     
    def get_machine_stats(self, machine_id):
        """Get production statistics for a specific machine"""
        return self.production_stats.get(machine_id)
    
    def _get_timestamp(self):
        """Helper to get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
