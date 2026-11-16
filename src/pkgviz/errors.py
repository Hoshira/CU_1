"""Исключения и коды возврата приложения."""


class ConfigError(Exception):
    """Ошибка конфигурации (некорректный параметр CLI)."""


class ExitCode:
    """Коды возврата процесса."""

    OK = 0
    CONFIG_ERROR = 2