import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Создает сервис Google Calendar с фиксированным redirect_uri"""
    creds = None
    
    # УДАЛИТЕ старый token.json чтобы начать заново
    if os.path.exists('token.json'):
        os.remove('token.json')
    
    # ФИКСИРОВАННЫЙ порт и URI
    REDIRECT_PORT = 8080
    REDIRECT_URI = f'http://localhost:{REDIRECT_PORT}/'
    
    print(f"Используется фиксированный redirect_uri: {REDIRECT_URI}")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    creds = flow.run_local_server(
        port=REDIRECT_PORT,
        host='localhost',
        authorization_prompt_message='Откройте эту ссылку в браузере: {url}',
        success_message='✅ Авторизация успешна! Вы можете закрыть окно.',
        open_browser=True
    )
    
    # Сохраняем токен
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("✅ Токен сохранен в token.json")
    
    # Создаем сервис
    service = build('calendar', 'v3', credentials=creds)
    return service

# Тестируем
if __name__ == '__main__':
    service = get_calendar_service()
    print("✅ Google Calendar API подключен успешно!")