from abc import ABC, abstractmethod
from enum import Enum, auto


class MachineState(Enum):
    """State pattern implementation for machine status"""
    IDLE = auto()
    ACTIVE = auto()
    MAINTENANCE = auto()
    ERROR = auto()


class Machine(ABC):
    """Abstract base class for all machines in the factory"""
    
    def __init__(self, machine_id, name):
        self._machine_id = machine_id
        self._name = name
        self._state = MachineState.IDLE
        self._performance_data = {}
        self._observers = []
    
    @property
    def machine_id(self):
        return self._machine_id
    
    @property
    def name(self):
        return self._name
    
    @property
    def state(self):
        return self._state
    
    def set_state(self, state):
        """Change machine state and notify observers"""
        old_state = self._state
        self._state = state
        self.notify_observers(f"State changed from {old_state.name} to {state.name}")
    
    def get_performance_data(self):
        """Encapsulation of performance data"""
        return self._performance_data.copy()
    
    def update_performance_data(self, key, value):
        """Update machine performance metrics"""
        self._performance_data[key] = value
        self.notify_observers(f"Performance data updated: {key}={value}")
    
    def attach_observer(self, observer):
        """Observer pattern: attach maintenance observer"""
        self._observers.append(observer)
    
    def detach_observer(self, observer):
        """Observer pattern: detach maintenance observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, message):
        """Observer pattern: notify all observers of changes"""
        for observer in self._observers:
            observer.update(self, message)
    
    @abstractmethod
    def start_operation(self):
        """Start machine operation"""
        pass
    
    @abstractmethod
    def stop_operation(self):
        """Stop machine operation"""
        pass
    
    @abstractmethod
    def run_diagnostics(self):
        """Run machine diagnostics"""
        pass


class AssemblyRobot(Machine):
    """Inheritance: specialized robot for assembly operations"""
    
    def __init__(self, machine_id, name, assembly_type):
        super().__init__(machine_id, name)
        self.assembly_type = assembly_type
        self.assembled_count = 0
    
    def start_operation(self):
        print(f"Assembly robot {self.name} starting {self.assembly_type} assembly")
        self.set_state(MachineState.ACTIVE)
    
    def stop_operation(self):
        print(f"Assembly robot {self.name} stopping operation")
        self.set_state(MachineState.IDLE)
    
    def run_diagnostics(self):
        print(f"Running diagnostics on assembly robot {self.name}")
        return {"status": "operational", "assembled_count": self.assembled_count}
    
    def assemble_part(self, part_a, part_b):
        """Specific method for assembly robots"""
        if self.state != MachineState.ACTIVE:
            print(f"Cannot assemble parts: {self.name} is in {self.state.name} state")
            return False
            
        print(f"Assembling {part_a} with {part_b}")
        self.assembled_count += 1
        self.update_performance_data("assembled_count", self.assembled_count)
        return True


class PackagingRobot(Machine):
    """Inheritance: specialized robot for packaging operations"""
    
    def __init__(self, machine_id, name, packaging_capacity):
        super().__init__(machine_id, name)
        self.packaging_capacity = packaging_capacity
        self.packaged_count = 0
    
    def start_operation(self):
        print(f"Packaging robot {self.name} starting operation with capacity {self.packaging_capacity}")
        self.set_state(MachineState.ACTIVE)
    
    def stop_operation(self):
        print(f"Packaging robot {self.name} stopping operation")
        self.set_state(MachineState.IDLE)
    
    def run_diagnostics(self):
        print(f"Running diagnostics on packaging robot {self.name}")
        return {"status": "operational", "packaged_count": self.packaged_count}
    
    def package_product(self, product):
        """Specific method for packaging robots"""
        if self.state != MachineState.ACTIVE:
            print(f"Cannot package product: {self.name} is in {self.state.name} state")
            return False
            
        print(f"Packaging product {product}")
        self.packaged_count += 1
        self.update_performance_data("packaged_count", self.packaged_count)
        return True


class QualityControlBot(Machine):
    """Inheritance: specialized robot for quality control"""
    
    def __init__(self, machine_id, name, tolerance_level):
        super().__init__(machine_id, name)
        self.tolerance_level = tolerance_level
        self.inspected_count = 0
        self.rejected_count = 0
    
    def start_operation(self):
        print(f"Quality control bot {self.name} starting inspection with tolerance {self.tolerance_level}")
        self.set_state(MachineState.ACTIVE)
    
    def stop_operation(self):
        print(f"Quality control bot {self.name} stopping operation")
        self.set_state(MachineState.IDLE)
    
    def run_diagnostics(self):
        print(f"Running diagnostics on quality control bot {self.name}")
        return {
            "status": "operational", 
            "inspected_count": self.inspected_count,
            "rejected_count": self.rejected_count
        }
    
    def inspect_product(self, product, quality_score):
        """Specific method for quality control bots"""
        if self.state != MachineState.ACTIVE:
            print(f"Cannot inspect product: {self.name} is in {self.state.name} state")
            return False
            
        self.inspected_count += 1
        result = quality_score >= self.tolerance_level
        
        if not result:
            self.rejected_count += 1
            print(f"Product {product} failed quality control with score {quality_score}")
        else:
            print(f"Product {product} passed quality control with score {quality_score}")
            
        self.update_performance_data("inspected_count", self.inspected_count)
        self.update_performance_data("rejected_count", self.rejected_count)
        
        return result
