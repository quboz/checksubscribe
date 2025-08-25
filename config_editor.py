#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-интерфейс для редактирования настроек бота
"""

import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

CONFIG_FILE = 'config.json'

def load_config():
    """Загрузка конфигурации из файла"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_config(config):
    """Сохранение конфигурации в файл"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def config_editor():
    if request.method == 'POST':
        # Получаем данные из формы
        channels = []
        
        # Обрабатываем каналы
        channel_count = 0
        while f'channel_id_{channel_count}' in request.form:
            if request.form[f'channel_id_{channel_count}'].strip():
                channels.append({
                    'id': request.form[f'channel_id_{channel_count}'],
                    'url': request.form[f'channel_url_{channel_count}'],
                    'name': request.form[f'channel_name_{channel_count}']
                })
            channel_count += 1
        
        config = {
            'bot_token': request.form['bot_token'],
            'channels': channels,
            'messages': {
                'welcome_message': request.form['welcome_message'],
                'app_info_message': request.form['app_info_message'],
                'not_subscribed_message': request.form['not_subscribed_message']
            },
            'buttons': {
                'channel_button': request.form['channel_button'],
                'check_subscription': request.form['check_subscription']
            },
            'styling': {
                'use_emojis': 'use_emojis' in request.form,
                'theme': request.form['theme']
            }
        }
        
        # Сохраняем конфигурацию
        if save_config(config):
            flash('Настройки успешно сохранены!', 'success')
        else:
            flash('Ошибка при сохранении настроек!', 'error')
        return redirect(url_for('config_editor'))
    
    # Загружаем текущую конфигурацию для отображения
    config = load_config()
    return render_template('config_editor.html', config=config)

if __name__ == '__main__':
    # Создаем папку templates если её нет
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Веб-интерфейс для настройки бота запущен!")
    print("Откройте в браузере: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)