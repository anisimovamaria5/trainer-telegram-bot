from ast import Dict
import json
import os
from typing import List, Optional, Tuple
from datetime import datetime, time, timedelta
from urllib.parse import urlencode
import aiohttp


class YandexCalendarAPI:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token: Optional[str] = None
        self.base_url = "https://api.calendar.yandex.ru/v3"
        self.token_file = "yandex_token.json"

        self._load_token()
    
    
    def _load_token(self):
        """Загружаем токен из файла"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.token = data.get('access_token')
                    if self.token:
                        print(f"✅ Токен загружен из файла")
            except Exception as e:
                print(f"❌ Ошибка загрузки токена: {e}")


    def _save_token(self):
        """Сохраняем токен в файл"""
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                data = {
                    'access_token': self.token,
                    'client_id': self.client_id
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✅ Токен сохранен в файл")
        except Exception as e:
            print(f"❌ Ошибка сохранения токена: {e}")

            
    async def get_auth_url(self) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        return f"https://oauth.yandex.ru/authorize?{urlencode(params)}"


    async def get_token(self, code: str) -> bool:
        """Получаем токен"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://oauth.yandex.ru/token", 
                data=data
                ) as resp:
                    resp.raise_for_status()
                    json_data = await resp.json()
                    self.token = json_data.get("access_token")
                    self._save_token()
                    return True


    async def create_event(self, event_data) -> Dict:
        """Создаем событие в календаре"""

        headers = {
            "Authorization": f'OAuth {self.token}',
            "Content-Type": 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/calendars/primary/events',
                headers=headers,
                json=event_data
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
            
    
    async def get_busy_periods(self, date:datetime) -> List[Dict]:
        """Проверяем занятые периоды"""

        start_datetime = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_datetime = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        start = start_datetime.isoformat() + 'Z'
        end = end_datetime.isoformat() + 'Z'

        connector = aiohttp.TCPConnector(ssl=self.ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                f"{self.base_url}/calendars/primary/events",
                headers={'Authorization': f'OAuth {self.token}'},
                params={
                    "start":start, 
                    "end":end,
                    "timeZone": "Asia/Yekaterinburg"
                    }
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
            
    
    async def get_available_slots(self, date: datetime.date) -> List[Tuple[time, time]]:
        """Получаем доступные слоты"""

        busy_events = await self.get_busy_periods(date)
        slots = []

        start_time = datetime.combine(date, time(8, 0))
        end_time = datetime.combine(date, time(20, 0))

        current = start_time
        while current < end_time:
            slot_end = current + timedelta(hours=1)
            is_available = True
            for event in busy_events:
                event_start = datetime.fromisoformat(event['start']['dateTime'])
                event_end = datetime.fromisoformat(event['end']['dateTime'])
                if not (slot_end <= event_start or current >= event_end):
                    is_available = False
                    break

            if is_available:
                slots.append((current.time(), slot_end.time()))
            current = slot_end

        return slots

