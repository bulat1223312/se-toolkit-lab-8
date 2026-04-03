#!/usr/bin/env python3
"""Suggest next steps for fixing LLM connection."""

print("=" * 60)
print("РЕЗЮМЕ ПРОБЛЕМЫ И РЕКОМЕНДАЦИИ")
print("=" * 60)

print("""
## Проблема
OAuth токен для qwen-code-api истек (1 апреля 2026).
Refresh токена требует прохождения капчи (WAF).

## Текущий статус Task 2
✅ Nanobot gateway запущен
✅ WebChat канал включен
✅ MCP серверы подключены (lms: 9 tools, webchat: 1 tool)
✅ Flutter клиент доступен на http://10.93.25.49:42002/flutter
✅ WebSocket endpoint работает: ws://localhost:42002/ws/chat
❌ LLM API не отвечает (OAuth токен истек)

## Варианты решения

### Вариант 1: Обновить OAuth токен вручную (РЕКОМЕНДУЕТСЯ)
На VM выполните:
```bash
ssh root@10.93.25.49
qwen login
# Следуйте инструкциям для аутентификации через браузер
# После успешного входа OAuth токен обновится автоматически

# Перезапустите qwen-code-api
cd /root/se-toolkit-lab-8
docker compose --env-file .env.docker.secret restart qwen-code-api

# Проверьте
curl -s http://localhost:42005/health
```

### Вариант 2: Использовать DashScope API напрямую
Измените конфигурацию nanobot для прямого подключения к DashScope:
1. В .env.docker.secret измените LLM_API_BASE_URL на DashScope endpoint
2. Установите LLM_API_KEY в ваш DashScope API ключ
3. Перезапустите nanobot

### Вариант 3: Использовать другой LLM провайдер
Настройте nanobot на использование OpenAI, Anthropic или другого провайдера.

## Что уже работает
- Все сервисы Docker запущены
- Flutter клиент доступен
- WebSocket принимает соединения
- MCP инструменты подключены
- Осталось только обновить OAuth токен для LLM
""")
