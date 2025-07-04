class InventorySystem:
    """System for managing inventory and supplies"""
    
    def __init__(self, central_control):
        self.central_control = central_control
        self.inventory = {}
        self.reorder_levels = {}
        self.on_order = {}
        self.suppliers = {}
    
    def add_item(self, item_id, name, quantity, reorder_level=10, supplier=None):
        """Add a new item to inventory"""
        self.inventory[item_id] = {
            'name': name,
            'quantity': quantity
        }
        self.reorder_levels[item_id] = reorder_level
        
        if supplier:
            self.suppliers[item_id] = supplier
            
        print(f"Added {quantity} units of {name} (ID: {item_id}) to inventory")
        
        # Update central control system inventory
        self.central_control.update_inventory(item_id, quantity)
    
    def remove_item(self, item_id, quantity):
        """Remove items from inventory"""
        if item_id not in self.inventory:
            print(f"Error: Item {item_id} not in inventory")
            return False
        
        if self.inventory[item_id]['quantity'] < quantity:
            print(f"Error: Insufficient quantity of {self.inventory[item_id]['name']}")
            return False
        
        self.inventory[item_id]['quantity'] -= quantity
        print(f"Removed {quantity} units of {self.inventory[item_id]['name']} from inventory")
        
        # Check if reorder needed
        self._check_reorder_level(item_id)
        
        # Update central control system inventory
        self.central_control.update_inventory(item_id, -quantity)
        return True
    
    def get_item_quantity(self, item_id):
        """Get current quantity of an item"""
        if item_id in self.inventory:
            return self.inventory[item_id]['quantity']
        return 0
    
    def set_reorder_level(self, item_id, level):
        """Set reorder level for an item"""
        if item_id not in self.inventory:
            print(f"Error: Item {item_id} not in inventory")
            return False
        
        self.reorder_levels[item_id] = level
        print(f"Reorder level for {self.inventory[item_id]['name']} set to {level}")
        
        # Check if reorder needed after changing level
        self._check_reorder_level(item_id)
        return True
    
    def _check_reorder_level(self, item_id):
        """Check if item needs to be reordered"""
        if item_id not in self.reorder_levels:
            return
            
        current_quantity = self.inventory[item_id]['quantity']
        reorder_level = self.reorder_levels[item_id]
        
        if current_quantity <= reorder_level and item_id not in self.on_order:
            print(f"WARNING: Low inventory for {self.inventory[item_id]['name']}")
            self._place_order(item_id)
    
    def _place_order(self, item_id):
        """Place an order for more inventory"""
        # Default order quantity is twice the reorder level
        order_quantity = self.reorder_levels[item_id] * 2
        
        print(f"Placing order for {order_quantity} units of {self.inventory[item_id]['name']}")
        self.on_order[item_id] = order_quantity
        
        if item_id in self.suppliers:
            print(f"Order sent to supplier: {self.suppliers[item_id]}")
        else:
            print("No supplier defined for this item")
            
        import threading
        threading.Timer(5.0, self._receive_order, args=[item_id, order_quantity]).start()
    
    def _receive_order(self, item_id, quantity):
        """Receive an order (simulated)"""
        if item_id in self.inventory:
            self.inventory[item_id]['quantity'] += quantity
            print(f"Received {quantity} units of {self.inventory[item_id]['name']}")
            
            # Update central control
            self.central_control.update_inventory(item_id, quantity)
            
            # Remove from on-order
            if item_id in self.on_order:
                del self.on_order[item_id]
    
    def get_inventory_report(self):
        """Generate inventory report"""
        report = []
        for item_id, details in self.inventory.items():
            report.append({
                'id': item_id,
                'name': details['name'],
                'quantity': details['quantity'],
                'reorder_level': self.reorder_levels.get(item_id, 0),
                'on_order': self.on_order.get(item_id, 0),
                'supplier': self.suppliers.get(item_id, 'None')
            })
        return report


class SafetyProtocol:
    """Safety protocol implementation"""
    
    def __init__(self, name, condition_func, severity="HIGH"):
        self.name = name
        self.condition_func = condition_func
        self.severity = severity
        self.violations = 0
    
    def check(self):
        """Check if safety protocol is being followed"""
        result = self.condition_func()
        if not result:
            self.violations += 1
            print(f"SAFETY VIOLATION: {self.name} - Severity: {self.severity}")
        return result
    
    def get_violations(self):
        """Get number of violations of this protocol"""
        return self.violations
    
    def __str__(self):
        return f"SafetyProtocol({self.name}, Severity: {self.severity})"
