"""CLI-интерфейс приложения (этап 1)."""

import sys
from typing import List, Optional

from .config import parse_config
from .errors import ConfigError, ExitCode


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа CLI: разбор параметров и их вывод."""
    try:
        config = parse_config(argv)
    except ConfigError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return ExitCode.CONFIG_ERROR

    print("Параметры запуска:")
    for key, value in config.as_dict().items():
        print(f"  {key}: {value}")
    return ExitCode.OK


if __name__ == "__main__":
    sys.exit(main())