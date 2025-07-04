from abc import ABC, abstractmethod


class ProductionStrategy(ABC):
    """Strategy Pattern implementation for different production approaches"""
    
    @abstractmethod
    def execute(self):
        """Execute the production strategy"""
        pass
    
    @abstractmethod
    def calculate_resource_requirements(self, order_quantity):
        """Calculate resources needed for production"""
        pass


class MassProductionStrategy(ProductionStrategy):
    """Strategy for high-volume, standardized production"""
    
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
    
    def execute(self):
        """Execute mass production"""
        print(f"Starting mass production with batch size {self.batch_size}")
        print("Configuring assembly line for maximum throughput")
        print("Allocating resources for continuous production")
        return {
            "strategy": "mass_production",
            "batch_size": self.batch_size,
            "status": "running"
        }
    
    def calculate_resource_requirements(self, order_quantity):
        """Calculate resources needed for mass production"""
        batches = (order_quantity + self.batch_size - 1) // self.batch_size  # Ceiling division
        
        return {
            "raw_materials": {
                "material_a": order_quantity * 1.2,  # 20% extra for waste
                "material_b": order_quantity * 0.8
            },
            "machine_time": {
                "assembly": batches * 4,  # 4 hours per batch
                "packaging": batches * 2  # 2 hours per batch
            },
            "estimated_completion_time": batches * 8  # 8 hours per batch
        }


class CustomBatchStrategy(ProductionStrategy):
    """Strategy for customized batch production"""
    
    def __init__(self, customization_level=3):
        self.customization_level = customization_level  # 1-5 scale
    
    def execute(self):
        """Execute custom batch production"""
        print(f"Starting custom batch production with customization level {self.customization_level}")
        print("Configuring assembly for precision and customization")
        print("Loading custom specifications for this batch")
        return {
            "strategy": "custom_batch",
            "customization_level": self.customization_level,
            "status": "running"
        }
    
    def calculate_resource_requirements(self, order_quantity):
        """Calculate resources needed for custom batch production"""
        # Custom production requires more resources per item
        customization_factor = 1 + (self.customization_level * 0.2)  # Level 3 = 1.6x resources
        
        return {
            "raw_materials": {
                "material_a": order_quantity * customization_factor,
                "material_b": order_quantity * 0.9,
                "custom_material": order_quantity * 0.5
            },
            "machine_time": {
                "assembly": order_quantity * 0.1 * customization_factor,  # 0.1 hours per item
                "packaging": order_quantity * 0.05,  # 0.05 hours per item
                "quality_control": order_quantity * 0.08  # Extra QC time
            },
            "estimated_completion_time": order_quantity * 0.2 * customization_factor  # 0.2 hours per item
        }


class OnDemandProductionStrategy(ProductionStrategy):
    """Strategy for on-demand, just-in-time production"""
    
    def __init__(self, priority_level=2):
        self.priority_level = priority_level  # 1-3 scale (3 = highest)
    
    def execute(self):
        """Execute on-demand production"""
        print(f"Starting on-demand production with priority level {self.priority_level}")
        print("Configuring just-in-time production line")
        print("Minimizing work-in-progress inventory")
        return {
            "strategy": "on_demand",
            "priority_level": self.priority_level,
            "status": "running"
        }
    
    def calculate_resource_requirements(self, order_quantity):
        """Calculate resources needed for on-demand production"""
        # Priority affects resource allocation and speed
        rush_factor = self.priority_level / 2  # Higher priority = more resources
        
        return {
            "raw_materials": {
                "material_a": order_quantity * 1.1,  # 10% extra for flexibility
                "material_b": order_quantity * 0.85
            },
            "machine_time": {
                "assembly": order_quantity * 0.15 / rush_factor,
                "packaging": order_quantity * 0.05,
                "logistics": order_quantity * 0.03  # Special logistics handling
            },
            "estimated_completion_time": order_quantity * 0.25 / rush_factor
        }


class ProductionStrategyContext:
    """Context class that uses a production strategy"""
    
    def __init__(self, strategy=None):
        self.strategy = strategy
    
    def set_strategy(self, strategy):
        """Change strategy at runtime"""
        self.strategy = strategy
        print(f"Production strategy changed to {strategy.__class__.__name__}")
    
    def execute_strategy(self):
        """Execute the current strategy"""
        if self.strategy:
            return self.strategy.execute()
        else:
            print("No production strategy set")
            return {"error": "no_strategy_set"}
    
    def get_resource_requirements(self, order_quantity):
        """Calculate resources using current strategy"""
        if self.strategy:
            return self.strategy.calculate_resource_requirements(order_quantity)
        else:
            print("No production strategy set")
            return {"error": "no_strategy_set"}
