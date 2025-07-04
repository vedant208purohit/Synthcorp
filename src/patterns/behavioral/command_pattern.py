from abc import ABC, abstractmethod


class ProductionCommand(ABC):
    """Command Pattern: Abstract base class for production commands"""
    
    @abstractmethod
    def execute(self):
        """Execute the command"""
        pass
    
    @abstractmethod
    def undo(self):
        """Undo the command"""
        pass


class StartProductionCommand(ProductionCommand):
    """Command to start production"""
    
    def __init__(self, production_line):
        self.production_line = production_line
        self.previous_status = None
    
    def execute(self):
        """Start the production line"""
        print(f"Executing command: Start production line {self.production_line.name}")
        self.previous_status = self.production_line.status
        success = self.production_line.start()
        return success
    
    def undo(self):
        """Undo by stopping the production line"""
        print(f"Undoing command: Stop production line {self.production_line.name} (was {self.previous_status})")
        self.production_line.stop()
        self.production_line.status = self.previous_status
        return True


class StopProductionCommand(ProductionCommand):
    """Command to stop production"""
    
    def __init__(self, production_line):
        self.production_line = production_line
        self.previous_status = None
    
    def execute(self):
        """Stop the production line"""
        print(f"Executing command: Stop production line {self.production_line.name}")
        self.previous_status = self.production_line.status
        success = self.production_line.stop()
        return success
    
    def undo(self):
        """Undo by starting the production line"""
        print(f"Undoing command: Restart production line {self.production_line.name} (was {self.previous_status})")
        self.production_line.start()
        self.production_line.status = self.previous_status
        return True


class ChangeProductionStrategyCommand(ProductionCommand):
    """Command to change production strategy"""
    
    def __init__(self, context, new_strategy):
        self.context = context
        self.new_strategy = new_strategy
        self.previous_strategy = None
    
    def execute(self):
        """Change the production strategy"""
        print(f"Executing command: Change production strategy to {self.new_strategy.__class__.__name__}")
        self.previous_strategy = self.context.strategy
        self.context.set_strategy(self.new_strategy)
        return True
    
    def undo(self):
        """Undo by reverting to previous strategy"""
        print(f"Undoing command: Revert production strategy to {self.previous_strategy.__class__.__name__ if self.previous_strategy else 'None'}")
        self.context.set_strategy(self.previous_strategy)
        return True


class CommandInvoker:
    """Invoker that executes commands"""
    
    def __init__(self):
        self._commands = []
        self._history = []
    
    def register_command(self, command_name, command):
        """Register a command with a name"""
        self._commands.append((command_name, command))
    
    def execute_command(self, command_name):
        """Execute a command by name"""
        for name, command in self._commands:
            if name == command_name:
                result = command.execute()
                if result:
                    self._history.append((name, command))
                return result
        return False
    
    def undo_last_command(self):
        """Undo the last executed command"""
        if self._history:
            name, command = self._history.pop()
            print(f"Undoing last command: {name}")
            return command.undo()
        return False
    
    def get_command_history(self):
        """Get the history of executed commands"""
        return [name for name, _ in self._history]
