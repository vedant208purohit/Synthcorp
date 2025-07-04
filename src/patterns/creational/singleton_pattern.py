class CentralControlSystem:
    """Singleton Pattern implementation for the central control system"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            print("Creating new instance of Central Control System")
            cls._instance = super(CentralControlSystem, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()
        return cls._instance

    
    def _initialize(self):
        """Initialize the central control system"""
        self._machines = {}
        self._production_orders = []
        self._active_production = None
        self._inventory = {}
        self._safety_protocols = []
        print("Central Control System initialized")
    
    def register_machine(self, machine):
        """Register a machine with the central control system"""
        self._machines[machine.machine_id] = machine
        print(f"Machine {machine.name} registered with ID {machine.machine_id}")
    
    def get_machine(self, machine_id):
        """Get a machine by ID"""
        return self._machines.get(machine_id)
    
    def get_all_machines(self):
        """Get all registered machines"""
        return list(self._machines.values())
    
    def add_production_order(self, order):
        """Add a production order to the queue"""
        self._production_orders.append(order)
        print(f"Production order added: {order.order_id}")
    
    def get_next_production_order(self):
        """Get the next production order in the queue"""
        if self._production_orders:
            return self._production_orders[0]
        return None
    
    def start_production(self, order_id):
        """Start production for a specific order"""
        for order in self._production_orders:
            if order.order_id == order_id:
                self._active_production = order
                order.start_production()
                print(f"Production started for order {order_id}")
                return True
        print(f"Order {order_id} not found")
        return False
    
    def stop_production(self):
        """Stop current production"""
        if self._active_production:
            order_id = self._active_production.order_id
            self._active_production.stop_production()
            self._active_production = None
            print(f"Production stopped for order {order_id}")
            return True
        print("No active production to stop")
        return False
    
    def update_inventory(self, item, quantity):
        """Update inventory levels"""
        if item in self._inventory:
            self._inventory[item] += quantity
        else:
            self._inventory[item] = quantity
        print(f"Inventory updated: {item} = {self._inventory[item]}")
    
    def get_inventory_level(self, item):
        """Get current inventory level for an item"""
        return self._inventory.get(item, 0)
    
    def get_all_inventory(self):
        """Get complete inventory status"""
        return self._inventory.copy()
    
    def add_safety_protocol(self, protocol):
        """Add a safety protocol"""
        self._safety_protocols.append(protocol)
        print(f"Safety protocol added: {protocol}")
    
    def check_safety_protocols(self):
        """Check if safety protocols are being followed"""
        results = []
        for protocol in self._safety_protocols:
            result = protocol.check()
            results.append((protocol, result))
            if not result:
                print(f"Safety protocol violation: {protocol}")
        return results
    
    def emergency_shutdown(self):
        """Emergency shutdown of all machines"""
        print("EMERGENCY SHUTDOWN INITIATED")
        for machine in self._machines.values():
            machine.stop_operation()
            machine.set_state(MachineState.IDLE)
        if self._active_production:
            self._active_production.stop_production()
            self._active_production = None
        print("Emergency shutdown complete - all machines stopped")

from src.core.machine import MachineState  
