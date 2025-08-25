#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный скрипт для запуска Telegram бота и веб-интерфейса одновременно
"""

import asyncio
import subprocess
import sys
import os
import signal
import time
import threading
from pathlib import Path

# Глобальные переменные для процессов
bot_process = None
web_process = None
running = True

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    global running, bot_process, web_process
    print("\n🛑 Получен сигнал завершения...")
    running = False
    
    if bot_process:
        print("⏹️ Останавливаю бота...")
        bot_process.terminate()
        try:
            bot_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            bot_process.kill()
    
    if web_process:
        print("⏹️ Останавливаю веб-интерфейс...")
        web_process.terminate()
        try:
            web_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            web_process.kill()
    
    print("✅ Все процессы остановлены")
    sys.exit(0)

def check_dependencies():
    """Проверка и установка зависимостей"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ Файл requirements.txt не найден!")
        return False
    
    print("📦 Проверяю зависимости...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Ошибка установки зависимостей: {result.stderr}")
            return False
        print("✅ Зависимости установлены")
        return True
    except Exception as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        return False

def check_config():
    """Проверка конфигурации"""
    config_file = Path("config.json")
    env_file = Path(".env")
    
    if not config_file.exists():
        print("❌ Файл config.json не найден!")
        return False
    
    if not env_file.exists():
        print("⚠️ Файл .env не найден. Создайте его на основе .env.example")
        print("💡 Или настройте бота через веб-интерфейс")
    
    return True

def start_bot():
    """Запуск бота в отдельном процессе"""
    global bot_process
    try:
        print("🤖 Запускаю Telegram бота...")
        bot_process = subprocess.Popen([sys.executable, "bot.py"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        return False

def start_web_interface():
    """Запуск веб-интерфейса в отдельном процессе"""
    global web_process
    try:
        print("🌐 Запускаю веб-интерфейс...")
        web_process = subprocess.Popen([sys.executable, "config_editor.py"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска веб-интерфейса: {e}")
        return False

def monitor_processes():
    """Мониторинг процессов"""
    global running, bot_process, web_process
    
    while running:
        time.sleep(2)
        
        # Проверяем бота
        if bot_process and bot_process.poll() is not None:
            print("⚠️ Бот неожиданно остановился")
            stdout, stderr = bot_process.communicate()
            if stderr:
                print(f"Ошибка бота: {stderr}")
            if running:  # Перезапускаем только если не завершаемся
                print("🔄 Перезапускаю бота...")
                start_bot()
        
        # Проверяем веб-интерфейс
        if web_process and web_process.poll() is not None:
            print("⚠️ Веб-интерфейс неожиданно остановился")
            stdout, stderr = web_process.communicate()
            if stderr:
                print(f"Ошибка веб-интерфейса: {stderr}")
            if running:  # Перезапускаем только если не завершаемся
                print("🔄 Перезапускаю веб-интерфейс...")
                start_web_interface()

def main():
    """Главная функция"""
    global running
    
    # Устанавливаем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Запуск системы управления Telegram ботом")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    # Проверяем конфигурацию
    if not check_config():
        sys.exit(1)
    
    # Запускаем процессы
    if not start_bot():
        sys.exit(1)
    
    if not start_web_interface():
        if bot_process:
            bot_process.terminate()
        sys.exit(1)
    
    # Даем время на запуск
    time.sleep(3)
    
    print("\n✅ Система запущена успешно!")
    print("🤖 Telegram бот: Активен")
    print("🌐 Веб-интерфейс: http://localhost:5001")
    print("\n💡 Управляйте ботом через веб-интерфейс")
    print("⏹️ Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем мониторинг в отдельном потоке
    monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
    monitor_thread.start()
    
    # Основной цикл
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()