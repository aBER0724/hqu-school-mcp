import re
import httpx
import asyncio
import os
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

DEFAULT_API_URL = "https://api.sends.cc"

# 加载.env文件
load_dotenv()

# 从环境变量获取token
API_TOKEN = os.getenv("SENDS_API_TOKEN")
if not API_TOKEN:
    raise ValueError("请在.env文件中设置SENDS_API_TOKEN")


class StudentDataService:
    def __init__(self, api_url: str = DEFAULT_API_URL):
        self.api_url = api_url
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

    def _get_current_semester(self) -> str:
        """计算当前学期，格式为 '2024-2025-2'"""
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # 获取学年
        if current_month >= 9:
            academic_year = f"{current_year}-{current_year + 1}"
        else:
            academic_year = f"{current_year - 1}-{current_year}"

        # 判断学期
        if 2 <= current_month <= 7:
            semester_num = 2  # 下学期
        else:
            semester_num = 1  # 上学期

        return f"{academic_year}-{semester_num}"

    async def get_schedule(self, semester: Optional[str] = None) -> Dict[str, Any]:
        """获取学生课表数据"""
        if semester is None:
            semester = self._get_current_semester()

        headers = self._get_headers()
        response = await self.client.get(
            f"{self.api_url}/service/school/schedule",
            params={"semester": semester},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def get_credit(self) -> Dict[str, Any]:
        """获取学生学分数据"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.api_url}/service/school/credit",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def get_gpa(self) -> Dict[str, Any]:
        """获取学生GPA数据"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.api_url}/service/school/gpa",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def get_grade(self) -> Dict[str, Any]:
        """获取学生成绩数据"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.api_url}/service/school/grade",
            headers=headers
        )
        response.raise_for_status()
        return response.json()


# Create a singleton instance
student_data_service = StudentDataService()
