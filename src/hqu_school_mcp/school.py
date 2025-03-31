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
        """
        初始化SchoolInfoService实例
        
        创建异步HTTP客户端，并设置初始学年和学期信息
        """
        self.client = httpx.AsyncClient()
        self.current_school_year = self._get_current_semester()[0]
        self.current_semester = self._get_current_semester()[1]
        self._jwt_token = None

    async def __aenter__(self):
        """
        异步上下文管理器入口方法
        
        Returns:
            SchoolInfoService: 当前服务实例
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        异步上下文管理器退出方法，关闭异步HTTP客户端
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯
        """
        await self.client.aclose()

    def _get_current_semester(self) -> tuple:
        """
        计算当前学期
        
        基于当前日期计算当前学年和学期
        
        Returns:
            tuple[str, str]: 包含(学年, 学期)的元组，如("2023-2024", "一")
        """
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
        
        通过微信OpenID获取访问学校API所需的JWT令牌
        
        Args:
            refresh (bool): 是否强制刷新令牌，默认为False
            
        Returns:
            str: JWT令牌字符串
            
        Raises:
            ValueError: 当环境变量中没有OPENID或获取令牌失败时抛出
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

    async def _get_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        获取请求头
        
        生成API请求所需的标准请求头，包括内容类型和授权信息
        
        Args:
            extra_headers (Optional[Dict[str, str]]): 额外的请求头键值对，默认为None
            
        Returns:
            Dict[str, str]: 合并后的请求头字典
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json;charset=utf-8"
        }
        
        headers["Authorization"] = await self._get_jwt_token()
        
        if extra_headers:
            headers.update(extra_headers)
            
        return headers

    async def get_empty_classroom_count(self, campus: str) -> Dict[str, Any]:
        """
        获取空教室统计信息
        
        查询指定校区的空教室数量统计信息
        
        Args:
            campus (str): 校区代码，可选值为["0001": 泉州校区, "0002": 厦门校区, "0003": 龙舟池校区]，默认为"0002"(厦门校区)
            
        Returns:
            Dict[str, Any]: 包含空教室统计的字典，包含建筑ID和数量信息
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        url = f"{self.BASE_URL}/academic/schoolroom/count"
        params = {
            "campus": campus,
            "name": ""
        }

        try:
            headers = await self._get_headers()
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取空教室统计失败: {str(e)}",
                "data": None
            }

    async def get_empty_classroom_status(self, build_id: str, day: str, campus: str) -> Dict[str, Any]:
        """
        获取教室详细信息
        
        查询特定建筑在指定日期的教室使用状态详情，包括各个时段的使用情况
        
        Args:
            build_id (str): 建筑ID，例如"0002011"代表C4楼
            day (Optional[str]): 日期，格式为"yyyy-MM-dd"，默认为当天
            campus (str): 校区代码，可选值为["0001": 泉州校区, "0002": 厦门校区, "0003": 龙舟池校区]，默认为"0002"(厦门校区)
            
        Returns:
            Dict[str, Any]: 包含教室详细使用信息的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
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
            headers = await self._get_headers()
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
        
        查询指定学年和学期的课程成绩数据
        
        Args:
            school_year (Optional[str]): 学年，格式如"2023-2024"，默认为当前学年
            semester (Optional[str]): 学期，可选值为"一"(上学期)或"二"(下学期)，默认为当前学期
            
        Returns:
            Dict[str, Any]: 包含课程成绩信息的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/score/account"

            headers = await self._get_headers()

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
        
        查询华侨大学所有学院的列表信息
        
        Returns:
            Dict[str, Any]: 包含学院列表的字典，格式为data:[{"wbwccollegenum": college_id, "nawbwccollegenameme": college_name}]
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/college"
            headers = await self._get_headers()

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
        
        查询指定班级在特定学年学期的课程表信息
        
        Args:
            class_id (str): 班级ID，例如: "2024级会展经济与管理1班"
            school_year (Optional[str]): 学年，格式如"2023-2024"，默认为当前学年
            semester (Optional[str]): 学期，可选值为"一"(上学期)或"二"(下学期)，默认为当前学期
            is_overseas (bool): 是否为境外生班级，默认为False
            
        Returns:
            Dict[str, Any]: 包含班级课表信息的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
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

            headers = await self._get_headers()

            params = {
                "KKXN": school_year,  # 学年
                "KKXQ": semester,     # 学期
                "ZYBJDM": class_id,     # 专业班级代码
                "timetableType": "班级课表查询"
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
        
        查询指定学院的教师列表信息
        
        Args:
            college_id (str): 学院ID
            
        Returns:
            Dict[str, Any]: 包含教师列表的字典，格式为data:[{"num": teacher_id, "name": teacher_name}]
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/teachers"
            headers = await self._get_headers()

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
        
        查询指定教师在特定学年学期的课程表信息
        
        Args:
            teacher_id (str): 教师ID
            school_year (Optional[str]): 学年，格式如"2023-2024"，默认为当前学年
            semester (Optional[str]): 学期，可选值为"一"(上学期)或"二"(下学期)，默认为当前学期
            
        Returns:
            Dict[str, Any]: 包含教师课表信息的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/schedule/teacherTimetable"

            headers = await self._get_headers()

            params = {
                "KKXN": school_year,  # 学年
                "KKXQ": semester,     # 学期
                "ZYBJDM": teacher_id,       # 教师ID
                "timetableType": "教师课表查询"
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
        
        查询学校提供的所有课程列表
        
        Returns:
            Dict[str, Any]: 包含课程列表的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/courseNames"
            headers = await self._get_headers()
            
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
        
        查询指定课程在特定学年学期的课表信息
        
        Args:
            course_name (str): 课程名称
            school_year (Optional[str]): 学年，格式如"2023-2024"，默认为当前学年
            semester (Optional[str]): 学期，可选值为"一"(上学期)或"二"(下学期)，默认为当前学期
            
        Returns:
            Dict[str, Any]: 包含课程课表信息的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/schedule/selectCourse"
            
            headers = await self._get_headers()
            
            params = {
                "year": school_year,
                "term": semester,
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
    
    async def get_building_list(self, campus: str) -> Dict[str, Any]:
        """
        获取建筑列表
        
        查询指定校区的所有建筑列表
        
        Args:
            campus (Optional[str]): 校区名称，可选值为["厦门校区", "泉州校区", "龙舟池校区"]，默认为"厦门校区"
            
        Returns:
            Dict[str, Any]: 包含建筑列表的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/buildByCampus"
            headers = await self._get_headers()
            
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
    
    async def get_classroom_list(self, campus: str, build: str) -> Dict[str, Any]:
        """
        获取教室列表
        
        查询指定校区和建筑的所有教室列表
        
        Args:
            build (str): 建筑名称
            campus (Optional[str]): 校区名称，可选值为["厦门校区", "泉州校区", "龙舟池校区"]，默认为"厦门校区"
            
        Returns:
            Dict[str, Any]: 包含教室列表的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            url = f"{self.BASE_URL}/academic/schedule/roomsByCampus"
            headers = await self._get_headers()
            
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
    
    
    async def get_rooms_timetable(self, campus: str, build_name: str, room_id: str, school_year: Optional[str] = None, semester: Optional[str] = None) -> Dict[str, Any]:
        """
        获取教室课表信息
        
        查询特定教室在指定学年学期的课表信息
        
        Args:
            school_year (Optional[str]): 学年，格式如"2023-2024"，默认为当前学年
            semester (Optional[str]): 学期，可选值为"一"(上学期)或"二"(下学期)，默认为当前学期
            campus (Optional[str]): 校区名称，可选值为["厦门校区", "泉州校区", "龙舟池校区"]，默认为"厦门校区"
            build_name (Optional[str]): 建筑名称，默认为None，需要从get_building_list()中获取
            room_id (Optional[str]): 教室ID，默认为None，需要从get_classroom_list()中获取
            
        Returns:
            Dict[str, Any]: 包含教室课表信息的字典
            
        Raises:
            Exception: 当API请求失败时捕获并返回错误信息
        """
        try:
            jwt_token = await self._get_jwt_token()
            
            if school_year is None:
                school_year = self.current_school_year

            if semester is None:
                semester = self.current_semester
                
            url = f"{self.BASE_URL}/academic/schedule/roomsTimetable"
            
            headers = await self._get_headers()
            
            params = {
                "KKXN": school_year,  # 学年
                "KKXQ": semester,     # 学期
                "campus": campus,      # 校区
                "build": build_name,   # 建筑名称
                "room": room_id,        # 教室ID
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