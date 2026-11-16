"""Исключения и коды возврата приложения."""


class ConfigError(Exception):
    """Ошибка конфигурации (некорректный параметр CLI)."""


class DataError(Exception):
    """Ошибка получения или разбора данных о зависимостях."""


class ExitCode:
    """Коды возврата процесса."""

    OK = 0
    CONFIG_ERROR = 2
    DATA_ERROR = 3