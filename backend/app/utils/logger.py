"""Logging utilities for backend services and API routes."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Create and return a module-level logger.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        Configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger(name)
