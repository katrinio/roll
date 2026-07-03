# MVP

> Найти нужную пленку по памяти: человек, место, событие, настроение — спустя месяцы.

## Сценарий

```bash
rl init ~/Pictures/plenka   # один раз
rl stock add                # купил пленку → в запас
rl load                     # зарядил в камеру → roll создан, спросит теги/особенности
rl stock process            # или: rl stock failed
rl search kir balcony       # через полгода — нашел
```

## Команды

| Задача | Команда |
|---|---|
| Запас пленки | `stock add`, `stock list` |
| Ролл | `load` (`--manual` — без запаса), `stock process`, `stock failed` |
| Дозаполнить ролл | `features add`, `tags add` |
| Найти / посмотреть | `search`, `scan`, `status`, `stats [-v]`, `vocab` |
| Гигиена архива | `doctor [--fix] [-v]`, `normalize [--tags]` |
| Массово | `batch process` |

## Не входит в MVP

sync между машинами · облако · веб-интерфейс · миграция старых форматов · обработка изображений

## Правило

Не помогает быстрее найти пленку по памяти — не входит в MVP.