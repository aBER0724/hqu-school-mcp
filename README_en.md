# hqu-school-mcp

En | [Zh](README.md)

Helps HQU students query academic information like schedules, grades, and GPAs.


## Project Structure

```
src/
└── hqu_school_mcp/
    ├── __init__.py     # Package initialization
    ├── server.py       # MCP server implementation
    ├── sends.py        # SENDS API interaction wrapper
    └── school.py       # School academic system related functions
```

## Features

This server implements several tools for accessing student data:

- `health_check`: Verify service status
- `get_student_schedule`: Get class schedule
  - Optional "semester" parameter (e.g. "2023-2024-2")
- ~~`get_student_credit`: Get student credit information~~
- ~~`get_student_gpa`: Get student GPA information~~
- `get_student_grade`: Get grade information
  - Optional "school_year" parameter (e.g. "2024-2025")
  - Optional "semester" parameter ("一" for first semester, "二" for second semester)
- `get_teaching_week`: Get current teaching week from HQU academic system
- `get_empty_classroom_count`: Get empty classroom statistics
  - Optional "campus" parameter ("0001": Quanzhou Campus, "0002": Xiamen Campus, "0003": Longzhouchi Campus)
- `get_empty_classroom_status`: Get detailed classroom usage status
  - Required "build_id" parameter, e.g. "0002011" represents Building C4
  - Optional "day" parameter (format: "yyyy-MM-dd")
  - Optional "campus" parameter (defaults to Xiamen Campus)
- `get_college_list`: Get list of colleges
- `get_teacher_list`: Get list of teachers
  - Required "college_id" parameter representing the college ID
- `get_course_list`: Get list of courses
- `get_course_timetable`: Get course timetable information
  - Required "course_name" parameter representing the course name
  - Optional "school_year" parameter (e.g. "2024-2025")
  - Optional "semester" parameter ("一" for first semester, "二" for second semester)
- `get_class_timetable`: Get class timetable information
  - Required "class_id" parameter representing the class ID
  - Optional "school_year" parameter (e.g. "2024-2025")
  - Optional "semester" parameter ("一" for first semester, "二" for second semester)
  - Optional "is_overseas" parameter indicating whether it's a class for overseas students (defaults to false)
- `get_rooms_timetable`: Get classroom timetable information
  - Required "campus" parameter (e.g. "Xiamen Campus")
  - Required "build_name" parameter (must be obtained from get_building_list)
  - Required "room_id" parameter (must be obtained from get_classroom_list)
  - Optional "school_year" parameter (e.g. "2024-2025")
  - Optional "semester" parameter ("一" for first semester, "二" for second semester)
- `get_building_list`: Get list of buildings
  - Required "campus" parameter (e.g. "Xiamen Campus", "Quanzhou Campus", "Longzhouchi Campus")
- `get_classroom_list`: Get list of classrooms
  - Required "campus" parameter (e.g. "Xiamen Campus")
  - Required "build" parameter representing the building name

## Quick Start

1. Clone repository
```shell
git clone https://github.com/aBER0724/hqu-school-mcp.git
cd hqu-school-mcp
```

2. Set up environment with uv
```shell
# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install project
uv pip install -e .

uv pip install "mcp[cli]"
```

3. Create and configure environment variables
```shell
cp .env.example .env
```

4. Fill in your `Student ID`, WeChat `OpenId`, and [Sends Token](https://stuinfo-plus.sends.cc/#/setting) in the `.env` file
   > Search for how to get your WeChat `OpenId` on your own
   
```
# Sends API Token Configuration
SENDS_API_TOKEN=your_sends_api_token

# OpenID Configuration
OPENID=your_openid

# Student ID Configuration
STUDENT_ID=your_student_id
```

### Add MCP Server Configuration

Add this configuration to Claude desktop app's config file:

```json
"mcpServers": {
  "hqu-school-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "your/path/hqu-school-mcp",
      "run",
      "--with",
      "mcp",
      "mcp",
      "run",
      "src/hqu_school_mcp/server.py"
    ]
  }
}
```

## Usage Preview

|Tool|Preview|
|:---:|:---:|
|`get_teaching_week`|![Teaching Week](img/TeachingWeek.png)|
|`get_student_schedule`|![Schedule](img/Schedule.png)|
|`get_empty_classroom_count` <br/> `get_empty_classroom_status`|![Empty Classroom](img/EmptyClassroom.png)|
|`get_student_grade`|![Grade](img/Grade.png)|
|~~`get_student_gpa`~~|![GPA](img/GPA.png)|
|~~`get_student_credit`~~ <br/> `get_student_grade`|![Credits and Grades](img/CreditGrade.png)|
|`get_college_list` <br/> `get_teacher_list`|![College & Teacher](img/CollegeTeacher.png)|
|`get_classroom_list` <br/> `get_building_list`|![Campus & Classroom](img/BuildClass.png)|
|**Others**<br/> Query classroom/class/teacher/course schedules <br/> Query college information|...|