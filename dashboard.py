"""SynthCorp GUI Dashboard using Tkinter"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
from src.patterns.creational.builder_pattern import ProductionLineBuilder, ProductionDirector
from src.patterns.behavioral.observer_pattern import MaintenanceEngineer, ProductionManager
from src.patterns.creational.singleton_pattern import CentralControlSystem
from src.systems.inventory_system import InventorySystem, SafetyProtocol
from src.patterns.creational.factory_pattern import MachineFactory
from src.core.machine import MachineState
from src.patterns.behavioral.command_pattern import CommandInvoker, StartProductionCommand, StopProductionCommand
from src.patterns.behavioral.strategy_pattern import MassProductionStrategy, CustomBatchStrategy, OnDemandProductionStrategy

class SynthCorpDashboard:
    """Main dashboard GUI for SynthCorp Manufacturing System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SynthCorp - Smart Manufacturing System")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # System initialization
        self.central_control = CentralControlSystem()
        self.inventory_system = InventorySystem(self.central_control)
        self.machine_factory = MachineFactory()
        self.command_invoker = CommandInvoker()
        
        # Production settings
        self.production_strategy = tk.StringVar(value="mass")
        self.current_production = None
        self.material_consumption_rate = 1  # Units per second
        self.consumption_active = False
        
        # For selection tracking
        self.updating_ui = False
        self.selected_machine_id = None
        self.selected_material_id = None
        self.selected_alert_id = None
        self.selected_maintenance_id = None
        self.selection_active = False
        
        # Maintenance data
        self.maintenance_schedule = []
        
        # Initialize default system
        self.initialize_default_system()
        
        # UI Setup
        self._create_menu()
        self._create_notebook()
        self._create_status_bar()
        
        # Start background updates
        self.running = True
        self.update_thread = threading.Thread(target=self._background_update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def initialize_default_system(self):
        """Initialize system with default machines and inventory"""
        # Default inventory
        self.inventory_system.add_item('raw_material_a', 'Steel Sheets', 1000, 20, 'MetalCorp')
        self.inventory_system.add_item('raw_material_b', 'Circuit Boards', 700, 15, 'ElectroCorp')
        self.inventory_system.add_item('raw_material_c', 'Plastic Components', 500, 30, 'PolymerTech')
        
        # Default observers
        self.maintenance_engineer = MaintenanceEngineer("Person1")
        self.production_manager = ProductionManager("Person2")
        
        # Default machines
        self.assembly_robot = self.machine_factory.create_machine(
            "assembly", "AR001", "Main Assembler", assembly_type="Component")
        self.packaging_robot = self.machine_factory.create_machine(
            "packaging", "PR001", "Primary Packager", packaging_capacity=200)
        self.qc_bot = self.machine_factory.create_machine(
            "quality", "QC001", "Quality Inspector", tolerance_level=0.85)
        
        # Register machines
        for machine in [self.assembly_robot, self.packaging_robot, self.qc_bot]:
            machine.attach_observer(self.maintenance_engineer)
            machine.attach_observer(self.production_manager)
            self.central_control.register_machine(machine)
        
        # Setup safety protocols
        self.create_safety_protocols()

    def _create_notebook(self):
        """Create the tabbed notebook interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.machines_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.alerts_tab = ttk.Frame(self.notebook)
        self.maintenance_tab = ttk.Frame(self.notebook)  # New maintenance tab
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.machines_tab, text="Machines")
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.alerts_tab, text="Alerts")
        self.notebook.add(self.maintenance_tab, text="Maintenance")  # Add new tab
        
        # Initialize each tab
        self._init_dashboard_tab()
        self._init_machines_tab()
        self._init_inventory_tab()
        self._init_alerts_tab()
        self._init_maintenance_tab()  

    def _init_maintenance_tab(self):
        """Initialize the maintenance management tab"""
        # Create a paned window to split maintenance schedule and controls
        paned_window = ttk.PanedWindow(self.maintenance_tab, orient=tk.VERTICAL)
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)

        # Maintenance schedule frame
        schedule_frame = ttk.LabelFrame(paned_window, text="Maintenance Schedule")
        paned_window.add(schedule_frame, weight=1)
        
        # Create treeview for maintenance schedule
        columns = ('Machine', 'Type', 'Date', 'Description')
        self.maintenance_tree = ttk.Treeview(schedule_frame, columns=columns, show='headings')
        
        # Define columns
        for col in columns:
            self.maintenance_tree.heading(col, text=col)
            if col == 'Description':
                self.maintenance_tree.column(col, width=250)
            else:
                self.maintenance_tree.column(col, width=100)
        
        # Add selection event handler
        self.maintenance_tree.bind('<<TreeviewSelect>>', self._on_maintenance_select)
        self.maintenance_tree.bind('<ButtonRelease-1>', self._on_maintenance_click)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=self.maintenance_tree.yview)
        self.maintenance_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.maintenance_tree.pack(fill="both", expand=True, padx=5, pady=5, side="left")
        
        # Maintenance control buttons
        control_frame = ttk.Frame(schedule_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Add Maintenance Task", 
                  command=self._add_maintenance_task).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Complete Selected Task", 
                  command=self._complete_maintenance_task).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Generate Report", 
                  command=self._generate_maintenance_report).pack(side="right", padx=5)

    def _on_maintenance_select(self, event):
        """Handle maintenance item selection"""
        if not self.updating_ui:
            selections = self.maintenance_tree.selection()
            if selections:
                self.selected_maintenance_id = selections[0]
                self.selection_active = True
                
    def _on_maintenance_click(self, event):
        """Handle maintenance item click"""
        self.selection_active = True
        self.root.after(10000, self._reset_selection_active)
        
    def _reset_selection_active(self):
        """Reset the selection_active flag"""
        self.selection_active = False

    def _add_maintenance_task(self):
        """Add a new maintenance task through dialog"""
        maint_dialog = tk.Toplevel(self.root)
        maint_dialog.title("Add Maintenance Task")
        maint_dialog.geometry("400x300")
        maint_dialog.transient(self.root)
        maint_dialog.grab_set()
        
        # Form fields
        ttk.Label(maint_dialog, text="Machine:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        machine_var = tk.StringVar()
        machine_combo = ttk.Combobox(maint_dialog, textvariable=machine_var, width=30)
        
        # Get machine names from existing machines
        machine_names = [machine.name for machine in self.central_control.get_all_machines()]
        if machine_names:
            machine_combo['values'] = machine_names
            machine_var.set(machine_names[0])
        machine_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(maint_dialog, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        type_var = tk.StringVar(value="Scheduled")
        ttk.Combobox(maint_dialog, textvariable=type_var, 
                    values=["Scheduled", "Preventive", "Calibration", "Repair"]).grid(
            row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(maint_dialog, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        date_var = tk.StringVar(value=time.strftime('%Y-%m-%d'))
        ttk.Entry(maint_dialog, textvariable=date_var).grid(
            row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(maint_dialog, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        description_var = tk.StringVar(value="Regular maintenance")
        ttk.Entry(maint_dialog, textvariable=description_var, width=30).grid(
            row=3, column=1, padx=5, pady=5, sticky="w")
        
        def submit_maintenance():
            self._add_maintenance_to_schedule(
                machine_var.get(),
                type_var.get(),
                date_var.get(),
                description_var.get()
            )
            maint_dialog.destroy()
            
        ttk.Button(maint_dialog, text="Add Task", command=submit_maintenance).grid(
            row=4, column=0, columnspan=2, padx=5, pady=20)
            
    def _add_maintenance_to_schedule(self, machine_name, maintenance_type, date, description):
        """Add a maintenance task to the schedule"""
        new_task = {
            'machine_name': machine_name,
            'type': maintenance_type,
            'date': date,
            'description': description
        }
        self.maintenance_schedule.append(new_task)
        self._update_maintenance_list()
        
    def _complete_maintenance_task(self):
        """Mark a maintenance task as completed"""
        if not hasattr(self, 'selected_maintenance_id') or not self.selected_maintenance_id:
            messagebox.showerror("Error", "No maintenance task selected")
            return
        
        # Get task details before removing
        task_values = self.maintenance_tree.item(self.selected_maintenance_id)['values']
        machine_name = task_values[0]
        task_type = task_values[1]
        
        # Remove from schedule
        task_to_remove = None
        for task in self.maintenance_schedule:
            if (task['machine_name'] == machine_name and 
                task['type'] == task_type and
                task['date'] == task_values[2]):
                task_to_remove = task
                break
                
        if task_to_remove:
            self.maintenance_schedule.remove(task_to_remove)
        
        # Remove from UI
        self.maintenance_tree.delete(self.selected_maintenance_id)
        self.selected_maintenance_id = None
        
        # Show confirmation message
        messagebox.showinfo("Task Completed", 
                          f"The {task_type} maintenance for {machine_name} has been marked as completed.")

    def _generate_maintenance_report(self):
        """Generate a maintenance report"""
        if not self.maintenance_schedule:
            messagebox.showinfo("Maintenance Report", "No maintenance tasks are currently scheduled.")
            return
            
        # Create a report dialog
        report_dialog = tk.Toplevel(self.root)
        report_dialog.title("Maintenance Report")
        report_dialog.geometry("600x500")
        report_dialog.transient(self.root)
        
        # Report header
        ttk.Label(report_dialog, text="MAINTENANCE SCHEDULE REPORT", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        ttk.Label(report_dialog, text=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").pack()
        
        # Sort tasks by date
        sorted_tasks = sorted(self.maintenance_schedule, key=lambda x: x['date'])
        
        # Create report text
        report_frame = ttk.Frame(report_dialog)
        report_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        report_text = tk.Text(report_frame, wrap="word", height=20, width=70)
        report_text.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Report content
        report_content = "UPCOMING MAINTENANCE TASKS:\n"
        report_content += "=" * 60 + "\n\n"
        
        for i, task in enumerate(sorted_tasks, 1):
            report_content += f"{i}. {task['date']} - {task['machine_name']}\n"
            report_content += f"   Type: {task['type']}\n"
            report_content += f"   Description: {task['description']}\n"
            report_content += "-" * 40 + "\n"
            
        report_content += "\nSUMMARY:\n"
        report_content += f"Total scheduled tasks: {len(sorted_tasks)}\n"
        
        # Count by type
        type_counts = {}
        for task in sorted_tasks:
            task_type = task['type']
            type_counts[task_type] = type_counts.get(task_type, 0) + 1
            
        for task_type, count in type_counts.items():
            report_content += f"{task_type} tasks: {count}\n"
            
        report_text.insert(tk.END, report_content)
        report_text.config(state="disabled")
        
        # Close button
        ttk.Button(report_dialog, text="Close Report", 
                  command=report_dialog.destroy).pack(pady=10)
        
    def _init_alerts_tab(self):
        """Initialize alerts tab with enhanced features"""
        alert_frame = ttk.LabelFrame(self.alerts_tab, text="System Alerts")
        alert_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create treeview for alerts
        columns = ('Machine', 'Status', 'Time', 'Priority', 'Description')
        self.alerts_tree = ttk.Treeview(alert_frame, columns=columns, show='headings')
    
    # Define columns
        for col in columns:
            self.alerts_tree.heading(col, text=col)
            if col == 'Description':
                self.alerts_tree.column(col, width=250)
            else:
                self.alerts_tree.column(col, width=100)
    
    # Add selection event handler
        self.alerts_tree.bind('<<TreeviewSelect>>', self._on_alert_select)
        self.alerts_tree.bind('<ButtonRelease-1>', self._on_alert_click)
    
    # Add scrollbar
        scrollbar = ttk.Scrollbar(alert_frame, orient="vertical", command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.alerts_tree.pack(fill="both", expand=True, padx=5, pady=5, side="left")
    
    # Alert response buttons
        control_frame = ttk.Frame(alert_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
    
        ttk.Button(control_frame, text="Acknowledge Alert", 
              command=self._acknowledge_alert).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Create Maintenance", 
              command=self._create_maintenance_from_alert).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Clear All Alerts", 
              command=self._clear_alerts).pack(side="right", padx=5)

    def _on_alert_select(self, event):
        """Handle alert selection"""
        selections = self.alerts_tree.selection()
        if selections:
            self.selected_alert_id = selections[0]
            self.selection_active = True

    def _on_alert_click(self, event):
        """Handle alert click to maintain selection"""
        region = self.alerts_tree.identify("region", event.x, event.y)
        if region == "cell":
            self.selection_active = True
            self.root.after(10000, self._reset_selection_active)

    def _acknowledge_alert(self):
        """Acknowledge the selected alert"""
        if not hasattr(self, 'selected_alert_id') or not self.selected_alert_id:
        # Try to get current selection if none is stored
            selections = self.alerts_tree.selection()
            if not selections:
                messagebox.showinfo("No Selection", "Please select an alert first")
                return
            self.selected_alert_id = selections[0]
    
    # Get alert details before deleting
        alert_values = self.alerts_tree.item(self.selected_alert_id, 'values')
        machine_name = alert_values[0]
    
    # Delete the alert
        self.alerts_tree.delete(self.selected_alert_id)
        self._add_log_entry(f"Acknowledged alert for {machine_name}")
    
    # Clear selection
        self.selected_alert_id = None
        self.alerts_tree.selection_remove(self.alerts_tree.selection())

    def _create_maintenance_from_alert(self):
        """Create maintenance task from selected alert"""
        if not hasattr(self, 'selected_alert_id') or not self.selected_alert_id:
        # Try to get current selection if none is stored
            selections = self.alerts_tree.selection()
            if not selections:
                messagebox.showinfo("No Selection", "Please select an alert first")
                return
            self.selected_alert_id = selections[0]
    
    # Get alert details
        alert_item = self.alerts_tree.item(self.selected_alert_id)
        alert_values = alert_item['values']
        machine_name = alert_values[0]
        alert_description = alert_values[4] if len(alert_values) > 4 else "Maintenance required"
    
    # Create maintenance task
        today = datetime.now().strftime('%Y-%m-%d')
        self._add_maintenance_to_schedule(
        machine_name,
        "Repair",
        today,
        f"Fix: {alert_description}"
    )
    
    # Remove the alert
        self.alerts_tree.delete(self.selected_alert_id)
        self._add_log_entry(f"Created maintenance for {machine_name}")
    
    # Clear selection
        self.selected_alert_id = None
        self.alerts_tree.selection_remove(self.alerts_tree.selection())

        
    def _add_test_alert(self):
        """Add a test alert to demonstrate functionality"""
        test_alert = {
            'machine_name': 'Test Machine',
            'state': 'Warning',
            'timestamp': time.time(),
            'description': 'This is a test alert',
            'priority': 'Medium'
        }
        
        # Add to alerts tree
        alert_time = datetime.now().strftime('%H:%M:%S')
        self.alerts_tree.insert('', 'end', values=(
            test_alert['machine_name'],
            test_alert['state'],
            alert_time,
            test_alert['priority'],
            test_alert['description']
        ))

    def _update_maintenance_list(self):
        """Update the maintenance schedule display"""
        if self.selection_active and self.updating_ui:
            return
            
        self.updating_ui = True
        current_selection = getattr(self, 'selected_maintenance_id', None)
        
        # Clear existing items
        for item in self.maintenance_tree.get_children():
            self.maintenance_tree.delete(item)
            
        # Add maintenance items
        for task in self.maintenance_schedule:
            item_id = self.maintenance_tree.insert('', 'end', values=(
                task['machine_name'],
                task['type'],
                task['date'],
                task['description']
            ))
            
            # Try to match with previously selected task
            if current_selection and item_id and not self.maintenance_tree.selection():
                if task['machine_name'] == self.maintenance_tree.item(current_selection, "values")[0] if current_selection in self.maintenance_tree.get_children() else "":
                    self.maintenance_tree.selection_set(item_id)
                    self.selected_maintenance_id = item_id
            
        # Try to reselect
        if current_selection and current_selection in self.maintenance_tree.get_children():
            self.maintenance_tree.selection_set(current_selection)
            
        self.updating_ui = False




    def _init_dashboard_tab(self):
        """Initialize the main dashboard tab with original styling"""
        # Create a frame for summary info
        summary_frame = ttk.LabelFrame(self.dashboard_tab, text="System Summary")
        summary_frame.pack(fill=tk.X, expand=False, padx=10, pady=10)
        
        # System status indicators
        self.lbl_machine_status = ttk.Label(summary_frame, text="Machines Online: 0")
        self.lbl_machine_status.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        self.lbl_prod_status = ttk.Label(summary_frame, text="Production Status: Idle")
        self.lbl_prod_status.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        self.lbl_safety_status = ttk.Label(summary_frame, text="Safety Status: Unknown", foreground="orange")
        self.lbl_safety_status.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        
        # Production type selection frame
        prod_type_frame = ttk.LabelFrame(self.dashboard_tab, text="Production Type")
        prod_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Radiobutton(prod_type_frame, text="Mass Production", 
                       variable=self.production_strategy, value="mass").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(prod_type_frame, text="Custom Production", 
                       variable=self.production_strategy, value="custom").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(prod_type_frame, text="On-Demand", 
                       variable=self.production_strategy, value="ondemand").pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.dashboard_tab)
        btn_frame.pack(fill=tk.X, expand=False, padx=10, pady=5)
        
        self.btn_start = ttk.Button(btn_frame, text="Start Production", command=self._start_production)
        self.btn_start.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_stop = ttk.Button(btn_frame, text="Stop Production", command=self._stop_production)
        self.btn_stop.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_emergency = ttk.Button(btn_frame, text="EMERGENCY STOP", 
                                      command=self._emergency_shutdown,
                                      style="Emergency.TButton")
        self.btn_emergency.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Create emergency button style
        style = ttk.Style()
        style.configure("Emergency.TButton", background="red", foreground="black")
        
        # Event log
        log_frame = ttk.LabelFrame(self.dashboard_tab, text="System Events")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.event_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.event_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.event_log.config(state=tk.DISABLED)
        
        # Add initial log entry
        self._add_log_entry("System dashboard initialized")

 
    def _start_production(self):
        """Start production with inventory checks and proper machine selection"""
        strategy_type = self.production_strategy.get()
    
        try:
        # Check inventory before starting
            if not self._check_inventory(strategy_type):
                messagebox.showwarning("Low Inventory", "Not enough materials to start production!")
                return
        
        # Get all machines from central control
            all_machines = self.central_control.get_all_machines()
        
        # Create appropriate strategy and select machines based on type
            if strategy_type == "mass":
                strategy = MassProductionStrategy(batch_size=100)
            # Get all machines of each type
                assembly_machines = [m for m in all_machines if m.__class__.__name__ == "AssemblyRobot"]
                packaging_machines = [m for m in all_machines if m.__class__.__name__ == "PackagingRobot"]
                qc_machines = [m for m in all_machines if m.__class__.__name__ == "QualityControlBot"]
            
                machines_to_start = assembly_machines + packaging_machines + qc_machines
            
            # Create production line using mass production constructor
                builder = ProductionLineBuilder()
                self.current_production = ProductionDirector.construct_mass_production_line(
                builder,
                f"{strategy_type.capitalize()} Production",
                assembly_machines,
                packaging_machines,
                qc_machines,
                strategy
            )
            
            elif strategy_type == "custom":
                strategy = CustomBatchStrategy(customization_level=2)
            # Get assembly and QC machines
                assembly_machines = [m for m in all_machines if m.__class__.__name__ == "AssemblyRobot"]
                qc_machines = [m for m in all_machines if m.__class__.__name__ == "QualityControlBot"]
                machines_to_start = assembly_machines + qc_machines
            
            # Create production line using custom production constructor
                builder = ProductionLineBuilder()
                self.current_production = ProductionDirector.construct_custom_batch_line(
                builder,
                f"{strategy_type.capitalize()} Production",
                assembly_machines,
                [],  # No packaging robots required for custom
                qc_machines,
                strategy
            )
            
            else:  # ondemand
                strategy = OnDemandProductionStrategy(priority_level=1)
            # Get only assembly machines
                machines_to_start = [m for m in all_machines if m.__class__.__name__ == "AssemblyRobot"]
            
            # Create production line using general constructor
            builder = ProductionLineBuilder()
            self.current_production = ProductionDirector.construct_production_line(
                builder,
                f"{strategy_type.capitalize()} Production",
                machines_to_start,
                [],  # No packaging robots required
                [],  # No QC bots required
                strategy
            )
        
        # Verify we have machines to start
            if not machines_to_start:
                raise ValueError("No machines available for selected production type")
        
        # Start machines
            for machine in machines_to_start:
                if machine:  # Check if machine exists
                    machine.start_operation()
        
        # Start inventory consumption thread
            self.consumption_active = True
            self.consumption_thread = threading.Thread(target=self._consume_inventory, args=(strategy_type,))
            self.consumption_thread.daemon = True
            self.consumption_thread.start()
        
        # Execute command
            start_command = StartProductionCommand(self.current_production)
            self.command_invoker.register_command("start_production", start_command)
            self.command_invoker.execute_command("start_production")
        
            self._add_log_entry(f"{strategy_type.capitalize()} production started")
            self._add_alert(f"{strategy_type.capitalize()} Production Started", "INFO")
            self.lbl_prod_status.config(text=f"Production Status: {strategy_type.capitalize()} Running")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start production: {str(e)}")
            self._add_log_entry(f"Error starting production: {str(e)}")
            self._add_alert(f"Production Failed: {str(e)}", "ERROR")

    def _check_inventory(self, strategy_type):
        """Check if enough inventory exists for the production type"""
        required = {
            "mass": 30,
            "custom": 20,
            "ondemand": 10
        }.get(strategy_type, 10)
        
        return (self.inventory_system.get_item_quantity('raw_material_a') >= required and
                self.inventory_system.get_item_quantity('raw_material_b') >= required and
                self.inventory_system.get_item_quantity('raw_material_c') >= required)

    def _consume_inventory(self, strategy_type):
        """Automatically consume inventory during production"""
        consumption_rates = {
            "mass": 3,
            "custom": 2, 
            "ondemand": 1
        }
        rate = consumption_rates.get(strategy_type, 1)
        
        while getattr(self, 'consumption_active', False):
            try:
                # Consume all three materials
                self.inventory_system.remove_item('raw_material_a', rate)
                self.inventory_system.remove_item('raw_material_b', rate)
                self.inventory_system.remove_item('raw_material_c', rate)
                
                # Update UI
                self.root.after(100, self.update_inventory_list)
                
                # Check if we ran out of materials
                if not self._check_inventory(strategy_type):
                    self._add_alert("Inventory depleted - stopping production", "WARNING")
                    self._stop_production()
                    break
                    
                time.sleep(1)  # Consume every second
            except Exception as e:
                self._add_alert(f"Inventory error: {str(e)}", "ERROR")
                break

    def _stop_production(self):
        """Stop production and set machines to idle"""
        try:
            # Stop inventory consumption
            self.consumption_active = False
            
            # Stop all machines
            for machine in self.central_control.get_all_machines():
                if machine:
                    machine.stop_operation()
                    machine.set_state(MachineState.IDLE)
            
            # Execute stop command
            self.command_invoker.execute_command("stop_production")
            
            self._add_log_entry("Production stopped")
            self._add_alert("Production Stopped", "WARNING")
            self.lbl_prod_status.config(text="Production Status: Stopped")
            self.update_machine_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop production: {str(e)}")
            self._add_alert(f"Stop Production Failed: {str(e)}", "ERROR")

    def _emergency_shutdown(self):
        """Emergency shutdown with machines going idle"""
        confirm = messagebox.askyesno("Emergency Shutdown", 
                                    "Are you sure you want to initiate emergency shutdown?")
        if confirm:
            try:
                # Stop inventory consumption
                self.consumption_active = False
                
                # Emergency stop all machines
                self.central_control.emergency_shutdown()
                
                # Set all machines to idle
                for machine in self.central_control.get_all_machines():
                    if machine:
                        machine.set_state(MachineState.IDLE)
                
                self._add_log_entry("EMERGENCY SHUTDOWN TRIGGERED")
                self._add_alert("EMERGENCY SHUTDOWN ACTIVATED", "CRITICAL")
                self.lbl_prod_status.config(text="Production Status: EMERGENCY STOP")
                self.update_machine_list()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error during shutdown: {str(e)}")
                self._add_alert(f"Emergency Shutdown Error: {str(e)}", "ERROR")




    def _configure_styles(self):
        """Configure ttk styles for better visibility"""
        style = ttk.Style()
        style.configure('Treeview', 
                      background='#f0f0f0',  # Light gray background
                      foreground='black',     # Black text
                      fieldbackground='#f0f0f0')
        style.map('Treeview', background=[('selected', '#0078d7')])  # Blue selection

    def _init_inventory_tab(self):
        """Initialize the inventory management tab (modified version)"""
        # Left frame for inventory list
        left_frame = ttk.Frame(self.inventory_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inventory list
        ttk.Label(left_frame, text="Current Inventory").pack(anchor=tk.W)
        
        # Create treeview for inventory
        columns = ('id', 'name', 'quantity', 'reorder', 'supplier')
        self.inventory_tree = ttk.Treeview(left_frame, columns=columns, show='headings')
        
        # Define headings
        self.inventory_tree.heading('id', text='ID')
        self.inventory_tree.heading('name', text='Name')
        self.inventory_tree.heading('quantity', text='Quantity')
        self.inventory_tree.heading('reorder', text='Reorder Level')
        self.inventory_tree.heading('supplier', text='Supplier')
        
        # Define columns
        self.inventory_tree.column('id', width=120)
        self.inventory_tree.column('name', width=150)
        self.inventory_tree.column('quantity', width=80)
        self.inventory_tree.column('reorder', width=100)
        self.inventory_tree.column('supplier', width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)



    def create_safety_protocols(self):
        """Create safety protocols for the factory"""
        def check_machine_states():
            for machine in self.central_control.get_all_machines():
                if machine.state == MachineState.ERROR:
                    return False
            return True
        
        def check_critical_inventory():
            return (self.inventory_system.get_item_quantity('raw_material_a') > 5 and 
                    self.inventory_system.get_item_quantity('raw_material_b') > 5)
        
        machine_state_protocol = SafetyProtocol(
            "No machines in error state", check_machine_states, "HIGH")
        inventory_protocol = SafetyProtocol(
            "Critical inventory levels maintained", check_critical_inventory, "MEDIUM")
        
        self.central_control.add_safety_protocol(machine_state_protocol)
        self.central_control.add_safety_protocol(inventory_protocol)

    
    def _create_menu(self):
        """Create the main menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Demo Simulation", command=self._run_demo)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Systems menu
        systems_menu = tk.Menu(menubar, tearoff=0)
        systems_menu.add_command(label="Start Production", command=self._start_production)
        systems_menu.add_command(label="Stop Production", command=self._stop_production)
        systems_menu.add_command(label="Emergency Shutdown", command=self._emergency_shutdown)
        menubar.add_cascade(label="Systems", menu=systems_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)


    



    def _create_status_bar(self):
        """Create status bar at bottom of window"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status bar with multiple sections
        self.system_status_var = tk.StringVar(value="System Status: Initializing...")
        system_status = ttk.Label(status_frame, textvariable=self.system_status_var, relief=tk.SUNKEN, anchor=tk.W)
        system_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.connection_status_var = tk.StringVar(value="Connected")
        conn_status = ttk.Label(status_frame, textvariable=self.connection_status_var, relief=tk.SUNKEN, width=15)
        conn_status.pack(side=tk.RIGHT, padx=2)
        
        self.time_var = tk.StringVar(value="00:00:00")
        time_lbl = ttk.Label(status_frame, textvariable=self.time_var, relief=tk.SUNKEN, width=10)
        time_lbl.pack(side=tk.RIGHT, padx=2)



 

    

    def _start_selected_machine(self):
        """Start the selected machine"""
        selection = self.machine_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a machine first.")
            return
        
        item_id = selection[0]
        machine_id = self.machine_tree.item(item_id, 'values')[0]
        
        machine = self.central_control.get_machine(machine_id)
        if machine:
            try:
                machine.start_operation()
                self._add_log_entry(f"Machine {machine.name} started")
                self.update_machine_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start machine: {str(e)}")
    
    def _stop_selected_machine(self):
        """Stop the selected machine"""
        selection = self.machine_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a machine first.")
            return
        
        item_id = selection[0]
        machine_id = self.machine_tree.item(item_id, 'values')[0]
        
        machine = self.central_control.get_machine(machine_id)
        if machine:
            try:
                machine.stop_operation()
                self._add_log_entry(f"Machine {machine.name} stopped")
                self.update_machine_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop machine: {str(e)}")
    
    def _run_diagnostics(self):
        """Run diagnostics on the selected machine"""
        selection = self.machine_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a machine first.")
            return
        
        item_id = selection[0]
        machine_id = self.machine_tree.item(item_id, 'values')[0]
        
        machine = self.central_control.get_machine(machine_id)
        if machine:
            try:
                diagnostics = machine.run_diagnostics()
                
                # Display diagnostics in a new window
                diag_window = tk.Toplevel(self.root)
                diag_window.title(f"Diagnostics: {machine.name}")
                diag_window.geometry("400x300")
                
                # Create a text area for the diagnostics
                diag_text = scrolledtext.ScrolledText(diag_window)
                diag_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Add diagnostics info
                diag_text.insert(tk.END, f"Machine: {machine.name} (ID: {machine.machine_id})\n")
                diag_text.insert(tk.END, f"Type: {machine.__class__.__name__}\n")
                diag_text.insert(tk.END, f"Current State: {machine.state.name}\n\n")
                diag_text.insert(tk.END, "Diagnostics Results:\n")
                
                for key, value in diagnostics.items():
                    diag_text.insert(tk.END, f"- {key}: {value}\n")
                
                diag_text.config(state=tk.DISABLED)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run diagnostics: {str(e)}")
    
    def _add_machine(self):
        """Add a new machine to the system"""
        machine_type = self.machine_type_var.get()
        machine_id = self.machine_id_entry.get()
        machine_name = self.machine_name_entry.get()
        
        if not (machine_type and machine_id and machine_name):
            messagebox.showwarning("Missing Information", "Please fill in all fields.")
            return
        
        try:
            if machine_type == "assembly":
                machine = self.machine_factory.create_machine(
                    "assembly", machine_id, machine_name, assembly_type="Standard"
                )
            elif machine_type == "packaging":
                machine = self.machine_factory.create_machine(
                    "packaging", machine_id, machine_name, packaging_capacity=100
                )
            elif machine_type == "quality":
                machine = self.machine_factory.create_machine(
                    "quality", machine_id, machine_name, tolerance_level=0.9
                )
            else:
                messagebox.showwarning("Invalid Type", "Invalid machine type.")
                return
            
            # Register machine with central control
            self.central_control.register_machine(machine)
            
            # Update the machine list
            self.update_machine_list()
            
            # Clear entry fields
            self.machine_id_entry.delete(0, tk.END)
            self.machine_name_entry.delete(0, tk.END)
            
            self._add_log_entry(f"Added new {machine_type} machine: {machine_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add machine: {str(e)}")
    
    def _use_inventory_item(self):
        """Use the selected inventory item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select an inventory item first.")
            return
        
        try:
            item_id = self.inventory_tree.item(selection[0], 'values')[0]
            quantity = int(self.use_quantity_var.get())
            
            if quantity <= 0:
                messagebox.showwarning("Invalid Quantity", "Quantity must be greater than zero.")
                return
            
            if self.inventory_system.remove_item(item_id, quantity):
                self._add_log_entry(f"Used {quantity} units of {item_id}")
                self.update_inventory_list()
            else:
                messagebox.showwarning("Failed", "Not enough inventory or item not found")
                
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Error using inventory: {str(e)}")


    def _add_inventory_item(self):
        """Add a new inventory item"""
        item_id = self.item_id_entry.get()
        name = self.item_name_entry.get()
        
        try:
            quantity = int(self.item_quantity_entry.get())
            reorder = int(self.reorder_level_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Quantity and reorder level must be numbers.")
            return
            
        supplier = self.supplier_entry.get()
        
        if not (item_id and name):
            messagebox.showwarning("Missing Information", "Item ID and name are required.")
            return
        
        try:
            self.inventory_system.add_item(item_id, name, quantity, reorder, supplier)
            
            # Clear entry fields
            self.item_id_entry.delete(0, tk.END)
            self.item_name_entry.delete(0, tk.END)
            self.item_quantity_entry.delete(0, tk.END)
            self.reorder_level_entry.delete(0, tk.END)
            self.supplier_entry.delete(0, tk.END)
            
            self._add_log_entry(f"Added {quantity} units of {name} to inventory")
            self.update_inventory_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add inventory item: {str(e)}")
    
    def _run_demo(self):
        """Run a demonstration simulation"""
        confirm = messagebox.askyesno("Run Demo", 
                                      "This will run a demonstration simulation.\n\n"
                                      "Continue?")
        if confirm:
            try:
                from src.main import main
                
                # Run the demo in a separate thread
                threading.Thread(target=main).start()
                
                self._add_log_entry("Running demonstration simulation")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run demo: {str(e)}")
    
    def _apply_alert_filter(self, event=None):
        """Apply filter to the alerts"""
        # In a full implementation, this would filter the alert log
        filter_type = self.alert_filter_var.get()
        self._add_log_entry(f"Alert filter set to: {filter_type}")
    
    def _clear_alerts(self):
        """Clear all alerts from the treeview"""
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)

            self.event_log.delete(1.0, tk.END)
            self.event_log.config(state=tk.DISABLED)
            self._add_log_entry("Cleared alert log")

    
    def _add_log_entry(self, message):
        """Add entry to event log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.event_log.config(state=tk.NORMAL)
        self.event_log.insert(tk.END, log_entry)
        self.event_log.see(tk.END)
        self.event_log.config(state=tk.DISABLED)

    def _add_alert(self, message, level="INFO"):
        """Add alert to the alert log using treeview"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
     # Determine priority based on level
        priority = "Low"
        if level == "CRITICAL":
            priority = "High"
        elif level == "WARNING":
            priority = "Medium"
    
    # Add to alerts tree
        self.alerts_tree.insert('', 'end', values=(
        "System",  # Machine name
        level,
        timestamp,
        priority,
        message
    ))
    
    # Auto-scroll to the new alert
        self.alerts_tree.see(self.alerts_tree.get_children()[-1])

    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About SynthCorp",
                           "SynthCorp - Smart Manufacturing System\n\n"
                           "Version 1.0\n\n"
                           "A demonstration of OOP design patterns in a manufacturing system.\n"
                           "Featuring real-time monitoring, production control, and inventory management.")
    
    def update_machine_list(self):
        """Update the machine list in the UI"""
        # Clear the treeview
        for item in self.machine_tree.get_children():
            self.machine_tree.delete(item)
            
        # Get machines from central control
        machines = self.central_control.get_all_machines()
        
        # Add machines to treeview
        for machine in machines:
            # Get performance data
            perf_str = "Performance: 100%"
            
            # Set row color based on machine state
            tag = machine.state.name.lower()
            
            self.machine_tree.insert('', tk.END, values=(
                machine.machine_id,
                machine.name,
                machine.__class__.__name__,
                machine.state.name,
                perf_str
            ), tags=(tag,))
        
        # Define tags for row colors
        self.machine_tree.tag_configure('active', background='black')  # Light green
        self.machine_tree.tag_configure('idle', background='black')
        self.machine_tree.tag_configure('error', background='#ffe6e6')  # Light red
        self.machine_tree.tag_configure('maintenance', background='#fff5e6')  # Light orange
        
        # Update machine count in dashboard
        self.lbl_machine_status.config(text=f"Machines Online: {len(machines)}")
    
    def update_inventory_list(self):
        """Update the inventory list in the UI"""
        # Clear the treeview
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
            
        # Get inventory report
        inventory_report = self.inventory_system.get_inventory_report()
        
        # Add inventory items to treeview
        for item in inventory_report:
            # Set row color based on inventory level
            tag = 'normal'
            if item['quantity'] <= item['reorder_level']:
                tag = 'low'
            
            self.inventory_tree.insert('', tk.END, values=(
                item['id'],
                item['name'],
                item['quantity'],
                item['reorder_level'],
                item['supplier']
            ), tags=(tag,))
        
        # Define tags for row colors
        self.inventory_tree.tag_configure('low', background='#fff0f0')  # Light pink
        self.inventory_tree.tag_configure('normal', background='black')
    
    def update_safety_status(self):
        """Update the safety status display"""
        try:
            safety_results = self.central_control.check_safety_protocols()
            all_safe = all(result[1] for result in safety_results)
            
            if all_safe:
                self.lbl_safety_status.config(text="Safety Status: OK", foreground="green")
            else:
                self.lbl_safety_status.config(text="Safety Status: VIOLATIONS", foreground="red")
                
        except Exception:
            self.lbl_safety_status.config(text="Safety Status: Unknown", foreground="orange")
    
    def _background_update(self):
        """Background thread for updating UI components"""
        while self.running:
            # Update time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_var.set(current_time)
            
            # Update machine list (every 5 seconds)
            if int(time.time()) % 5 == 0:
                self.update_machine_list()
                self.update_inventory_list()
                self.update_safety_status()
                self.system_status_var.set("System Status: Running")
            
            time.sleep(1)
    
    def _on_exit(self):
        """Handle application exit"""
        confirm = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if confirm:
            self.running = False
            self.root.destroy()


    def _background_update(self):
        """Background thread for updating UI components"""
        while self.running:
            # Update time
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_var.set(current_time)
            
            # Update machine list (every 5 seconds)
            if int(time.time()) % 5 == 0 and not self.selection_active:
                self.update_machine_list()
                self.update_inventory_list()
                self.update_safety_status()
                self._update_maintenance_list()  
                self.system_status_var.set("System Status: Running")
            
            time.sleep(1)
            
    def _init_machines_tab(self):
        """Initialize the machines monitoring tab"""
        # Machine list on the left
        left_frame = ttk.Frame(self.machines_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Machine actions on the right
        right_frame = ttk.Frame(self.machines_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=10, pady=10, ipadx=10)
        
        # Machine list
        ttk.Label(left_frame, text="Factory Machines").pack(anchor=tk.W)
        
        # Create treeview for machines
        columns = ('id', 'name', 'type', 'state', 'performance')
        self.machine_tree = ttk.Treeview(left_frame, columns=columns, show='headings')
        
        # Define headings
        self.machine_tree.heading('id', text='ID')
        self.machine_tree.heading('name', text='Name')
        self.machine_tree.heading('type', text='Type')
        self.machine_tree.heading('state', text='State')
        self.machine_tree.heading('performance', text='Performance')
        
        # Define columns
        self.machine_tree.column('id', width=80)
        self.machine_tree.column('name', width=150)
        self.machine_tree.column('type', width=120)
        self.machine_tree.column('state', width=100)
        self.machine_tree.column('performance', width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.machine_tree.yview)
        self.machine_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.machine_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Machine actions
        ttk.Label(right_frame, text="Machine Actions").pack(anchor=tk.W, pady=5)
        
        ttk.Button(right_frame, text="Start Selected Machine", 
                 command=self._start_selected_machine).pack(fill=tk.X, pady=2)
        ttk.Button(right_frame, text="Stop Selected Machine", 
                 command=self._stop_selected_machine).pack(fill=tk.X, pady=2)
        ttk.Button(right_frame, text="Diagnostics", 
                 command=self._run_diagnostics).pack(fill=tk.X, pady=2)
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Add machines section
        ttk.Label(right_frame, text="Add New Machine").pack(anchor=tk.W, pady=5)
        
        machine_types = ["assembly", "packaging", "quality"]
        self.machine_type_var = tk.StringVar(value=machine_types[0])
        
        ttk.Label(right_frame, text="Machine Type:").pack(anchor=tk.W)
        machine_type_cb = ttk.Combobox(right_frame, textvariable=self.machine_type_var, values=machine_types)
        machine_type_cb.pack(fill=tk.X, pady=2)
        
        ttk.Label(right_frame, text="Machine ID:").pack(anchor=tk.W)
        self.machine_id_entry = ttk.Entry(right_frame)
        self.machine_id_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(right_frame, text="Machine Name:").pack(anchor=tk.W)
        self.machine_name_entry = ttk.Entry(right_frame)
        self.machine_name_entry.pack(fill=tk.X, pady=2)
        
        ttk.Button(right_frame, text="Add Machine", 
                 command=self._add_machine).pack(fill=tk.X, pady=10)
    

def run_gui():
    """Run the SynthCorp GUI"""
    root = tk.Tk()
    app = SynthCorpDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()   