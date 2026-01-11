import os
import pickle
from datetime import datetime, time, timedelta
from typing import List, Tuple, Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarAPI:
    def __init__(self):
        self.creds = None
        self.service = None
        self.token_file = 'google_token.pickle'
        self.credentials_file = 'credentials.json'
        self._authenticate()
    
    def _authenticate(self):
        """Аутентификация в Google API"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Файл {self.credentials_file} не найден. "
                        f"Скачайте его из Google Cloud Console: "
                        f"https://console.cloud.google.com/"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('calendar', 'v3', credentials=self.creds)
        print("✅ Google Calendar API инициализирован")
    
    async def get_auth_url(self) -> str:
        """Получить URL для авторизации (для совместимости с интерфейсом)"""
        return "https://accounts.google.com/o/oauth2/auth"
    
    async def get_token(self, code: str) -> bool:
        """Получить токен (для совместимости с интерфейсом)"""
        return True
    
    async def create_event(self, event_data: Dict) -> Dict:
        """Создать событие в календаре"""
        try:
            event = {
                'summary': event_data.get('summary', 'Запись'),
                'description': 'Запись из Telegram бота',
                'start': {
                    'dateTime': event_data['start']['dateTime'],
                    'timeZone': event_data['start'].get('timeZone', 'Europe/Moscow'),
                },
                'end': {
                    'dateTime': event_data['end']['dateTime'],
                    'timeZone': event_data['end'].get('timeZone', 'Europe/Moscow'),
                },
            }
            
            event_result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            print(f"✅ Событие создано: {event_result.get('id')}")
            return event_result
            
        except HttpError as error:
            print(f'❌ Ошибка создания события: {error}')
            raise Exception(f"Ошибка Google Calendar: {error}")
    
    async def get_busy_periods(self, date: datetime) -> List[Dict]:
        """Получить занятые периоды на указанную дату"""
        try:

            time_min = datetime(date.year, date.month, date.day, 0, 0, 0).isoformat() + 'Z'
            time_max = datetime(date.year, date.month, date.day, 23, 59, 59).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"📅 Найдено событий: {len(events)}")
            return events
            
        except HttpError as error:
            print(f'❌ Ошибка Google Calendar API: {error}')
            return []
    
    async def get_available_slots(self, date: datetime.date) -> List[Tuple[time, time]]:
        """Получить свободные слоты на указанную дату"""
        try:
            events = await self.get_busy_periods(date)
            slots = []
            
            start_time = datetime.combine(date, time(8, 0))
            end_time = datetime.combine(date, time(20, 0))
            
            busy_periods = []
            for event in events:
                start_str = event['start'].get('dateTime', event['start'].get('date'))
                end_str = event['end'].get('dateTime', event['end'].get('date'))
                
                if start_str and end_str:
                    event_start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                    busy_periods.append((event_start, event_end))
            
            current = start_time
            while current < end_time:
                slot_end = current + timedelta(hours=1)
                is_available = True
                
                for busy_start, busy_end in busy_periods:
                    if not (slot_end <= busy_start or current >= busy_end):
                        is_available = False
                        break
                
                if is_available:
                    slots.append((current.time(), slot_end.time()))
                
                current = slot_end
            
            print(f"✅ Свободных слотов найдено: {len(slots)}")
            return slots
            
        except Exception as e:
            print(f"❌ Ошибка при получении слотов: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def view_all_appointments(self) -> List[Dict]:
        """Показать все события"""
        try:
            time_min = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
            time_max = (datetime.now() + timedelta(days=30)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                maxResults=50
            ).execute()
            
            events = events_result.get('items', [])
            
            for event in events:
                event['created_at'] = event.get('created', 'Не известно')
            
            return events
            
        except HttpError as error:
            print(f'❌ Ошибка: {error}')
            return []
    
    @property
    def token(self):
        """Свойство token для совместимости"""
        return self.creds.token if self.creds else None