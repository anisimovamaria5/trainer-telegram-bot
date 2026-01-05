# 🏋️‍♂️ Тренерский Telegram Бот

Бот для записи на индивидуальные тренировки с интеграцией Яндекс.Календаря.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-3.x-blue.svg)


## ✨ Возможности

- 📅 Просмотр свободных слотов на тренировки
- ✅ Онлайн запись на удобное время
- 🔄 Синхронизация с Яндекс.Календарем
- 💰 Просмотр цен на услуги
- 📍 Контакты и адрес зала
- 🔐 Авторизация через Яндекс OAuth

trainer-telegram-bot/
├── main.py              # Точка входа
├── config.py           # Конфигурация
├── keyboards.py        # Клавиатуры
├── states.py          # Состояния FSM
├── yandex_calendar.py # Яндекс.Календарь API
├── user_handlers.py   # Обработчики команд
├── other_handlers.py  # Основные обработчики
├── requirements.txt   # Зависимости
└── README.md         # Документация
