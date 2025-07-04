"""SynthCorp - Smart and Automated Manufacturing System"""

from src.patterns.creational.singleton_pattern import CentralControlSystem
from src.patterns.creational.factory_pattern import MachineFactory
from src.patterns.structural.facade_pattern import ManufacturingSystemFacade
from src.patterns.behavioral.observer_pattern import MaintenanceEngineer, ProductionManager
from src.patterns.behavioral.strategy_pattern import (MassProductionStrategy, 
                                                    CustomBatchStrategy, 
                                                    OnDemandProductionStrategy,
                                                    ProductionStrategyContext)
from src.patterns.creational.builder_pattern import ProductionLineBuilder, ProductionDirector
from src.patterns.behavioral.command_pattern import (StartProductionCommand, 
                                                  StopProductionCommand,
                                                  ChangeProductionStrategyCommand,
                                                  CommandInvoker)
from src.patterns.behavioral.state_pattern import MachineStateContext

from src.patterns.structural.decorator_pattern import ErrorDetectionDecorator, EnergyEfficiencyDecorator
from src.patterns.structural.adapter_pattern import LegacyMachine, LegacyMachineAdapter  
from src.systems.inventory_system import InventorySystem, SafetyProtocol
from src.core.machine import MachineState
import time


def create_safety_protocols(inventory_system, central_control):
    """Create safety protocols for the factory"""
    
    # Check if any machines are in error state
    def check_machine_states():
        for machine in central_control.get_all_machines():
            if machine.state == MachineState.ERROR:
                return False
        return True
    
    # Check if critical inventory is available
    def check_critical_inventory():
        return (inventory_system.get_item_quantity('raw_material_a') > 5 and 
                inventory_system.get_item_quantity('raw_material_b') > 5)
    
    # Create safety protocols
    machine_state_protocol = SafetyProtocol(
        "No machines in error state", 
        check_machine_states,
        "HIGH"
    )
    
    inventory_protocol = SafetyProtocol(
        "Critical inventory levels maintained",
        check_critical_inventory,
        "MEDIUM"
    )
    
    # Register protocols with central control
    central_control.add_safety_protocol(machine_state_protocol)
    central_control.add_safety_protocol(inventory_protocol)
    
    return [machine_state_protocol, inventory_protocol]


def main():
    """Main function to run the SynthCorp manufacturing system"""
    print("\n" + "=" * 80)
    print("Welcome to SynthCorp - Smart and Automated Manufacturing System")
    print("=" * 80 + "\n")
    
    # Create the central control system (Singleton)
    central_control = CentralControlSystem()
    
    # Create the manufacturing system facade
    system_facade = ManufacturingSystemFacade(central_control)
    
    # Create inventory system
    inventory_system = InventorySystem(central_control)
    
    # Add initial inventory
    inventory_system.add_item('raw_material_a', 'Steel Sheets', 100, 20, 'MetalCorp')
    inventory_system.add_item('raw_material_b', 'Circuit Boards', 80, 15, 'ElectroCorp')
    inventory_system.add_item('raw_material_c', 'Plastic Components', 150, 30, 'PolymerTech')
    
    # Create observers
    maintenance_engineer = MaintenanceEngineer("Person1")
    production_manager = ProductionManager("Person2")
    
    # Create machines using factory pattern
    machine_factory = MachineFactory()
    
    # Create assembly robots
    assembly_robot1 = machine_factory.create_machine("assembly", "AR001", "Main Assembler", assembly_type="Component")
    assembly_robot2 = machine_factory.create_machine("assembly", "AR002", "Precision Assembler", assembly_type="Circuit")
    
    # Add observers to machines
    assembly_robot1.attach_observer(maintenance_engineer)
    assembly_robot1.attach_observer(production_manager)
    assembly_robot2.attach_observer(maintenance_engineer)
    
    # Create packaging robots
    packaging_robot1 = machine_factory.create_machine("packaging", "PR001", "Primary Packager", packaging_capacity=200)
    
    # Use decorator pattern to enhance machines
    enhanced_packager = ErrorDetectionDecorator(packaging_robot1, 0.2)
    enhanced_packager.attach_observer(maintenance_engineer)
    enhanced_packager.attach_observer(production_manager)
    
    # Apply energy efficiency decorator
    energy_efficient_assembler = EnergyEfficiencyDecorator(assembly_robot2)
    energy_efficient_assembler.attach_observer(maintenance_engineer)
    
    # Create quality control bots
    qc_bot1 = machine_factory.create_machine("quality", "QC001", "Quality Inspector", tolerance_level=0.85)
    qc_bot1.attach_observer(maintenance_engineer)
    qc_bot1.attach_observer(production_manager)
    
    # Register all machines with central control
    central_control.register_machine(assembly_robot1)
    central_control.register_machine(energy_efficient_assembler)  
    central_control.register_machine(enhanced_packager)  
    central_control.register_machine(qc_bot1)
    
    # Create production strategies
    mass_strategy = MassProductionStrategy(batch_size=500)
    custom_strategy = CustomBatchStrategy(customization_level=4)
    ondemand_strategy = OnDemandProductionStrategy(priority_level=3)
    
    # Create strategy context
    strategy_context = ProductionStrategyContext(mass_strategy)
    
    # Create production line using builder pattern
    builder = ProductionLineBuilder()
    
    production_line = ProductionDirector.construct_mass_production_line(
        builder,
        "Main Production Line",
        [assembly_robot1, assembly_robot2],
        [packaging_robot1],
        [qc_bot1],
        mass_strategy
    )
    
    # Create command pattern implementation
    invoker = CommandInvoker()
    
    start_command = StartProductionCommand(production_line)
    stop_command = StopProductionCommand(production_line)
    change_strategy_command = ChangeProductionStrategyCommand(strategy_context, custom_strategy)
    
    invoker.register_command("start_production", start_command)
    invoker.register_command("stop_production", stop_command)
    invoker.register_command("change_strategy", change_strategy_command)

    legacy = LegacyMachine(machine_id=101, name="OldPress")

    adapted_legacy = LegacyMachineAdapter(legacy)

    print("=== Using Legacy Machine via Adapter ===")
    adapted_legacy.start_operation()
    adapted_legacy.run_diagnostics()
    adapted_legacy.stop_operation()

    central_system = CentralControlSystem.get_instance()
    machine = central_system.get_machine("M001")  # Replace with actual ID

    if machine:
        print("\n--- State Pattern: Machine State Transitions ---")
        state_ctx = MachineStateContext(machine)
        state_ctx.handle_start()  # IDLE → ACTIVE
        state_ctx.handle_error("Overheat detected")  # ACTIVE → ERROR
        state_ctx.handle_maintenance()  # ERROR → MAINTENANCE
        state_ctx.handle_stop()  # MAINTENANCE → IDLE

    # Create safety protocols
    safety_protocols = create_safety_protocols(inventory_system, central_control)
    
    # Simulate system operation
    print("\n" + "-" * 50)
    print("SYSTEM SIMULATION START")
    print("-" * 50)
    
    # Start the production line
    print("\n1. Starting production line")
    invoker.execute_command("start_production")
    
    # Check machine statuses
    print("\n2. Current machine statuses:")
    machine_statuses = system_facade.get_all_machine_statuses()
    for machine_id, status in machine_statuses.items():
        print(f"  - {status['name']}: {status['state']}")
    
    # Check inventory
    print("\n3. Current inventory levels:")
    inventory_report = inventory_system.get_inventory_report()
    for item in inventory_report:
        print(f"  - {item['name']}: {item['quantity']} units (Reorder level: {item['reorder_level']})")
    
    # Use resources from inventory
    print("\n4. Using materials for production:")
    inventory_system.remove_item('raw_material_a', 30)
    inventory_system.remove_item('raw_material_b', 25)
    
    # Simulate assembly operations
    print("\n5. Simulating assembly operations:")
    assembly_robot1.start_operation()
    assembly_robot1.assemble_part("Frame", "Motor")
    assembly_robot1.assemble_part("Circuit", "Housing")
    
    # Simulate quality control
    print("\n6. Simulating quality control:")
    qc_bot1.start_operation()
    product1_quality = qc_bot1.inspect_product("Product A", 0.92)  
    product2_quality = qc_bot1.inspect_product("Product B", 0.78)  
    
    # Simulate changing production strategy
    print("\n7. Changing production strategy:")
    invoker.execute_command("change_strategy")
    
    # Check safety protocols
    print("\n8. Checking safety protocols:")
    safety_status = system_facade.check_safety_status()
    print(f"  Safety Status: {'SAFE' if safety_status['safe'] else 'UNSAFE'}")
    
    # Simulate error state
    print("\n9. Simulating machine malfunction:")
    assembly_robot1.set_state(MachineState.ERROR)
    
    # Check safety again - should be unsafe now
    print("\n10. Re-checking safety protocols:")
    safety_status = system_facade.check_safety_status()
    print(f"  Safety Status: {'SAFE' if safety_status['safe'] else 'UNSAFE'}")
    
    # Simulate emergency shutdown
    print("\n11. Triggering emergency shutdown:")
    system_facade.trigger_emergency_shutdown()
    
    # Check final machine states
    print("\n12. Final machine statuses:")
    machine_statuses = system_facade.get_all_machine_statuses()
    for machine_id, status in machine_statuses.items():
        print(f"  - {status['name']}: {status['state']}")
    
    # Display alerts received by maintenance engineer
    print("\n13. Maintenance alerts received:")
    for i, alert in enumerate(maintenance_engineer.get_alerts()[-5:]):
        print(f"  [{alert['time']}] {alert['machine_name']}: {alert['message']}")
    
    print("\n" + "-" * 50)
    print("SYSTEM SIMULATION COMPLETE")
    print("-" * 50)
    
    print("\nSynthCorp Manufacturing System demonstration completed.\n")
    
    # Pause to let the user see the output
    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
