class ProductionLineBuilder:
    """Builder Pattern implementation for configuring production lines"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the builder to initial state"""
        self._production_line = ProductionLine()
    
    def set_name(self, name):
        """Set the name of the production line"""
        self._production_line.name = name
        return self
    
    def add_assembly_robot(self, robot):
        """Add an assembly robot to the production line"""
        self._production_line.assembly_robots.append(robot)
        return self
    
    def add_packaging_robot(self, robot):
        """Add a packaging robot to the production line"""
        self._production_line.packaging_robots.append(robot)
        return self
    
    def add_quality_control_bot(self, robot):
        """Add a quality control bot to the production line"""
        self._production_line.quality_control_bots.append(robot)
        return self
    
    def set_production_strategy(self, strategy):
        """Set the production strategy for the line"""
        self._production_line.production_strategy = strategy
        return self
    
    def set_safety_protocol(self, protocol):
        """Set safety protocol for the production line"""
        self._production_line.safety_protocol = protocol
        return self
    
    def get_result(self):
        """Return the finished production line"""
        production_line = self._production_line
        self.reset()
        return production_line


class ProductionLine:
    """Modified ProductionLine with flexible requirements"""
    
    def __init__(self):
        self.name = "Default Production Line"
        self.assembly_robots = []
        self.packaging_robots = []
        self.quality_control_bots = []
        self.production_strategy = None
        self.safety_protocol = None
        self.status = "idle"
    
    def start(self):
        """Start the production line with flexible requirements"""
        if not self.assembly_robots:
            raise ValueError("At least one assembly robot is required")
            
        if not self.production_strategy:
            raise ValueError("No production strategy assigned")
            
        print(f"Starting production line: {self.name}")
        
        # Start all available robots
        for robot in self.assembly_robots + self.packaging_robots + self.quality_control_bots:
            robot.start_operation()
        
        # Execute production strategy
        self.production_strategy.execute()
        
        self.status = "running"
        return True
    
    
    def stop(self):
        """Stop the production line"""
        print(f"Stopping production line: {self.name}")
        
        # Stop all robots
        for robot in self.assembly_robots + self.packaging_robots + self.quality_control_bots:
            robot.stop_operation()
            
        self.status = "idle"
        return True
    
    def get_status(self):
        """Get current status of the production line"""
        return {
            "name": self.name,
            "status": self.status,
            "assembly_robots": len(self.assembly_robots),
            "packaging_robots": len(self.packaging_robots),
            "quality_control_bots": len(self.quality_control_bots),
            "strategy": self.production_strategy.__class__.__name__ if self.production_strategy else "None"
        }


class ProductionDirector:
    """Modified Director with safe list handling"""
    
    @staticmethod
    def construct_production_line(builder, name, assembly_robots, packaging_robots, quality_bots, strategy):
        """Universal production line constructor with safe list handling"""
        builder = builder.set_name(name).set_production_strategy(strategy)
        
        # Safe handling of assembly robots (required)
        if not assembly_robots:
            raise ValueError("At least one assembly robot required")
        for robot in assembly_robots:
            builder.add_assembly_robot(robot)
        
        # Optional packaging robots
        for robot in packaging_robots:
            builder.add_packaging_robot(robot)
        
        # Optional quality bots
        for robot in quality_bots:
            builder.add_quality_control_bot(robot)
        
        return builder.get_result()
    
    @staticmethod
    def construct_mass_production_line(builder, name, assembly_robots, packaging_robots, quality_bots, strategy):
        """Mass production requires all robot types"""
        if not packaging_robots:
            raise ValueError("Mass production requires packaging robots")
        if not quality_bots:
            raise ValueError("Mass production requires quality control bots")
            
        return ProductionDirector.construct_production_line(
            builder, name, assembly_robots, packaging_robots, quality_bots, strategy
        )
    
    @staticmethod
    def construct_custom_batch_line(builder, name, assembly_robots, packaging_robots, quality_bots, strategy):
        """Custom production requires assembly and quality control"""
        if not quality_bots:
            raise ValueError("Custom production requires quality control bots")
            
        return ProductionDirector.construct_production_line(
            builder, name, assembly_robots, packaging_robots, quality_bots, strategy
        )
    
    @staticmethod
    def construct_high_precision_line(builder, name, assembly_robots, packaging_robots, quality_bots, strategy, safety_protocol):
        """High precision requires extra quality control"""
        if len(quality_bots) < 2:
            raise ValueError("High precision requires at least 2 quality control bots")
            
        line = ProductionDirector.construct_production_line(
            builder, name, assembly_robots, packaging_robots, quality_bots, strategy
        )
        line.safety_protocol = safety_protocol
        return line