#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска бота и веб-интерфейса
"""

import sys
import subprocess
import os
import json
from pathlib import Path

def check_config():
    """Проверка наличия и корректности конфигурации"""
    config_file = Path('config.json')
    env_file = Path('.env')
    
    if not config_file.exists():
        print("❌ Файл config.json не найден!")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверяем наличие токена
        bot_token = os.getenv('BOT_TOKEN') or config.get('bot_token')
        if not bot_token or bot_token == 'YOUR_BOT_TOKEN_HERE':
            print("❌ Токен бота не настроен!")
            print("   Укажите токен в файле .env или config.json")
            return False
        
        # Проверяем наличие канала
        channel_id = os.getenv('CHANNEL_ID') or config.get('channel_id')
        if not channel_id or channel_id == '@your_channel_username':
            print("❌ ID канала не настроен!")
            print("   Укажите ID канала в файле .env или config.json")
            return False
            
        print("✅ Конфигурация корректна")
        return True
        
    except json.JSONDecodeError:
        print("❌ Ошибка в формате config.json!")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке конфигурации: {e}")
        return False

def install_dependencies():
    """Установка зависимостей"""
    print("📦 Установка зависимостей...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def run_bot():
    """Запуск бота"""
    print("🤖 Запуск Telegram бота...")
    print("   Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, 'bot.py'])
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

def run_config_editor():
    """Запуск веб-интерфейса для настроек"""
    print("🌐 Запуск веб-интерфейса для настроек...")
    print("   Откройте в браузере: http://localhost:5001")
    print("   Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, 'config_editor.py'])
    except KeyboardInterrupt:
        print("\n🛑 Веб-интерфейс остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска веб-интерфейса: {e}")

def show_menu():
    """Показать главное меню"""
    print("\n" + "=" * 50)
    print("🤖 TELEGRAM БОТ ДЛЯ КАНАЛА WHERING")
    print("=" * 50)
    print("1. 🚀 Запустить бота")
    print("2. ⚙️  Настроить бота (веб-интерфейс)")
    print("3. 📦 Установить зависимости")
    print("4. 🔍 Проверить конфигурацию")
    print("5. 📖 Показать инструкции")
    print("0. ❌ Выход")
    print("-" * 50)

def show_instructions():
    """Показать краткие инструкции"""
    print("\n📖 КРАТКИЕ ИНСТРУКЦИИ:")
    print("-" * 30)
    print("1. Создайте бота у @BotFather")
    print("2. Создайте канал и добавьте бота как администратора")
    print("3. Настройте бота через веб-интерфейс (пункт 2)")
    print("4. Запустите бота (пункт 1)")
    print("\n📋 Подробные инструкции в файле README.md")

def main():
    """Главная функция"""
    while True:
        show_menu()
        
        try:
            choice = input("\nВыберите действие (0-5): ").strip()
            
            if choice == '0':
                print("👋 До свидания!")
                break
            elif choice == '1':
                if check_config():
                    run_bot()
                else:
                    print("\n❌ Сначала настройте конфигурацию (пункт 2)")
            elif choice == '2':
                run_config_editor()
            elif choice == '3':
                install_dependencies()
            elif choice == '4':
                check_config()
            elif choice == '5':
                show_instructions()
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

if __name__ == '__main__':
    main()