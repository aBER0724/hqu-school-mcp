from mcp.server.fastmcp import FastMCP, Context
from hqu_school_mcp.sends import student_data_service
from hqu_school_mcp.school import school_info_service
import sys
from typing import Optional, List
from mcp.client.websocket import websocket_client
import asyncio
import json
from datetime import datetime
import httpx
import re

mcp = FastMCP(
    "SendsServer",
    verbose=True,
    debug=True,
)


@mcp.tool()
async def health_check(
    ctx: Context,
) -> str:
    """
    健康检查端点，用于验证服务是否正常运行

    Args:
        ctx (Context): MCP上下文对象

    Returns:
        str: 服务状态信息
    """
    return "MCP Scholar服务运行正常"


@mcp.tool()
async def get_student_schedule(
    ctx: Context,
    semester: Optional[str] = None,
) -> dict:
    """
    获取学生课表数据

    Args:
        ctx (Context): MCP上下文对象
        semester (Optional[str], optional): 学期. Defaults to None.

    Returns:
        dict: 课表数据
    """
    data = await student_data_service.get_schedule(semester)
    return data

@mcp.tool()
async def get_student_grade(
    ctx: Context,
    school_year: Optional[str] = None,
    semester: Optional[str] = None,
) -> dict:
    """
    获取学生成绩数据

    Args:
        ctx (Context): MCP上下文对象
        school_year (Optional[str], optional): 学年，默认为当前学年, 例如: 2024-2025. Defaults to None.
        semester (Optional[str], optional): 学期，默认为当前学期, 一 或 二. Defaults to None.

    Returns:
        dict: 成绩数据
    """
    try:
        data = await school_info_service.get_grade(school_year, semester)
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_teaching_week(
    ctx: Context,
) -> dict:
    """
    获取当前教学周，通过调用学校API获取

    Args:
        ctx (Context): MCP上下文对象

    Returns:
        dict: 当前教学周信息，包含success状态、week_number周数和date日期
    """
    try:
        # 调用学校API获取教学周信息
        target_url = "https://apps.hqu.edu.cn/academic/schoolCalendar"

        # 获取当前日期作为备用信息
        today = datetime.now()

        # 发送HTTP请求获取API数据
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url)
            response_data = response.json()

        # 从API响应中提取当前周信息
        week_number = None
        if response_data.get("code") == "0000" and response_data.get("data"):
            curr_week = response_data["data"].get("currWeek", "")
            week_match = re.search(r'第(\d+)周', curr_week)
            if week_match:
                week_number = int(week_match.group(1))

        data = {
            "success": week_number is not None,
            "week_number": week_number,
            "date": today.strftime("%Y-%m-%d")
        }

        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_empty_classroom_status(
    ctx: Context,
    build_id: str,
    day: str,
    campus: str,
) -> dict:
    """
    获取教室详细信息，包括各时段的使用状态
    
    Args:
        ctx (Context): MCP上下文对象
        build_id (str): 建筑ID，必填，例如"0002011"代表C4楼
        day (Optional[str], optional): 日期，格式为"yyyy-MM-dd"，默认为当天. Defaults to None.
        campus (str, optional): 校区代码(0001: 泉州校区, 0002: 厦门校区, 0003: 龙舟池校区). Defaults to "0002".
        
    Returns:
        dict: 教室详情数据
    """
    try:
        data = await school_info_service.get_empty_classroom_status(build_id, day, campus)
        return data
    except Exception as e:
        return {"error": str(e)}
    

@mcp.tool()
async def get_empty_classroom_count(
    ctx: Context,
    campus: str,
) -> dict:
    """
    获取空教室统计信息
    
    Args:
        ctx (Context): MCP上下文对象
        campus (Optional[str], optional): 校区代码(0001: 泉州校区, 0002: 厦门校区, 0003: 龙舟池校区). Defaults to "0002".
        
    Returns:
        dict: 空教室统计数据
    """
    try:
        data = await school_info_service.get_empty_classroom_count(campus)
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_jwt_token(
    ctx: Context,
) -> dict:
    """
    获取微信认证的JWT令牌
    
    Args:
        ctx (Context): MCP上下文对象
        
    Returns:
        dict: 包含JWT令牌的字典
    """
    try:
        data = await school_info_service._get_jwt_token()
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_college_list(
    ctx: Context,
) -> dict:
    """
    获取学院列表
    
    Args:
        ctx (Context): MCP上下文对象
        
    Returns:
        dict: 包含学院列表的字典
    """
    try:
        data = await school_info_service.get_college_list()
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_class_timetable(
    ctx: Context,
    class_id: str,
    school_year: Optional[str] = None,
    semester: Optional[str] = None,
    is_overseas: bool = False,
) -> dict:
    """
    获取班级课表信息
    
    Args:
        ctx (Context): MCP上下文对象
        class_id (str): 班级ID
        school_year (Optional[str], optional): 学年, 例如: 2024-2025. Defaults to None.
        semester (Optional[str], optional): 上学期: 一, 下学期: 二. Defaults to None.
        is_overseas (bool, optional): 是否是境外生班级. Defaults to False.
        
    Returns:
        dict: 包含班级课表信息的字典
    """
    try:
        data = await school_info_service.get_class_timetable(class_id, school_year, semester, is_overseas)
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_teacher_list(
    ctx: Context,
    college_id: str,
) -> dict:
    """
    获取教师列表
    
    Args:
        ctx (Context): MCP上下文对象
        college_id (str): 学院ID
        
    Returns:
        dict: 包含教师列表的字典
    """
    try:
        data = await school_info_service.get_teacher_list(college_id)
        return data
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_teacher_timetable(
    ctx: Context,
    teacher_id: str,
    school_year: Optional[str] = None,
    semester: Optional[str] = None,
) -> dict:
    """
    获取教师课表信息
    
    Args:
        ctx (Context): MCP上下文对象
        teacher_id (str): 教师ID
        school_year (Optional[str], optional): 学年, 例如: 2024-2025. Defaults to None.
        semester (Optional[str], optional): 上学期: 一, 下学期: 二. Defaults to None.
        
    Returns:
        dict: 包含教师课表信息的字典
    """
    try:
        data = await school_info_service.get_teacher_timetable(teacher_id, school_year, semester)
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_course_list(
    ctx: Context,
) -> dict:
    """
    获取课程列表
    
    Args:
        ctx (Context): MCP上下文对象
        
    Returns:
        dict: 包含课程列表的字典
    """
    try:
        data = await school_info_service.get_course_list()
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_course_timetable(
    ctx: Context,
    course_name: str,
    school_year: Optional[str] = None,
    semester: Optional[str] = None,
) -> dict:
    """
    获取课程课表信息
    
    Args:
        ctx (Context): MCP上下文对象
        course_name (str): 课程名称
        school_year (Optional[str], optional): 学年, 例如: 2024-2025. Defaults to None.
        semester (Optional[str], optional): 上学期: 一, 下学期: 二. Defaults to None.
        
    Returns:
        dict: 包含课程课表信息的字典
    """
    try:
        data = await school_info_service.get_course_timetable(course_name, school_year, semester)
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_rooms_timetable(
    ctx: Context,
    campus: str,
    build_name: str,
    room_id: str,
    school_year: Optional[str] = None,
    semester: Optional[str] = None,
) -> dict:
    """
    获取教室课表信息
    
    Args:
        ctx (Context): MCP上下文对象
        school_year (Optional[str], optional): 学年. Defaults to None.
        semester (Optional[str], optional): 学期. Defaults to None.
        campus (Optional[str], optional): 校区. Defaults to "厦门校区".
        build_name (Optional[str], optional): 建筑名称, 需要从 get_building_list() 中获取. Defaults to None.
        room_id (Optional[str], optional): 教室ID, 需要从 get_classroom_list() 中获取. Defaults to None.
        
    Returns:
        dict: 包含教室课表信息的字典
    """
    try:
        data = await school_info_service.get_rooms_timetable(school_year, semester, campus, build_name, room_id)
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_building_list(
    ctx: Context,
    campus: str,
) -> dict:
    """
    获取建筑列表
    
    Args:
        ctx (Context): MCP上下文对象
        campus (Optional[str], optional): 校区: 厦门校区, 泉州校区, 龙舟池校区. Defaults to "厦门校区".
        
    Returns:
        dict: 包含建筑列表的字典
    """
    try:
        data = await school_info_service.get_building_list(campus)
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_classroom_list(
    ctx: Context,
    campus:str,
    build:str,
) -> dict:
    """
    获取教室列表
    
    Args:
        ctx (Context): MCP上下文对象
        campus (Optional[str], optional): 校区: 厦门校区, 泉州校区, 龙舟池校区. Defaults to "厦门校区".
        build (Optional[str], optional): 建筑名称. Defaults to None.
        
    Returns:
        dict: 包含教室列表的字典
    """
    try:
        data = await school_info_service.get_classroom_list(campus, build)
        return data
    except Exception as e:
        return {"error": str(e)}


def cli_main():
    """
    CLI入口点，使用STDIO交互
    
    Returns:
        None
    """
    print("MCP Scholar STDIO服务准备启动...", file=sys.stderr)

    try:
        # 启动STDIO服务器
        sys.stderr.write("MCP Scholar STDIO服务已启动，等待输入...\n")
        sys.stderr.flush()
        mcp.run()
    except Exception as e:
        print(f"服务启动失败: {str(e)}", file=sys.stderr)


def server_main():
    """
    服务入口点函数，使用WebSocket交互
    
    Returns:
        None
    """
    try:
        # 启动WebSocket服务器
        mcp.run(host="0.0.0.0", port=8765)
    except Exception as e:
        print(f"服务启动失败: {str(e)}", file=sys.stderr)


async def client_test():
    """
    测试客户端连接和API调用的函数
    
    Returns:
        None
    """
    # 使用WebSocket连接到您的服务器
    async with websocket_client("ws://localhost:8765") as client:
        # 列出可用工具
        tools = await client.list_tools()
        print("可用工具:", [tool.name for tool in tools])

        try:
            # 调用健康检查工具
            result = await client.invoke_tool("health_check")
            print("健康检查结果:", result)

            # 调用其他工具
            credit_data = await client.invoke_tool("get_student_credit")
            print("学分数据:", credit_data)

        except Exception as e:
            print(f"调用工具时出错: {str(e)}")

if __name__ == "__main__":
    # 选择要运行的主函数
    import argparse

    parser = argparse.ArgumentParser(description='MCP Scholar 服务')
    parser.add_argument('--mode', choices=['server', 'cli', 'client'], default='server',
                        help='运行模式: server=WebSocket服务器, cli=STDIO服务器, client=测试客户端')

    args = parser.parse_args()

    if args.mode == 'server':
        server_main()
    elif args.mode == 'cli':
        cli_main()
    elif args.mode == 'client':
        asyncio.run(client_test())
