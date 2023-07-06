import logging
import pywinctl as pwc

from pywinctl import Re, Window
from typing import List, Union

from config import find_window_config
from actions import actions
from src.directive import perform_actions

logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

found_window: Union[Window, None] = None

if "window_name" in find_window_config:
    logger.info(
        f"Searching for window using window_name condition: {find_window_config['window_name']}"
    )

    match_policy: Union[int, None] = None

    if "window_name_match_policy" in find_window_config:
        match_policy = find_window_config["window_name_match_policy"]
    else:
        logger.warning(
            "No window_name_match_policy specified, defaulting to Re.CONTAINS"
        )
        match_policy = Re.CONTAINS

    windows: List[Window] = pwc.getWindowsWithTitle(
        find_window_config["window_name"], condition=match_policy
    )

    if len(windows) == 0:
        logger.error(
            f"Could not find window with title {find_window_config['window_name']}"
        )
        exit(1)
    elif len(windows) > 1:
        logger.warning(
            f"Found multiple windows with title {find_window_config['window_name']}, we'll choose the first one."
        )

    found_window = windows[0]


if "position" in find_window_config:
    if found_window is not None:
        logger.error("Can't specify both window_name and position.")
        exit(1)

    [x, y] = find_window_config["position"]

    logger.info(f"Searching for window using position condition: ({x}, {y})")

    windows: List[Window] = pwc.getWindowsAt(x, y)
    if len(windows) == 0:
        logger.error(f"Could not find any window at position ({x}, {y})")
        exit(1)
    elif len(windows) > 1:
        logger.warning(
            f"Found multiple windows at position ({x}, {y}), we'll choose the first one."
        )
        found_window = pwc.getTopWindowAt(x, y)
    else:
        found_window = windows[0]


if found_window is None:
    if "window_name" not in find_window_config and "position" not in find_window_config:
        # No useful configs were specified, so we'll just use the active window.
        logger.warning(
            "No window_name or position specified, defaulting to the active window!"
        )

        found_window = pwc.getActiveWindow()
        if found_window is None:
            # We've tried our best, but we can't find any window, so just report and quit.
            logger.error("Could not find any active window!")
            exit(1)
    else:
        # So, configs were specified, but we couldn't find any window.
        # This branch should be unreachable, but just in case...
        logger.error("Could not find any window with the provided config!")
        exit(1)

logger.info(f"Found window with title: {found_window.title}")

perform_actions(actions, found_window)
