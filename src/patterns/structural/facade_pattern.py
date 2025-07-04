class ManufacturingSystemFacade:
    """Facade Pattern implementation for providing a simplified interface"""
    
    def __init__(self, central_control_system):
        self.central_control = central_control_system
    
    def register_machine(self, machine):
        """Register a new machine with the system"""
        self.central_control.register_machine(machine)
    
    def get_machine_status(self, machine_id):
        """Get the status of a specific machine"""
        machine = self.central_control.get_machine(machine_id)
        if machine:
            return {
                "id": machine.machine_id,
                "name": machine.name,
                "state": machine.state.name,
                "performance": machine.get_performance_data()
            }
        return {"error": f"Machine {machine_id} not found"}
    
    def get_all_machine_statuses(self):
        """Get status of all machines"""
        statuses = {}
        for machine in self.central_control.get_all_machines():
            statuses[machine.machine_id] = {
                "name": machine.name,
                "state": machine.state.name,
                "performance": machine.get_performance_data()
            }
        return statuses
    
    def start_production_order(self, order_id):
        """Start a specific production order"""
        return self.central_control.start_production(order_id)
    
    def stop_current_production(self):
        """Stop the currently running production"""
        return self.central_control.stop_production()
    
    def check_inventory(self, item=None):
        """Check inventory levels"""
        if item:
            return {item: self.central_control.get_inventory_level(item)}
        return self.central_control.get_all_inventory()
    
    def check_safety_status(self):
        """Check if all safety protocols are being followed"""
        results = self.central_control.check_safety_protocols()
        return {"safe": all(result[1] for result in results), "protocols": len(results)}
    
    def trigger_emergency_shutdown(self):
        """Trigger emergency shutdown of all systems"""
        self.central_control.emergency_shutdown()
        return {"status": "emergency_shutdown_completed"}
