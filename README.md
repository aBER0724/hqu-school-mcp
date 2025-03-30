# hqu-school-mcp

[En](README_en.md) | Zh

帮助HQU学生查询课程表、成绩、GPA等教务信息。

## 项目结构

```
src/
└── hqu_school_mcp/
    ├── __init__.py     # 包初始化
    ├── server.py       # MCP 服务器
    ├── sends.py        # SENDS API
    └── school.py       # 学校教务系统
```

## 功能

该服务器实现了几个访问学生数据的工具：

- `health_check`：验证服务是否正常运行
- `get_student_schedule`：获取学生课程表
  - 可选"semester"参数（例如："2023-2024-2"）
- `get_student_credit`：获取学生学分信息
- `get_student_gpa`：获取学生GPA信息
- `get_student_grade`：获取学生成绩信息
- `get_teaching_week`：从华侨大学教务网站获取当前教学周
- `get_empty_classroom_count`：获取空教室统计信息
  - 可选"campus"参数（"0001"：泉州校区，"0002"：厦门校区，"0003"：龙舟池校区）
- `get_empty_classroom_status`：获取教室详细的使用状态
  - 必选"build_id"参数，例如"0002011"代表C4楼
  - 可选"day"参数，格式为"yyyy-MM-dd"
  - 可选"campus"参数（默认厦门校区）

## 快速开始

1. 克隆仓库
```shell
git clone https://github.com/aBER0724/hqu-school-mcp.git
cd hqu-school-mcp
```

1. 创建并配置环境变量
```shell
cp .env.example .env
```

1. 在`.env`文件中填入[其他设置 - 桑梓令牌](https://stuinfo-plus.sends.cc/#/setting)
```
SENDS_API_TOKEN=your_sends_api_token
```

### 添加MCP服务器配置

将以下配置添加到Claude桌面应用的配置文件中:

```json
"mcpServers": {
  "hqu-school-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "your/path/hqu-school-mcp=",
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

## 使用预览

|工具|预览|
|---|---|
|`get_teaching_week`|![教学周](img/TeachingWeek.png)|
|`get_student_schedule`|![课表](img/Schedule.png)|
|`get_empty_classroom_count` <bl /> `get_empty_classroom_status`|![课表](img/EmptyClassroom.png)|
|`get_student_credit` <bl /> `get_student_grade`|![课表](img/CreditGrade.png)|