"""
Test Suite for Career Planning Education Agent
Tests core functionality, agents, and observability features
"""

import unittest
import json
import logging
from datetime import datetime
from dataclasses import asdict
from main import (
    StudentProfile,
    SchoolRecommendation,
    CourseRecommendation,
    CareerPlanningAgent
)
from observability import (
    ExecutionMetrics,
    WorkflowMetrics,
    MetricsCollector,
    AgentType
)


class TestStudentProfile(unittest.TestCase):
    """Test StudentProfile data structure"""
    
    def setUp(self):
        self.student = StudentProfile(
            name="Test Student",
            current_gpa=3.7,
            target_schools=["MIT", "Stanford"],
            target_programs=["CS"],
            current_grades={"Math": "A", "Physics": "A-"},
            extracurriculars=["Robotics"],
            test_scores={"SAT": 1400}
        )
    
    def test_student_creation(self):
        """Test creating a student profile"""
        self.assertEqual(self.student.name, "Test Student")
        self.assertEqual(self.student.current_gpa, 3.7)
        self.assertIsInstance(self.student.target_schools, list)
    
    def test_student_serialization(self):
        """Test converting student to dict"""
        student_dict = asdict(self.student)
        self.assertIsInstance(student_dict, dict)
        self.assertEqual(student_dict['name'], "Test Student")
    
    def test_gpa_validation(self):
        """Test GPA value constraints"""
        self.assertTrue(0 <= self.student.current_gpa <= 4.0)


class TestSchoolRecommendation(unittest.TestCase):
    """Test SchoolRecommendation data structure"""
    
    def setUp(self):
        self.recommendation = SchoolRecommendation(
            school_name="MIT",
            average_gpa=3.9,
            gpa_gap=0.2,
            acceptance_rate=3.3,
            why_fit="Strong CS program",
            category="Reach"
        )
    
    def test_school_recommendation_creation(self):
        """Test creating school recommendation"""
        self.assertEqual(self.recommendation.school_name, "MIT")
        self.assertEqual(self.recommendation.category, "Reach")
    
    def test_gpa_gap_calculation(self):
        """Test GPA gap is reasonable"""
        self.assertGreaterEqual(self.recommendation.gpa_gap, 0)
        self.assertLessEqual(self.recommendation.gpa_gap, 1.0)
    
    def test_acceptance_rate_valid(self):
        """Test acceptance rate is percentage"""
        self.assertGreaterEqual(self.recommendation.acceptance_rate, 0)
        self.assertLessEqual(self.recommendation.acceptance_rate, 100)


class TestCourseRecommendation(unittest.TestCase):
    """Test CourseRecommendation data structure"""
    
    def setUp(self):
        self.course = CourseRecommendation(
            course_name="AP Computer Science",
            subject="Computer Science",
            difficulty_level="AP",
            why_important="Core CS knowledge",
            expected_grade_boost="0.1-0.2 GPA"
        )
    
    def test_course_creation(self):
        """Test creating course recommendation"""
        self.assertEqual(self.course.course_name, "AP Computer Science")
        self.assertEqual(self.course.difficulty_level, "AP")
    
    def test_difficulty_levels(self):
        """Test valid difficulty levels"""
        valid_levels = ["AP", "Honors", "Regular"]
        self.assertIn(self.course.difficulty_level, valid_levels)


class TestExecutionMetrics(unittest.TestCase):
    """Test ExecutionMetrics tracking"""
    
    def setUp(self):
        self.metrics = ExecutionMetrics(
            agent_name="Test Agent",
            agent_type=AgentType.SERIAL,
            start_time=datetime.now(),
            success=True
        )
    
    def test_metrics_creation(self):
        """Test creating execution metrics"""
        self.assertEqual(self.metrics.agent_name, "Test Agent")
        self.assertEqual(self.metrics.agent_type, AgentType.SERIAL)
        self.assertTrue(self.metrics.success)
    
    def test_metrics_duration_calculation(self):
        """Test duration calculation"""
        import time
        from datetime import datetime, timedelta
        
        metrics = ExecutionMetrics(
            agent_name="Timed Agent",
            agent_type=AgentType.PARALLEL,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=5),
            success=True
        )
        metrics.calculate_duration()
        self.assertAlmostEqual(metrics.duration, 5, delta=0.1)
    
    def test_metrics_serialization(self):
        """Test converting metrics to dict"""
        metrics_dict = self.metrics.to_dict()
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict['agent_name'], "Test Agent")
        self.assertEqual(metrics_dict['agent_type'], "serial")


class TestWorkflowMetrics(unittest.TestCase):
    """Test WorkflowMetrics collection"""
    
    def setUp(self):
        self.workflow = WorkflowMetrics(
            workflow_name="Test Workflow",
            start_time=datetime.now()
        )
    
    def test_workflow_creation(self):
        """Test creating workflow metrics"""
        self.assertEqual(self.workflow.workflow_name, "Test Workflow")
        self.assertEqual(len(self.workflow.agents), 0)
    
    def test_add_agent_metrics(self):
        """Test adding agent metrics to workflow"""
        agent_metric = ExecutionMetrics(
            agent_name="Agent 1",
            agent_type=AgentType.SERIAL,
            start_time=datetime.now(),
            success=True,
            inputs_size=100,
            outputs_size=200
        )
        
        self.workflow.add_agent_metrics(agent_metric)
        self.assertEqual(len(self.workflow.agents), 1)
        self.assertEqual(self.workflow.total_inputs_size, 100)
        self.assertEqual(self.workflow.total_outputs_size, 200)
    
    def test_parallel_efficiency_calculation(self):
        """Test parallel efficiency metric"""
        # Add multiple agents with same duration
        from datetime import timedelta
        
        for i in range(3):
            agent_metric = ExecutionMetrics(
                agent_name=f"Parallel Agent {i}",
                agent_type=AgentType.PARALLEL,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(seconds=2),
                success=True,
                duration=2.0
            )
            self.workflow.add_agent_metrics(agent_metric)
        
        efficiency = self.workflow.get_parallel_efficiency()
        # Perfect parallelization would be 100%
        # With same durations, efficiency should be high
        self.assertGreater(efficiency, 0)
        self.assertLessEqual(efficiency, 100)


class TestMetricsCollector(unittest.TestCase):
    """Test MetricsCollector functionality"""
    
    def setUp(self):
        self.collector = MetricsCollector()
    
    def test_collector_creation(self):
        """Test creating metrics collector"""
        self.assertEqual(len(self.collector.workflows), 0)
    
    def test_create_workflow(self):
        """Test creating a workflow"""
        workflow = self.collector.create_workflow("Test")
        self.assertEqual(workflow.workflow_name, "Test")
        self.assertIsNotNone(workflow.start_time)
    
    def test_finalize_workflow(self):
        """Test finalizing workflow"""
        workflow = self.collector.create_workflow("Test")
        self.collector.finalize_workflow(workflow)
        
        self.assertEqual(len(self.collector.workflows), 1)
        self.assertIsNotNone(workflow.end_time)
    
    def test_get_summary(self):
        """Test getting workflow summary"""
        workflow = self.collector.create_workflow("Test")
        self.collector.finalize_workflow(workflow)
        
        summary = self.collector.get_summary()
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary['total_workflows'], 1)
    
    def test_metrics_json_serialization(self):
        """Test that metrics can be JSON serialized"""
        workflow = self.collector.create_workflow("Test")
        agent_metric = ExecutionMetrics(
            agent_name="Test Agent",
            agent_type=AgentType.SERIAL,
            start_time=datetime.now(),
            success=True
        )
        workflow.add_agent_metrics(agent_metric)
        self.collector.finalize_workflow(workflow)
        
        summary = self.collector.get_summary()
        # Should be JSON serializable
        json_str = json.dumps(summary)
        self.assertIsInstance(json_str, str)


class TestAgentTypes(unittest.TestCase):
    """Test agent type enumeration"""
    
    def test_agent_types(self):
        """Test agent type values"""
        self.assertEqual(AgentType.SERIAL.value, "serial")
        self.assertEqual(AgentType.PARALLEL.value, "parallel")
        self.assertEqual(AgentType.COORDINATOR.value, "coordinator")


class TestDataValidation(unittest.TestCase):
    """Test data validation and constraints"""
    
    def test_valid_gpa_range(self):
        """Test GPA must be between 0 and 4.0"""
        # Valid GPAs
        for gpa in [0.0, 2.0, 3.7, 4.0]:
            student = StudentProfile(
                name="Test",
                current_gpa=gpa,
                target_schools=["A"],
                target_programs=["B"],
                current_grades={},
                extracurriculars=[],
                test_scores={}
            )
            self.assertTrue(0 <= student.current_gpa <= 4.0)
    
    def test_school_category_validity(self):
        """Test school categories are valid"""
        valid_categories = ["Safety", "Target", "Reach"]
        
        for category in valid_categories:
            recommendation = SchoolRecommendation(
                school_name="Test",
                average_gpa=3.5,
                gpa_gap=0.1,
                acceptance_rate=50,
                why_fit="Test",
                category=category
            )
            self.assertIn(recommendation.category, valid_categories)


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""
    
    def test_workflow_with_multiple_agents(self):
        """Test workflow with multiple agents"""
        collector = MetricsCollector()
        workflow = collector.create_workflow("Integration Test")
        
        # Add multiple agents
        for i in range(3):
            agent_metric = ExecutionMetrics(
                agent_name=f"Agent {i}",
                agent_type=AgentType.SERIAL,
                start_time=datetime.now(),
                success=True,
                inputs_size=100 * (i + 1),
                outputs_size=200 * (i + 1)
            )
            workflow.add_agent_metrics(agent_metric)
        
        collector.finalize_workflow(workflow)
        
        self.assertEqual(len(workflow.agents), 3)
        self.assertEqual(workflow.total_inputs_size, 600)  # 100+200+300
        self.assertEqual(workflow.total_outputs_size, 1200)  # 200+400+600


def run_test_suite():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStudentProfile))
    suite.addTests(loader.loadTestsFromTestCase(TestSchoolRecommendation))
    suite.addTests(loader.loadTestsFromTestCase(TestCourseRecommendation))
    suite.addTests(loader.loadTestsFromTestCase(TestExecutionMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_test_suite()
    exit(0 if success else 1)
