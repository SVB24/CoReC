"""
Career Planning Education App using Google Gemini API
This app uses serial and parallel agents with observability to help students plan their careers.
"""

import json
import os
from typing import Any
from datetime import datetime
import concurrent.futures
import logging
from functools import wraps
from dataclasses import dataclass, asdict
import google.generativeai as genai

# Configure logging for observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('career_planning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class StudentProfile:
    """Student information for career planning"""
    name: str
    current_gpa: float
    target_schools: list[str]
    target_programs: list[str]
    current_grades: dict  # subject: grade mapping
    extracurriculars: list[str]
    test_scores: dict  # SAT, ACT, etc.


@dataclass
class SchoolRecommendation:
    """School recommendation with GPA gaps"""
    school_name: str
    average_gpa: float
    gpa_gap: float  # how much to improve
    acceptance_rate: float
    why_fit: str
    category: str  # Safety, Target, Reach


@dataclass
class CourseRecommendation:
    """Course recommendation for a specific program"""
    course_name: str
    subject: str
    difficulty_level: str
    why_important: str
    expected_grade_boost: str


# Observability decorator to track agent execution
def observe_agent(agent_name: str):
    """Decorator to add observability to agents"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.info(f"Starting agent: {agent_name}")
            logger.debug(f"Agent {agent_name} called with args: {args}, kwargs: {kwargs}")
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Agent {agent_name} completed successfully in {duration:.2f}s")
                logger.debug(f"Agent {agent_name} result: {result}")
                return result
            except Exception as e:
                logger.error(f"Agent {agent_name} failed with error: {str(e)}")
                raise
        
        return wrapper
    return decorator


class CareerPlanningAgent:
    """Main agent coordinator using Gemini API"""
    
    def __init__(self, api_key: str = None):
        """Initialize the agent with Gemini API"""
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("CareerPlanningAgent initialized with Gemini API")
    
    @observe_agent("School Recommendation Agent")
    def get_school_recommendations(self, student: StudentProfile) -> list[SchoolRecommendation]:
        """Serial agent: Get school recommendations based on current and target GPA"""
        logger.info(f"Getting school recommendations for {student.name}")
        
        prompt = f"""You are an educational advisor. Based on the following student profile, 
        recommend schools categorized as Safety, Target, and Reach schools.
        
        Student Profile:
        - Name: {student.name}
        - Current GPA: {student.current_gpa}
        - Target Schools: {', '.join(student.target_schools)}
        - Current Grades: {json.dumps(student.current_grades)}
        - Test Scores: {json.dumps(student.test_scores)}
        
        For each school recommendation, provide:
        1. School name
        2. Average GPA for acceptance
        3. How much current GPA needs to improve (GPA gap)
        4. Acceptance rate
        5. Why this school fits
        6. Category (Safety/Target/Reach)
        
        Format your response as a JSON array with these exact fields:
        [{{
            "school_name": "...",
            "average_gpa": X.X,
            "gpa_gap": X.X,
            "acceptance_rate": X.X,
            "why_fit": "...",
            "category": "Safety/Target/Reach"
        }}]
        
        Only respond with valid JSON, no other text."""
        
        response = self.model.generate_content(prompt)
        logger.debug(f"Gemini response for schools: {response.text}")
        
        recommendations = json.loads(response.text)
        return [SchoolRecommendation(**rec) for rec in recommendations]
    
    @observe_agent("Course Recommendation Agent")
    def get_course_recommendations(self, student: StudentProfile, program: str) -> list[CourseRecommendation]:
        """Serial agent: Get course recommendations for a specific program"""
        logger.info(f"Getting course recommendations for program: {program}")
        
        prompt = f"""You are an academic advisor specializing in {program}.
        
        Based on this student's profile:
        - Current Grades: {json.dumps(student.current_grades)}
        - Target Programs: {', '.join(student.target_programs)}
        
        Recommend the top 5 courses they should take to strengthen their application for: {program}
        
        For each course, provide:
        1. Course name
        2. Subject
        3. Difficulty level (AP/Honors/Regular)
        4. Why it's important for their target program
        5. Expected grade boost impact
        
        Format as JSON array:
        [{{
            "course_name": "...",
            "subject": "...",
            "difficulty_level": "...",
            "why_important": "...",
            "expected_grade_boost": "..."
        }}]
        
        Only respond with valid JSON."""
        
        response = self.model.generate_content(prompt)
        logger.debug(f"Gemini response for courses: {response.text}")
        
        courses = json.loads(response.text)
        return [CourseRecommendation(**course) for course in courses]
    
    @observe_agent("Academic Profile Analyzer")
    def analyze_academic_strengths(self, student: StudentProfile) -> dict[str, Any]:
        """Parallel agent: Analyze academic strengths"""
        logger.info(f"Analyzing academic strengths for {student.name}")
        
        prompt = f"""Analyze the academic profile and identify strengths and areas for improvement.
        
        Student Profile:
        - GPA: {student.current_gpa}
        - Grades by Subject: {json.dumps(student.current_grades)}
        - Test Scores: {json.dumps(student.test_scores)}
        
        Provide analysis in JSON format with:
        - top_strengths: list of strongest subjects
        - areas_to_improve: list of subjects needing work
        - overall_assessment: brief assessment
        - improvement_strategy: recommended strategy
        
        Only respond with valid JSON."""
        
        response = self.model.generate_content(prompt)
        logger.debug(f"Academic analysis response: {response.text}")
        return json.loads(response.text)
    
    @observe_agent("Extracurricular Advisor")
    def analyze_extracurriculars(self, student: StudentProfile) -> dict[str, Any]:
        """Parallel agent: Analyze extracurriculars and suggest improvements"""
        logger.info(f"Analyzing extracurriculars for {student.name}")
        
        prompt = f"""You are an admissions advisor. Analyze the student's extracurricular profile
        and suggest improvements to strengthen their application.
        
        Current Activities: {json.dumps(student.extracurriculars)}
        Target Programs: {', '.join(student.target_programs)}
        
        Provide in JSON format:
        - strengths: what's good about their activities
        - gaps: activities commonly seen in successful applicants for their target programs
        - recommendations: specific activities to pursue
        - leadership_opportunities: leadership roles to seek
        
        Only respond with valid JSON."""
        
        response = self.model.generate_content(prompt)
        logger.debug(f"Extracurricular analysis response: {response.text}")
        return json.loads(response.text)
    
    @observe_agent("Test Prep Advisor")
    def get_test_prep_strategy(self, student: StudentProfile) -> dict[str, Any]:
        """Parallel agent: Get test preparation strategy"""
        logger.info(f"Creating test prep strategy for {student.name}")
        
        prompt = f"""Create a test preparation strategy for a student applying to selective schools.
        
        Current Test Scores: {json.dumps(student.test_scores)}
        Target Schools Average Scores: {json.dumps({s: "~1450 SAT / 33 ACT" for s in student.target_schools})}
        
        Provide in JSON format:
        - current_assessment: analysis of current scores
        - target_scores: realistic target scores
        - preparation_timeline: recommended study timeline
        - resources: recommended prep resources
        - weak_areas: specific areas to focus on
        
        Only respond with valid JSON."""
        
        response = self.model.generate_content(prompt)
        logger.debug(f"Test prep strategy response: {response.text}")
        return json.loads(response.text)


def run_parallel_agents(agent: CareerPlanningAgent, student: StudentProfile) -> dict[str, Any]:
    """Run multiple agents in parallel using concurrent execution"""
    logger.info("Starting parallel agent execution")
    
    parallel_results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit parallel tasks
        future_academic = executor.submit(agent.analyze_academic_strengths, student)
        future_extracurricular = executor.submit(agent.analyze_extracurriculars, student)
        future_test_prep = executor.submit(agent.get_test_prep_strategy, student)
        
        # Collect results
        logger.info("Waiting for parallel agents to complete")
        parallel_results['academic_analysis'] = future_academic.result()
        parallel_results['extracurricular_analysis'] = future_extracurricular.result()
        parallel_results['test_prep_strategy'] = future_test_prep.result()
        logger.info("All parallel agents completed successfully")
    
    return parallel_results


def run_serial_agents(agent: CareerPlanningAgent, student: StudentProfile) -> dict[str, Any]:
    """Run agents sequentially (serial execution)"""
    logger.info("Starting serial agent execution")
    
    serial_results = {}
    
    # Serial execution: schools first, then courses
    logger.info("Executing school recommendation agent (serial)")
    serial_results['school_recommendations'] = agent.get_school_recommendations(student)
    
    # Get course recommendations for each target program
    serial_results['course_recommendations'] = {}
    for program in student.target_programs:
        logger.info(f"Executing course recommendation agent for {program} (serial)")
        serial_results['course_recommendations'][program] = agent.get_course_recommendations(
            student, program
        )
    
    return serial_results


def generate_comprehensive_report(
    student: StudentProfile,
    serial_results: dict,
    parallel_results: dict
) -> str:
    """Generate a comprehensive career planning report"""
    logger.info(f"Generating comprehensive report for {student.name}")
    
    report = f"""
╔════════════════════════════════════════════════════════════════╗
║           CAREER PLANNING & COLLEGE PREP REPORT                ║
╚════════════════════════════════════════════════════════════════╝

STUDENT: {student.name}
Current GPA: {student.current_gpa}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ACADEMIC ANALYSIS (Parallel Agent Results)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{json.dumps(parallel_results['academic_analysis'], indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SCHOOL RECOMMENDATIONS (Serial Agent Results)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Organize schools by category
    safety_schools = [s for s in serial_results['school_recommendations'] if s.category == 'Safety']
    target_schools = [s for s in serial_results['school_recommendations'] if s.category == 'Target']
    reach_schools = [s for s in serial_results['school_recommendations'] if s.category == 'Reach']
    
    report += "\n🛡️  SAFETY SCHOOLS (Likely Acceptance):\n"
    for school in safety_schools:
        report += f"""
  • {school.school_name}
    - Average GPA: {school.average_gpa}
    - Your GPA Gap: {school.gpa_gap} (need to improve by this much)
    - Acceptance Rate: {school.acceptance_rate}%
    - Why: {school.why_fit}
"""
    
    report += "\n🎯 TARGET SCHOOLS (Good Fit):\n"
    for school in target_schools:
        report += f"""
  • {school.school_name}
    - Average GPA: {school.average_gpa}
    - Your GPA Gap: {school.gpa_gap}
    - Acceptance Rate: {school.acceptance_rate}%
    - Why: {school.why_fit}
"""
    
    report += "\n🚀 REACH SCHOOLS (Aspirational):\n"
    for school in reach_schools:
        report += f"""
  • {school.school_name}
    - Average GPA: {school.average_gpa}
    - Your GPA Gap: {school.gpa_gap}
    - Acceptance Rate: {school.acceptance_rate}%
    - Why: {school.why_fit}
"""
    
    report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += "📚 RECOMMENDED COURSES (Serial Agent Results)\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for program, courses in serial_results['course_recommendations'].items():
        report += f"\n\nFor {program}:\n"
        for course in courses:
            report += f"""
  • {course.course_name} ({course.difficulty_level})
    - Subject: {course.subject}
    - Why: {course.why_important}
    - Impact: {course.expected_grade_boost}
"""
    
    report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += "🎪 EXTRACURRICULAR RECOMMENDATIONS (Parallel Agent Results)\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += json.dumps(parallel_results['extracurricular_analysis'], indent=2)
    
    report += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += "📝 TEST PREPARATION STRATEGY (Parallel Agent Results)\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += json.dumps(parallel_results['test_prep_strategy'], indent=2)
    
    report += "\n\n╚════════════════════════════════════════════════════════════════╝\n"
    
    return report


def main():
    """Main function to run the career planning agent"""
    logger.info("Starting Career Planning Education App")
    
    # Example student profile
    student = StudentProfile(
        name="Alex Johnson",
        current_gpa=3.7,
        target_schools=[
            "Stanford University",
            "MIT",
            "UC Berkeley",
            "University of Michigan",
            "Georgia Tech"
        ],
        target_programs=[
            "Computer Science",
            "Engineering",
            "Data Science"
        ],
        current_grades={
            "Math": "A",
            "Physics": "A-",
            "Chemistry": "A",
            "English": "B+",
            "History": "A-",
            "Computer Science": "A+"
        },
        extracurriculars=[
            "Robotics Club (President)",
            "Debate Team",
            "Volunteer Tutoring",
            "Hackathons (3 participations)"
        ],
        test_scores={
            "SAT": 1380,
            "ACT": 32,
            "SAT Math": 780,
            "SAT EBRW": 600
        }
    )
    
    logger.info(f"Processing student: {student.name}")
    
    try:
        # Initialize the agent
        agent = CareerPlanningAgent()
        
        # Execute serial agents
        logger.info("Executing serial agents")
        serial_results = run_serial_agents(agent, student)
        
        # Execute parallel agents
        logger.info("Executing parallel agents")
        parallel_results = run_parallel_agents(agent, student)
        
        # Generate comprehensive report
        logger.info("Generating comprehensive report")
        report = generate_comprehensive_report(student, serial_results, parallel_results)
        
        # Print and save report
        print(report)
        
        # Save report to file
        report_filename = f"career_plan_{student.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {report_filename}")
        
        # Save structured data as JSON
        json_data = {
            'student_profile': asdict(student),
            'serial_results': {
                'school_recommendations': [asdict(s) for s in serial_results['school_recommendations']],
                'course_recommendations': {
                    prog: [asdict(c) for c in courses]
                    for prog, courses in serial_results['course_recommendations'].items()
                }
            },
            'parallel_results': parallel_results
        }
        
        json_filename = f"career_plan_{student.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"Structured data saved to {json_filename}")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
