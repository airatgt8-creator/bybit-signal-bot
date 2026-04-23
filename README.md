# Bybit Signal Bot

Это не «бот, который знает будущее». Это сканер сигналов для раннего движения с уведомлениями в Telegram и опциональной покупкой на Bybit spot.

## Что делает

1. Читает новые и активные токены через DEX Screener API.
2. Отбирает монеты по жёстким фильтрам: ликвидность, 5m объём, движение цены, соотношение buys/sells.
3. Пытается сопоставить сигнал с тикером из твоего watchlist на Bybit.
4. Отправляет сигнал в Telegram.
5. Опционально ставит рыночный spot-ордер на Bybit, только если `ENABLE_AUTO_BUY=true`.

## Важно

- DEX Screener API даёт публичные данные по токенам и парам, включая latest token profiles, boosted tokens, paid orders и pair data. В справке также указаны rate limits: 60 rpm для профилей/boosts и 300 rpm для pair endpoint. 
- Bybit V5 поддерживает market data (`Get Instruments Info`, `Get Tickers`, `Get Kline`) и создание ордеров через `Place Order`.
- Для X сейчас нужен доступ через X Developer Platform; доступ к API завязан на enrolment и биллинг, поэтому модуль здесь оставлен опциональным.

## Установка

### 1. Установи Python 3.11+
Проверь:

```bash
python --version
```

### 2. Открой папку проекта

```bash
cd /path/to/bybit_signal_bot
```

### 3. Создай виртуальное окружение

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Установи зависимости

```bash
pip install -r requirements.txt
```

### 5. Создай `.env`
Скопируй файл `.env.example` в `.env` и заполни значения.

Windows:
```bash
copy .env.example .env
```

Linux / macOS:
```bash
cp .env.example .env
```

### 6. Запусти

```bash
python main.py
```

## Что и где вставить

### Telegram bot token
Вставь в файл `.env` сюда:

```env
TELEGRAM_BOT_TOKEN=твой_токен
TELEGRAM_CHAT_ID=твой_chat_id
```

### Bybit API ключи
Вставь в `.env` сюда:

```env
BYBIT_API_KEY=твой_key
BYBIT_API_SECRET=твой_secret
BYBIT_TESTNET=true
ENABLE_AUTO_BUY=false
```

Сначала оставь `ENABLE_AUTO_BUY=false`.

## Как включить автопокупку

1. Проверь, что бот неделю шлёт нормальные сигналы.
2. Потом в `.env` поменяй:

```env
ENABLE_AUTO_BUY=true
BYBIT_TESTNET=true
ORDER_USDT_PER_TRADE=10
MAX_OPEN_POSITIONS=1
STOP_LOSS_PCT=0.08
TAKE_PROFIT_PCT=0.18
```

3. Только потом переходи на `BYBIT_TESTNET=false`.

## Логика фильтров

Сигнал проходит, если одновременно:
- ликвидность >= `MIN_LIQUIDITY_USD`
- 5m volume >= `MIN_VOLUME_5M_USD`
- 5m price change >= `MIN_PRICE_CHANGE_5M_PCT`
- 1h price change <= `MAX_PRICE_CHANGE_1H_PCT`
- ratio buys/sells >= `MIN_BUY_SELL_RATIO`
- unique buyers >= `MIN_UNIQUE_BUYERS`

## Ограничения

- Совсем ранние микро-мемкойны часто не торгуются на Bybit spot. Тогда бот отправит сигнал, но не купит.
- Для X-модуля нужен доступ в X Developer Platform.
- Это не гарантия прибыли. Бот режет риск, а не «угадывает» рынок.
