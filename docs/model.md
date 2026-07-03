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

## Code Layout

Код тоже разделен по зонам:

- `src/roll/filesystem.py` — низкоуровневые операции с файловой структурой архива;
- `src/roll/app/archive/` — чтение, анализ и массовые операции над архивом;
- `src/roll/app/diagnostics/` — проверки и рендер отчета `doctor`;
- `src/roll/app/flows/` — интерактивные сценарии команд;
- `src/roll/app/workspace/` — workspace, словари и файлы состояния;
- `src/roll/messages/` — короткие user-facing строки по зонам.

## 1. Global config

Глобальная конфигурация приложения живет в `~/.config/roll/config.toml`.
Она знает только список архивов.

## 2. Archive workspace

У каждого архива есть свой workspace — `<архив>/.roll/`. Внутри:
- `config.toml`
- `stock.toml` — запас пленки
- `vocabulary/{films,cameras,features,keywords}.txt`

`stock.toml` и словари работают совместно, но решают разные задачи:
- `stock.toml` хранит физические катушки, которые сейчас есть на руках;
- `vocabulary/*.txt` хранит канонические значения для автокомплита и ручного ввода.

## 3. Roll

Один roll хранится в отдельной папке внутри архива, например `2026/07-03/`.
Внутри лежит `roll.toml`. Минимальное состояние roll:

- `status` — один из `loaded`, `processed`, `failed` (см. `roll.app.statuses.VALID_STATUSES`)
- `film`
- `camera`
- `loaded_at`
- `features` — необязательные особенности; их можно добавить через `rl features add`
- `keywords` — теги; их можно добавить через `rl tags add`

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

- `rl init` — зарегистрировать архив и создать workspace;
- `rl stock add` — добавить пленку в запас;
- `rl stock list` — показать текущий запас пленки;
- `rl load` — взять одну пленку из запаса и создать новый roll;
- `rl load --manual` — вручную задать пленку через словарь, не трогая stock;
- `rl stock process` — пометить `loaded` roll как обработанную;
- `rl stock failed` — пометить `loaded` roll как испорченную;
- `rl features add` — добавить особенности к roll;
- `rl tags add` — добавить теги к roll;
- `rl batch process` — массово пометить старые loaded-роллы как processed;
- `rl stats` — показать статистику по архиву;
- `rl stats -v` — показать полный список значений;
- `rl search` — искать по уже известным данным;
- `rl scan` — показать структуру архива;
- `rl status` — показать состояние индекса;
- `rl vocab` — показать словари;
- `rl doctor` — проверить целостность и показать не проиндексированные папки;
- `rl doctor --fix` — применить безопасные исправления;
- `rl doctor -v` — показать полный список безопасных исправлений;
- `rl normalize` — привести имена папок к единому виду.
- `rl normalize --tags` — привести теги к uppercase.

## Принципы

- архив самодостаточен;
- приложение можно удалить без потери данных;
- словари редактируются обычным текстом;
- новые значения пополняют словари автоматически;
- запас пленки хранится в workspace, отдельно от `roll.toml`;
- ручной режим `rl load --manual` использует словарь пленок и может пополнять его новыми значениями;
- особенности можно дополнять отдельно через `rl features add`;
- пленка попадает в roll только после загрузки в камеру;
- roll начинается как `loaded` и переходит в `processed` или `failed`, дальше не меняется;
- теги в CLI называются тегами, но хранятся в поле `keywords`;
- `doctor` показывает, что можно безопасно исправить, и поддерживает `--fix` и `-v`;
- `normalize --tags` приводит keywords к uppercase в `roll.toml` и в словаре;
- `stats` умеет смотреть общий срез и фильтр по году; `-v` раскрывает полный список;
- нормализация не меняет `roll.toml`;
- до изменения диска сначала строится план.
- разработка и настройка описаны в [docs/development.md](development.md);
