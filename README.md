# Career Planning Education Agent with Google Gemini

A sophisticated AI-powered education app that helps students plan their careers and college applications using Google's Gemini API. The system uses serial agents, parallel agents, and comprehensive observability tools to provide personalized recommendations.

## Features

### Core Functionality
- **School Recommendations**: Get personalized school lists (Safety, Target, Reach) based on current GPA and target schools
- **GPA Gap Analysis**: Understand exactly how much you need to improve your GPA for each school
- **Course Recommendations**: Get specific course recommendations for your target programs
- **Academic Strengths Analysis**: Identify your strongest and weakest subjects
- **Extracurricular Guidance**: Recommendations to strengthen your application profile
- **Test Prep Strategy**: Personalized test preparation timeline and strategy

### Agent Architecture

#### Serial Agents (Sequential Execution)
1. **School Recommendation Agent**: Analyzes current GPA vs. target school requirements
2. **Course Recommendation Agent**: Recommends courses for each target program

#### Parallel Agents (Concurrent Execution)
1. **Academic Profile Analyzer**: Analyzes strengths and weaknesses
2. **Extracurricular Advisor**: Evaluates and suggests improvement areas
3. **Test Prep Advisor**: Creates personalized test strategy

#### Observability & Monitoring
- Comprehensive logging system with file and console output
- Agent execution tracking with timing information
- Detailed error handling and debugging information
- Performance metrics for each agent

## Project Structure

```
/Users/sanjana/Work/projects/Google/
├── main.py                 
├── requirements.txt
├── config.py
├── observability.py
├── test_suite.py        
└── README.md              
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Gemini API

```bash
# Using environment variable
export GEMINI_API_KEY="your-api-key-here"
```

Get your API key from: https://aistudio.google.com/app/apikey

### 3. Verify Installation

```bash
python -c "import google.generativeai as genai; print('✓ Gemini API installed')"
```

## Usage

### Basic Usage

```python
from main import CareerPlanningAgent, StudentProfile

# Create a student profile
student = StudentProfile(
    name="Alex Johnson",
    current_gpa=3.7,
    target_schools=["MIT", "Stanford", "UC Berkeley"],
    target_programs=["Computer Science", "Engineering"],
    current_grades={
        "Math": "A",
        "Physics": "A-",
        "Chemistry": "A",
        "English": "B+",
        "Computer Science": "A+"
    },
    extracurriculars=[
        "Robotics Club (President)",
        "Hackathons (3 participations)"
    ],
    test_scores={
        "SAT": 1380,
        "SAT Math": 780,
        "SAT EBRW": 600
    }
)

# Initialize agent
agent = CareerPlanningAgent()

# Get school recommendations
schools = agent.get_school_recommendations(student)
for school in schools:
    print(f"{school.school_name}: GPA Gap = {school.gpa_gap}")
```

## Agent Details

### Serial Execution Flow
```
Start
  ↓
School Recommendation Agent
  ↓
Course Recommendation Agent (for each program)
  ↓
End
```

### Parallel Execution Flow
```
Start
  ├→ Academic Profile Analyzer
  ├→ Extracurricular Advisor
  └→ Test Prep Advisor
  ↓
End (all complete)
```

## Observability Features

### Logging Levels
- **INFO**: High-level operations (agent start/complete)
- **DEBUG**: Detailed data and API responses
- **ERROR**: Failures and exceptions

### Execution Tracking
Each agent tracked with:
- Start timestamp
- Duration (seconds)
- Success/failure status
- Input/output data

### Performance Metrics
Logs include:
- Agent execution time
- Total workflow time
- Parallel vs. serial comparison

## Customization

### Adding Custom Student Data

```python
from main import StudentProfile, CareerPlanningAgent

custom_student = StudentProfile(
    name="Your Name",
    current_gpa=3.8,
    target_schools=["School1", "School2"],
    target_programs=["Program1", "Program2"],
    current_grades={"Subject1": "A", "Subject2": "B+"},
    extracurriculars=["Activity1", "Activity2"],
    test_scores={"SAT": 1400, "SAT Math": 700}
)

agent = CareerPlanningAgent()
results = agent.get_school_recommendations(custom_student)
```

### Modifying Agent Prompts

Edit the prompt strings in the agent methods to customize behavior:
- Change tone and style
- Add specific criteria
- Focus on different aspects

### Extending Functionality

Add new agents by following the pattern:

```python
@observe_agent("My New Agent")
def my_custom_agent(self, student: StudentProfile) -> dict:
    prompt = "Your custom prompt here..."
    response = self.model.generate_content(prompt)
    return json.loads(response.text)
```


### Run Main Application

```bash
python main.py
```

This runs a complete analysis for the example student and generates:
- `career_plan_*.txt`: Human-readable report
- `career_plan_*.json`: Structured data for programmatic use
- `career_planning.log`: Detailed execution logs

## Output Files

### Text Report (`career_plan_*.txt`)
Formatted report with:
- Student information
- School recommendations by category
- Course recommendations by program
- Extracurricular guidance
- Test preparation strategy

### JSON Data (`career_plan_*.json`)
Structured data containing:
```json
{
  "student_profile": { ... },
  "serial_results": {
    "school_recommendations": [ ... ],
    "course_recommendations": { ... }
  },
  "parallel_results": {
    "academic_analysis": { ... },
    "extracurricular_analysis": { ... },
    "test_prep_strategy": { ... }
  }
}
```

### Log File (`career_planning.log`)
Detailed execution logs showing:
- Agent start/completion times
- Agent execution duration
- Error information
- Debug details

## API Classes

### StudentProfile
Student information container:
```python
@dataclass
class StudentProfile:
    name: str
    current_gpa: float
    target_schools: list[str]
    target_programs: list[str]
    current_grades: dict  # subject: grade
    extracurriculars: list[str]
    test_scores: dict     # test_name: score
```

### SchoolRecommendation
School recommendation with analysis:
```python
@dataclass
class SchoolRecommendation:
    school_name: str
    average_gpa: float
    gpa_gap: float        # improvement needed
    acceptance_rate: float
    why_fit: str
    category: str         # Safety/Target/Reach
```

### CourseRecommendation
Recommended course for target program:
```python
@dataclass
class CourseRecommendation:
    course_name: str
    subject: str
    difficulty_level: str # AP/Honors/Regular
    why_important: str
    expected_grade_boost: str
```

## References

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Concurrent.futures Documentation](https://docs.python.org/3/library/concurrent.futures.html)

---

**Created**: November 2025
**Version**: 1.0
**Python**: 3.8+
