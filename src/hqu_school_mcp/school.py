import httpx
from typing import Dict, Any, Optional, List
import asyncio

class SchoolInfoService:
    """华侨大学校园信息服务类"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    async def get_empty_classroom_count(self, campus: str = "0002") -> Dict[str, Any]:
        """
        获取空教室统计信息
        
        Args:
            campus: 校区代码(0001: 泉州校区, 0002: 厦门校区, 0003: 龙舟池校区)，默认为厦门校区
            
        Returns:
            Dict[str, Any]: 包含空教室统计的字典
        """
        url = "https://apps.hqu.edu.cn/academic/schoolroom/count"
        
        params = {
            "campus": campus,
            "name": ""
        }
        
        try:
            response = await self.client.get(url, params=params)
            data = response.json()
            return data
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取空教室统计失败: {str(e)}",
                "data": None
            }
            
    async def get_empty_classroom_status(self, build_id: str, day: Optional[str] = None, campus: str = "0002",) -> Dict[str, Any]:
        """
        获取教室详细信息，包括各个时段的使用状态
        
        Args:
            build_id: 建筑ID，可选，例如"0002011"代表C4楼
            day: 日期，可选，格式为"yyyy-MM-dd"，默认为当天
            campus: 校区代码(0001: 泉州校区, 0002: 厦门校区, 0003: 龙舟池校区)，默认为厦门校区
            
        Returns:
            Dict[str, Any]: 包含教室详细信息的字典
        """
        url = "https://apps.hqu.edu.cn/academic/schoolroom/analysis"
        
        params = {
            "campus": campus,
            "buildId": build_id,
        }
        
        # 如果未指定日期，默认使用当天日期
        if day:
            params["day"] = day
        else:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            params["day"] = today
            
        try:
            response = await self.client.get(url, params=params)
            data = response.json()
            return data
        except Exception as e:
            return {
                "code": "9999",
                "msg": f"获取教室详情失败: {str(e)}",
                "data": None
            }

# 创建一个单例实例
school_info_service = SchoolInfoService()

