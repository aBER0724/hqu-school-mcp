import httpx
from typing import Dict, Any, Optional, List
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 从环境变量获取必要的信息
STUDENT_ID = os.getenv("STUDENT_ID")
if not STUDENT_ID:
    raise ValueError("请在.env文件中设置STUDENT_ID")


class SchoolInfoService:
    """华侨大学校园信息服务类"""

    BASE_URL = "https://apps.hqu.edu.cn"

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.current_school_year = self._get_current_semester()[0]
        self.current_semester = self._get_current_semester()[1]
        self._jwt_token = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _get_current_semester(self) -> tuple:
        """计算当前学期，返回(学年, 学期)元组"""
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # 获取学年
        if current_month >= 9:
            school_year = f"{current_year}-{current_year + 1}"
        else:
            school_year = f"{current_year - 1}-{current_year}"

        # 判断学期
        if 2 <= current_month <= 7:
            semester_num = '二'  # 下学期
        else:
            semester_num = '一'  # 上学期

        return (school_year, semester_num)

    async def _get_jwt_token(self, refresh: bool = False) -> str:
        """
        获取或刷新JWT令牌
        
        Args:
            refresh: 是否强制刷新令牌

        Returns:
            str: JWT令牌字符串
        """
        if self._jwt_token is None or refresh:
            openid = os.getenv("OPENID")
            if not openid:
                raise ValueError("环境变量中未找到OPENID")

            url = f"{self.BASE_URL}/wechatauth/wechat/generate/token"
            params = {"openId": openid}

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != "0000" or not data.get("data") or not data.get("data").get("restToken"):
                raise ValueError(f"获取JWT令牌失败: {data.get('msg', '未知错误')}")
            
            self._jwt_token = data.get("data").get("restToken").get("token")
        
        return self._jwt_token

    def _get_headers(self, extra_headers: Dict = None) -> Dict[str, str]:
        """
        获取请求头
        
        Args:
            extra_headers: 额外的请求头

        Returns:
            Dict[str, str]: 合并后的请求头
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json;charset=utf-8"
        }
        
        if self._jwt_token:
            headers["Authorization"] = self._jwt_token
        
        if extra_headers:
            headers.update(extra_headers)
            
        return headers

    async def get_empty_classroom_count(self, campus: str = "0002") -> Dict[str, Any]:
        """
        获取空教室统计信息

        Args:
            campus: 校区代码(0001: 泉州校区, 0002: 厦门校区, 0003: 龙舟池校区)，默认为厦门校区

        Returns:
            Dict[str, Any]: 包含空教室统计的字典, 包含建筑ID
        """
        url = f"{self.BASE_URL}/academic/schoolroom/count"
        params = {
            "campus": campus,
            "name": ""
        }

        try:
            headers = self._get_headers()
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取空教室统计失败: {str(e)}",
                "data": None
            }

    async def get_empty_classroom_status(self, build_id: str, day: Optional[str] = None, campus: str = "0002") -> Dict[str, Any]:
        """
        获取教室详细信息，包括各个时段的使用状态

        Args:
            build_id: 建筑ID，例如"0002011"代表C4楼
            day: 日期，格式为"yyyy-MM-dd"，默认为当天
            campus: 校区代码(0001: 泉州校区, 0002: 厦门校区, 0003: 龙舟池校区)，默认为厦门校区

        Returns:
            Dict[str, Any]: 包含教室详细信息的字典
        """
        url = f"{self.BASE_URL}/academic/schoolroom/analysis"

        params = {
            "campus": campus,
            "buildId": build_id,
        }

        # 如果未指定日期，默认使用当天日期
        if day:
            params["day"] = day
        else:
            today = datetime.now().strftime("%Y-%m-%d")
            params["day"] = today

        try:
            headers = self._get_headers()
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取教室详情失败: {str(e)}",
                "data": None
            }

    async def get_grade(self, school_year: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
        """
        获取课程成绩信息

        Parameters:
            school_year: 学年，可选，默认为当前学年, 2024-2025
            semester: 学期，可选，默认为当前学期, 一 或 二
        Returns:
            Dict[str, Any]: 包含课程成绩信息的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/score/account"

            headers = self._get_headers()

            params = {
                "account": STUDENT_ID,
                "schoolYear": school_year,
                "semester": semester
            }

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取课程成绩失败: {str(e)}",
                "data": None
            }

    async def get_college_list(self) -> Dict[str, Any]:
        """
        获取学院列表

        Returns:
            Dict[str, Any]: data:[{"wbwccollegenum": college_id, "nawbwccollegenameme": college_name}]
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/college"
            headers = self._get_headers()

            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取学院列表失败: {str(e)}",
                "data": None
            }

    async def get_class_timetable(self, class_id: str, school_year: Optional[str] = None, semester: Optional[str] = None, is_overseas: bool = False) -> Dict[str, Any]:
        """
        获取班级课表信息

        Args:
            class_id: 班级ID, 例如: 2024级会展经济与管理1班
            school_year: 学年, 例如: 2024-2025
            semester: 上学期: 一, 下学期: 二
            is_overseas: 是否为境外生班级
        Returns:
            Dict[str, Any]: 包含班级课表信息的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester

            if is_overseas:
                class_id += "(境外生)"
                
            url = f"{self.BASE_URL}/academic/schedule/classTimetable"

            headers = self._get_headers({"timetableType": "班级课表查询"})

            params = {
                "KKXN": school_year,  # 学年
                "KKXQ": semester,     # 学期
                "ZYBJDM": class_id     # 专业班级代码
            }

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取班级课表失败: {str(e)}",
                "data": None
            }

    async def get_teacher_list(self, college_id: str) -> Dict[str, Any]:
        """
        获取教师列表

        Args:
            college_id: 学院ID

        Returns:
            Dict[str, Any]: 包含教师列表信息的字典, data:[{"num": teacher_id, "name": teacher_name}]
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/teachers"
            headers = self._get_headers()

            params = {
                "XYDM": college_id,
                "Type": "weimeng-sends"
            }

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取教师列表失败: {str(e)}",
                "data": None
            }

    async def get_teacher_timetable(self, teacher_id: str, school_year: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
        """
        获取教师课表信息

        Args:
            teacher_id: 教师ID
            school_year: 学年, 例如: 2024-2025
            semester: 上学期: 一, 下学期: 二

        Returns:
            Dict[str, Any]: 包含教师课表信息的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/schedule/teacherTimetable"

            headers = self._get_headers({"timetableType": "教师课表查询"})

            params = {
                "KKXN": school_year,  # 学年
                "KKXQ": semester,     # 学期
                "id": teacher_id       # 教师ID
            }
            
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取教师课表失败: {str(e)}",
                "data": None
            }
    
    async def get_course_list(self) -> Dict[str, Any]:
        """
        获取课程列表
        
        Returns:
            Dict[str, Any]: 包含课程列表的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/courseNames"
            headers = self._get_headers()
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取课程列表失败: {str(e)}",
                "data": None
            }
    
    async def get_course_timetable(self, course_name: str, school_year: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
        """
        获取课程课表信息
        
        Args:
            course_name: 课程名称
            school_year: 学年, 例如: 2024-2025
            semester: 上学期: 一, 下学期: 二
            
        Returns:
            Dict[str, Any]: 包含课程课表信息的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/schedule/selectCourse"
            
            headers = self._get_headers()
            
            params = {
                "year": school_year,
                "semester": semester,
                "courseName": course_name
            }
            
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取课程课表失败: {str(e)}",
                "data": None
            }
    
    async def get_building_list(self, campus: Optional[str] = "厦门校区") -> Dict[str, Any]:
        """
        获取建筑列表
        
        Args:
            campus: 校区: 厦门校区, 泉州校区, 龙舟池校区

        Returns:
            Dict[str, Any]: 包含建筑列表的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/buildByCampus"
            headers = self._get_headers()
            
            params = {"campus": campus}

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取建筑列表失败: {str(e)}",
                "data": None
            }
    
    async def get_classroom_list(self, campus: Optional[str] = "厦门校区", build: Optional[str] = None) -> Dict[str, Any]:
        """
        获取教室列表
        
        Args:
            campus: 校区: 厦门校区, 泉州校区, 龙舟池校区
            build: 建筑名称
            
        Returns:
            Dict[str, Any]: 包含教室列表的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/roomsByCampus"
            headers = self._get_headers()
            
            params = {
                "campus": campus,
                "build": build
            }

            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取教室列表失败: {str(e)}",
                "data": None
            }
    
    
    async def get_rooms_timetable(self, school_year: Optional[str] = None, semester: Optional[str] = None, campus: Optional[str] = "厦门校区", build_name: Optional[str] = None, room_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取教室课表信息
        
        Args:
            school_year: 学年
            semester: 学期
            campus: 校区
            build_name: 建筑名称
            room_id: 教室ID
            
        Returns:
            Dict[str, Any]: 包含教室课表信息的字典
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/schedule/roomsTimetable"
            
            headers = self._get_headers()
            
            params = {
                "KKXN": school_year,  # 学年
                "KKXQ": semester,     # 学期
                "campus": campus,      # 校区
                "build": build_name,   # 建筑名称
                "room": room_id        # 教室ID
            }
            
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取教室课表失败: {str(e)}",
                "data": None
            }

# 创建一个单例实例
school_info_service = SchoolInfoService()