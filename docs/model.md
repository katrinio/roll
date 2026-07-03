# Model

Проект разделен на три уровня: global config → archive workspace → roll.

```
~/.config/roll/config.toml         1. global config — список архивов
        │
        ▼
~/Pictures/plenka/                  архив
├── .roll/                         2. workspace
│   ├── config.toml
│   ├── stock.toml                    запас пленки, отдельно от roll.toml
│   └── vocabulary/
│       ├── films.txt
│       ├── cameras.txt
│       ├── features.txt
│       └── keywords.txt
└── 2026/
    └── 07-03/                     3. roll
        └── roll.toml
```

| Уровень | Где | Что знает |
|---|---|---|
| Global config | `~/.config/roll/config.toml` | список архивов |
| Workspace | `<архив>/.roll/` | config, stock, словари |
| Roll | `<архив>/YYYY/MM-DD/roll.toml` | одна пленка |

`stock.toml` и `vocabulary/*.txt` решают разные задачи: stock — что физически есть на руках, словари — канонические значения для автокомплита.

## Code layout

| Путь | Зона |
|---|---|
| `filesystem.py` | низкоуровневые операции с файловой структурой архива |
| `app/workspace/` | workspace, словари, stock/roll storage |
| `app/flows/` | интерактивные сценарии (`stock.py`: load/process/failed) |
| `app/archive/` | search, stats, batch, normalization + рендер |
| `app/diagnostics/` | doctor |
| `messages/` | user-facing строки по зонам |

## Roll

`roll.toml`:

| Поле | Обязательно | Комментарий |
|---|---|---|
| `status` | да | `loaded` \| `processed` \| `failed` |
| `film` | да | |
| `camera` | да | |
| `loaded_at` | да | определяет имя папки ролла |
| `features` | нет | заполняется через `rl features add` |
| `keywords` | нет | заполняется через `rl tags add` (в CLI — "теги") |

### Жизненный цикл ролла

```
[ запас ]  --rl stock add-->  лежит в stock.toml
              │
           rl load
              ▼
[ loaded ]   roll.toml создан
              │
       ┌──────┴──────┐
  rl stock       rl stock
  process          failed
       ▼              ▼
[ processed ]    [ failed ]
```

Переход по циклу — ручной и однонаправленный: обратно в `loaded` roll не возвращается.

## Команды

| Зона | Команда |
|---|---|
| Инициализация | `rl init` |
| Запас | `rl stock add`, `rl stock list` |
| Ролл | `rl load` (`--manual` — без stock), `rl stock process`, `rl stock failed` |
| Дозаполнить | `rl features add`, `rl tags add` |
| Найти / посмотреть | `rl search`, `rl scan`, `rl status`, `rl stats [-v]`, `rl vocab` |
| Гигиена архива | `rl doctor [--fix] [-v]`, `rl normalize [--tags]` |
| Массово | `rl batch process` |

## Принципы

- архив самодостаточен, приложение можно удалить без потери данных;
- словари редактируются текстом и пополняются автоматически при вводе;
- нормализация (`rl normalize`, `rl doctor --fix`) сначала строит план и только потом просит подтверждение;
- roll начинается как `loaded`, дальше — терминально `processed`/`failed`, назад не возвращается.

Настройка окружения и CI — в [docs/development.md](development.md).
