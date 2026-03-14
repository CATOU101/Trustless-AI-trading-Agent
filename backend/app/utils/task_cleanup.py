"""Utilities for graceful shutdown of background asyncio tasks."""

import asyncio


async def stop_background_tasks() -> None:
    """Cancel and await all background tasks except the current shutdown task."""
    print("Stopping background tasks...")
    current = asyncio.current_task()
    tasks = [
        task
        for task in asyncio.all_tasks()
        if task is not current and not task.done()
    ]

    for task in tasks:
        task.cancel()

    for task in tasks:
        try:
            await task
        except asyncio.CancelledError:
            pass

    print("Cleanup complete")
