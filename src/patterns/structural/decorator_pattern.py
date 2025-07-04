from abc import ABC, abstractmethod


class MachineFeature(ABC):
    """Abstract base class for machine features"""
    
    @abstractmethod
    def start_operation(self):
        pass
    
    @abstractmethod
    def stop_operation(self):
        pass
    
    @abstractmethod
    def run_diagnostics(self):
        pass


class MachineDecorator(MachineFeature):
    """Base decorator class for machines"""
    
    def __init__(self, machine):
        self.machine = machine
    
    @property
    def machine_id(self):
        return self.machine.machine_id
    
    @property
    def name(self):
        return self.machine.name
    
    @property
    def state(self):
        return self.machine.state
    
    def start_operation(self):
        return self.machine.start_operation()
    
    def stop_operation(self):
        return self.machine.stop_operation()
    
    def run_diagnostics(self):
        return self.machine.run_diagnostics()
    
    # Forward observer pattern methods to the decorated machine
    def attach_observer(self, observer):
        return self.machine.attach_observer(observer)
    
    def detach_observer(self, observer):
        return self.machine.detach_observer(observer)
    
    def notify_observers(self, message):
        return self.machine.notify_observers(message)
    
    # Forward state management methods
    def set_state(self, state):
        return self.machine.set_state(state)
    
    # Forward performance data methods
    def get_performance_data(self):
        return self.machine.get_performance_data()
    
    def update_performance_data(self, key, value):
        return self.machine.update_performance_data(key, value)


class ErrorDetectionDecorator(MachineDecorator):
    """Decorator Pattern implementation for real-time error detection"""
    
    def __init__(self, machine, error_threshold=0.1):
        super().__init__(machine)
        self.error_threshold = error_threshold
        self.errors_detected = 0
    
    def start_operation(self):
        print(f"Error detection enabled for {self.name}")
        return self.machine.start_operation()
    
    def run_diagnostics(self):
        print(f"Running enhanced diagnostics with error detection for {self.name}")
        base_result = self.machine.run_diagnostics()
        
        # Simulate error detection
        import random
        error_probability = random.random()
        if error_probability < self.error_threshold:
            self.errors_detected += 1
            print(f"Warning: Potential issue detected in {self.name}")
            
        # Add error detection data to diagnostics
        enhanced_result = base_result.copy()
        enhanced_result["error_detection"] = {
            "errors_detected": self.errors_detected,
            "threshold": self.error_threshold
        }
        
        return enhanced_result


class EnergyEfficiencyDecorator(MachineDecorator):
    """Decorator Pattern implementation for energy efficiency monitoring"""
    
    def __init__(self, machine):
        super().__init__(machine)
        self.energy_consumption = 0
        self.operation_time = 0
        self.energy_saving_mode = False
        self.operation_start_time = None  
    
    def start_operation(self):
        print(f"Energy efficiency monitoring enabled for {self.name}")
        self.operation_start_time = self._get_time()
        result = self.machine.start_operation()
        return result
    
    def stop_operation(self):
        # Checking if the machine was properly started before stopping
        if self.operation_start_time is not None:
            operation_duration = self._get_time() - self.operation_start_time
            self.operation_time += operation_duration
            
            # Simulating energy consumption calculation
            base_consumption = operation_duration * 10  # 10 units per time unit
            if self.energy_saving_mode:
                actual_consumption = base_consumption * 0.8  # 20% reduction
                print(f"Energy saving mode saved {base_consumption * 0.2:.2f} energy units")
            else:
                actual_consumption = base_consumption
                
            self.energy_consumption += actual_consumption
            print(f"Energy consumption for this operation: {actual_consumption:.2f} units")
            
            # Reset the start time
            self.operation_start_time = None
        else:
            print(f"Warning: Attempting to stop {self.name} that wasn't properly started")
            
        return self.machine.stop_operation()
    
    def toggle_energy_saving(self):
        """Toggle energy saving mode on/off"""
        self.energy_saving_mode = not self.energy_saving_mode
        mode = "enabled" if self.energy_saving_mode else "disabled"
        print(f"Energy saving mode {mode} for {self.name}")
    
    def run_diagnostics(self):
        base_result = self.machine.run_diagnostics()
        
        # Add energy data to diagnostics
        enhanced_result = base_result.copy()
        enhanced_result["energy_data"] = {
            "total_consumption": self.energy_consumption,
            "operation_time": self.operation_time,
            "energy_saving_mode": self.energy_saving_mode
        }
        
        return enhanced_result
    
    def _get_time(self):
        """Helper method to get current time"""
        import time
        return time.time()
