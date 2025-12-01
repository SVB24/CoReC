"""
Advanced Configuration and Utilities for Career Planning Agent
Includes monitoring dashboards, metrics collection, and advanced features
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import time
from functools import wraps


class AgentType(Enum):
    """Types of agents in the system"""
    SERIAL = "serial"
    PARALLEL = "parallel"
    COORDINATOR = "coordinator"


@dataclass
class ExecutionMetrics:
    """Metrics for agent execution"""
    agent_name: str
    agent_type: AgentType
    start_time: datetime
    end_time: datetime = None
    duration: float = 0.0
    success: bool = True
    error_message: str = ""
    inputs_size: int = 0
    outputs_size: int = 0
    
    def calculate_duration(self):
        """Calculate execution duration"""
        if self.end_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        return self.duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'agent_name': self.agent_name,
            'agent_type': self.agent_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration,
            'success': self.success,
            'error_message': self.error_message,
            'inputs_size_bytes': self.inputs_size,
            'outputs_size_bytes': self.outputs_size
        }


@dataclass
class WorkflowMetrics:
    """Metrics for entire workflow"""
    workflow_name: str
    start_time: datetime
    end_time: datetime = None
    duration: float = 0.0
    agents: List[ExecutionMetrics] = field(default_factory=list)
    total_inputs_size: int = 0
    total_outputs_size: int = 0
    success: bool = True
    error_message: str = ""
    
    def add_agent_metrics(self, metrics: ExecutionMetrics):
        """Add agent metrics to workflow"""
        self.agents.append(metrics)
        self.total_inputs_size += metrics.inputs_size
        self.total_outputs_size += metrics.outputs_size
    
    def finalize(self):
        """Finalize workflow metrics"""
        if self.end_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
    
    def get_parallel_efficiency(self) -> float:
        """Calculate parallel execution efficiency"""
        if not self.agents:
            return 0.0
        
        # Find max duration among parallel agents
        max_agent_duration = max(agent.duration for agent in self.agents)
        
        # Sum of all agent durations (if run sequentially)
        total_agent_duration = sum(agent.duration for agent in self.agents)
        
        if total_agent_duration == 0:
            return 0.0
        
        # Efficiency: how close to theoretical maximum parallelization
        return (total_agent_duration / (max_agent_duration * len(self.agents))) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'workflow_name': self.workflow_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_duration_seconds': self.duration,
            'agents': [agent.to_dict() for agent in self.agents],
            'total_inputs_size_bytes': self.total_inputs_size,
            'total_outputs_size_bytes': self.total_outputs_size,
            'workflow_success': self.success,
            'error_message': self.error_message,
            'parallel_efficiency_percent': self.get_parallel_efficiency()
        }


class MetricsCollector:
    """Collects and manages metrics for all agents and workflows"""
    
    def __init__(self):
        self.workflows: List[WorkflowMetrics] = []
        self.logger = logging.getLogger('MetricsCollector')
    
    def create_workflow(self, workflow_name: str) -> WorkflowMetrics:
        """Create a new workflow metrics tracker"""
        workflow = WorkflowMetrics(
            workflow_name=workflow_name,
            start_time=datetime.now()
        )
        self.logger.info(f"Workflow '{workflow_name}' started")
        return workflow
    
    def finalize_workflow(self, workflow: WorkflowMetrics):
        """Finalize workflow metrics"""
        workflow.end_time = datetime.now()
        workflow.finalize()
        self.workflows.append(workflow)
        self.logger.info(f"Workflow '{workflow.workflow_name}' completed in {workflow.duration:.2f}s")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all workflows"""
        return {
            'total_workflows': len(self.workflows),
            'total_agents_executed': sum(len(w.agents) for w in self.workflows),
            'total_time': sum(w.duration for w in self.workflows),
            'workflows': [w.to_dict() for w in self.workflows]
        }
    
    def save_metrics(self, filename: str):
        """Save metrics to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)
        self.logger.info(f"Metrics saved to {filename}")


class ObservabilityDashboard:
    """Dashboard for monitoring agent execution"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.logger = logging.getLogger('ObservabilityDashboard')
    
    def print_workflow_summary(self, workflow: WorkflowMetrics):
        """Print formatted workflow summary"""
        print(f"\n{'='*70}")
        print(f"Workflow: {workflow.workflow_name}")
        print(f"{'='*70}")
        print(f"Status: {'✓ SUCCESS' if workflow.success else '✗ FAILED'}")
        print(f"Duration: {workflow.duration:.2f} seconds")
        print(f"Agents Executed: {len(workflow.agents)}")
        print(f"Data Size - In: {workflow.total_inputs_size:,} bytes, Out: {workflow.total_outputs_size:,} bytes")
        
        if any(agent.agent_type == AgentType.PARALLEL for agent in workflow.agents):
            print(f"Parallel Efficiency: {workflow.get_parallel_efficiency():.1f}%")
        
        print(f"\nAgent Breakdown:")
        for agent in workflow.agents:
            status = "✓" if agent.success else "✗"
            print(f"  {status} {agent.agent_name}: {agent.duration:.2f}s ({agent.agent_type.value})")
            if agent.error_message:
                print(f"    Error: {agent.error_message}")
        
        print(f"{'='*70}\n")
    
    def print_all_summaries(self):
        """Print summaries for all workflows"""
        for workflow in self.metrics.workflows:
            self.print_workflow_summary(workflow)
    
    def generate_html_report(self, filename: str):
        """Generate HTML dashboard report"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Career Planning Agent - Observability Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .workflow { background: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .agent { margin: 10px 0; padding: 10px; background: #ecf0f1; border-left: 4px solid #3498db; }
        .success { border-left-color: #27ae60; }
        .failed { border-left-color: #e74c3c; }
        .metric { display: inline-block; margin: 10px 20px 10px 0; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .metric-label { font-size: 12px; color: #7f8c8d; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Career Planning Agent - Observability Dashboard</h1>
        <p>Real-time monitoring and performance metrics</p>
    </div>
"""
        
        summary = self.metrics.get_summary()
        
        html += f"""
    <div class="workflow">
        <h2>Overall Statistics</h2>
        <div class="metric">
            <div class="metric-value">{summary['total_workflows']}</div>
            <div class="metric-label">Workflows</div>
        </div>
        <div class="metric">
            <div class="metric-value">{summary['total_agents_executed']}</div>
            <div class="metric-label">Agents Executed</div>
        </div>
        <div class="metric">
            <div class="metric-value">{summary['total_time']:.1f}s</div>
            <div class="metric-label">Total Time</div>
        </div>
    </div>
"""
        
        for workflow_data in summary['workflows']:
            status_class = "success" if workflow_data['workflow_success'] else "failed"
            html += f"""
    <div class="workflow">
        <h3>{workflow_data['workflow_name']} <span style="color: {'green' if workflow_data['workflow_success'] else 'red'}">
            {'✓ Success' if workflow_data['workflow_success'] else '✗ Failed'}</span></h3>
        <table>
            <tr>
                <th>Agent Name</th>
                <th>Type</th>
                <th>Duration (s)</th>
                <th>Status</th>
            </tr>
"""
            for agent_data in workflow_data['agents']:
                agent_status = "✓ Success" if agent_data['success'] else "✗ Failed"
                html += f"""
            <tr>
                <td>{agent_data['agent_name']}</td>
                <td>{agent_data['agent_type']}</td>
                <td>{agent_data['duration_seconds']:.2f}</td>
                <td>{agent_status}</td>
            </tr>
"""
            html += """
        </table>
"""
            if 'parallel_efficiency_percent' in workflow_data:
                html += f"<p>Parallel Efficiency: {workflow_data['parallel_efficiency_percent']:.1f}%</p>"
            html += "</div>"
        
        html += """
</body>
</html>
"""
        
        with open(filename, 'w') as f:
            f.write(html)
        self.logger.info(f"HTML report saved to {filename}")


# Global metrics collector
_metrics_collector = MetricsCollector()
_dashboard = ObservabilityDashboard(_metrics_collector)


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector"""
    return _metrics_collector


def get_dashboard() -> ObservabilityDashboard:
    """Get the global observability dashboard"""
    return _dashboard
