from roll.helpers.output import echo_lines

from roll.app.archive.stats import build_stats_report


def render_stats_report(archive, year: str | None = None, verbose: bool = False) -> None:
    report = build_stats_report(archive, year)

    if not report.roll_count:
        from typer import echo

        echo("Нет данных для статистики.")
        return

    from typer import echo

    echo_lines(["Состояние индекса", ""])
    if report.year:
        echo(f"Год: {report.year}")
    echo(f"Роллов: {report.roll_count}")
    echo(f"Пленок в статистике: {report.film_count}")
    echo(f"Тегов в статистике: {report.tag_count}")
    echo("")

    limit = None if verbose else 5
    _echo_counter_block("По статусам", report.status_counts, limit=limit)
    _echo_counter_block("По годам", report.year_counts, limit=limit)
    _echo_counter_block("По пленкам", report.film_counts, limit=limit)
    _echo_counter_block("По тегам", report.tag_counts, limit=limit)
    _echo_counter_block("По камерам", report.camera_counts, limit=limit)


def _echo_counter_block(title: str, counter, limit: int | None = None) -> None:
    from typer import echo

    if not counter:
        return

    echo(title)
    items = counter.most_common(limit)
    width = _bar_width(dict(items))
    label_width = _label_width(dict(items))
    for name, count in items:
        echo(f"  {name:<{label_width}}  {count:>4}  {_render_bar(count, width)}")
    if limit is not None and len(counter) > limit:
        echo(f"  ... и еще {len(counter) - limit}")
    echo("")


def _bar_width(counter) -> int:
    return max(1, min(20, max(counter.values(), default=0)))


def _label_width(counter) -> int:
    return max(24, max((len(name) for name in counter), default=0))


def _render_bar(count: int, max_count: int) -> str:
    if count <= 0 or max_count <= 0:
        return ""
    return "█" * max(1, round((count / max_count) * 20))
