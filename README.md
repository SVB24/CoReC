# Career Planning Education Agent with Google Gemini

A sophisticated AI-powered education app that helps students plan their careers and college applications using Google's Gemini API. The system uses serial agents, parallel agents, and comprehensive observability tools to provide personalized recommendations.

## Features

### 🎯 Core Functionality
- **School Recommendations**: Get personalized school lists (Safety, Target, Reach) based on current GPA and target schools
- **GPA Gap Analysis**: Understand exactly how much you need to improve your GPA for each school
- **Course Recommendations**: Get specific course recommendations for your target programs
- **Academic Strengths Analysis**: Identify your strongest and weakest subjects
- **Extracurricular Guidance**: Recommendations to strengthen your application profile
- **Test Prep Strategy**: Personalized test preparation timeline and strategy

### 🔄 Agent Architecture

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
├── main.py                 # Main agent implementation
├── examples.py             # Usage examples and demos
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── README.md              # This file
└── career_planning.log    # Generated log file
```

## Installation

### 1. Install Dependencies

```bash
cd /Users/sanjana/Work/projects/Google/
pip install -r requirements.txt
```

### 2. Set Up Google Gemini API

```bash
# Option 1: Using environment variable
export GEMINI_API_KEY="your-api-key-here"

# Option 2: Using .env file
cp .env.example .env
# Edit .env and add your API key
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

### Run Examples

```bash
python examples.py
```

This runs 4 different examples:
1. **Basic Usage**: Single student analysis
2. **Batch Processing**: Multiple students
3. **Custom Input**: How to create custom student profiles
4. **Full Workflow**: Complete analysis with all agents

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
Beautiful formatted report with:
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

## Troubleshooting

### API Key Issues
```
ValueError: GEMINI_API_KEY environment variable not set
```
**Solution**: Set your API key via environment or .env file

### Import Errors
```
ImportError: No module named 'google.generativeai'
```
**Solution**: Run `pip install -r requirements.txt`

### JSON Parsing Errors
If Gemini returns non-JSON:
1. Check your prompts end with "Only respond with valid JSON"
2. Review the log file for the actual response
3. Simplify the prompt structure

### Rate Limiting
If you hit API rate limits:
1. Add delays between requests
2. Use batch processing with throttling
3. Check Gemini API quota limits

## Advanced Usage

### Batch Processing with Rate Limiting

```python
import time
from main import CareerPlanningAgent, StudentProfile

agent = CareerPlanningAgent()
students = [...]  # Your student list

for student in students:
    schools = agent.get_school_recommendations(student)
    time.sleep(2)  # Rate limiting delay
```

### Custom Report Generation

```python
from main import generate_comprehensive_report

# After running agents
report = generate_comprehensive_report(student, serial_results, parallel_results)

# Customize and save
with open(f"custom_report_{student.name}.txt", "w") as f:
    f.write(report)
```

### Monitoring Parallel Execution

```python
from main import run_parallel_agents

results = run_parallel_agents(agent, student)
# Results dict contains outputs from all 3 parallel agents
```

## Performance Characteristics

- **Serial Agents**: ~20-30 seconds (depends on API latency)
- **Parallel Agents**: ~20-30 seconds (all run concurrently)
- **Total Workflow**: ~40-60 seconds for complete analysis
- **Log File Size**: ~50-100 KB per run

## Error Handling

The system includes:
- Try-catch blocks around API calls
- Detailed error logging with stack traces
- Graceful degradation when agents fail
- Informative error messages

## API Rate Limits

Default Gemini API limits:
- 60 requests per minute (free tier)
- Higher limits for paid plans

Monitor your usage in logs to stay within limits.

## Future Enhancements

Potential additions:
- Web UI for interactive student profiles
- Database persistence for student histories
- Email report delivery
- Real-time progress tracking
- Integration with college databases
- Multi-language support
- Video generation of personalized guidance

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the `career_planning.log` file
3. Verify API key and dependencies
4. Check Gemini API status

## References

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Concurrent.futures Documentation](https://docs.python.org/3/library/concurrent.futures.html)

---

**Created**: November 2025
**Version**: 1.0
**Python**: 3.8+
