from src.core.machine import AssemblyRobot, PackagingRobot, QualityControlBot


class MachineFactory:
    """Factory Pattern implementation for creating different types of machines"""
    
    @staticmethod
    def create_assembly_robot(machine_id, name, assembly_type):
        """Create an assembly robot"""
        return AssemblyRobot(machine_id, name, assembly_type)
    
    @staticmethod
    def create_packaging_robot(machine_id, name, packaging_capacity):
        """Create a packaging robot"""
        return PackagingRobot(machine_id, name, packaging_capacity)
    
    @staticmethod
    def create_quality_control_bot(machine_id, name, tolerance_level):
        """Create a quality control bot"""
        return QualityControlBot(machine_id, name, tolerance_level)
        
    @staticmethod
    def create_machine(machine_type, machine_id, name, **kwargs):
        """General factory method for creating any type of machine"""
        if machine_type == "assembly":
            return MachineFactory.create_assembly_robot(
                machine_id, name, kwargs.get('assembly_type', 'general')
            )
        elif machine_type == "packaging":
            return MachineFactory.create_packaging_robot(
                machine_id, name, kwargs.get('packaging_capacity', 100)
            )
        elif machine_type == "quality":
            return MachineFactory.create_quality_control_bot(
                machine_id, name, kwargs.get('tolerance_level', 0.9)
            )
        else:
            raise ValueError(f"Unknown machine type: {machine_type}")
