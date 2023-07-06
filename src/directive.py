import logging, time
import pyautogui, pywinctl

from pywinctl import Window
from typing import List
from src.stub_types import (
    AllDirective,
    Action,
    SetActiveStateDirective,
    KeyboardDirective,
    MouseDirective,
    SleepDirective,
)

from config import execute_directive_config


logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(levelname)s: %(message)s")
logger = logging.getLogger("directive")

sleep_ms = 0
if "sleep_ms_between_directives" in execute_directive_config:
    sleep_ms = execute_directive_config["sleep_ms_between_directives"]


def point_in_rect_inclusive(
    x: float, y: float, left: float, top: float, right: float, bottom: float
):
    """Returns ``True`` if the ``(x, y)`` point is within or on the edge of the box
    described by ``(left, top, right, bottom)``, with origin point set as top-left."""
    return left <= x <= right and top <= y <= bottom


def _set_active_state_of_win(
    directive: SetActiveStateDirective, window: Window
) -> bool:
    logger.debug(
        f"Setting active state of window \"{window.title}\" to {directive['state']}"
    )

    if directive["state"] == "active":
        # wait=True is ignored on Windows. see pywinctl/_pywinctl_win.py
        ret = False
        for i in range(3):
            ret = ret or window.activate(wait=True)
            if ret:
                logger.info("Successfully activated window.")
                return True
            elif i < 2:
                logger.warning(
                    f"Failed to activate window. Retrying after {sleep_ms} ms..."
                )
                time.sleep(sleep_ms / 1000)
            else:
                logger.error("Failed to activate window after 3 attempts.")
        return False
    elif directive["state"] == "inactive":
        return window.lowerWindow()
    elif directive["state"] == "front_but_inactive":
        ret = window.lowerWindow()
        time.sleep(sleep_ms / 1000)
        ret = ret and window.raiseWindow()
        return ret
    else:
        logger.error(f"Unknown target active state {directive['state']}")
        return False


def _send_mouse_directive_to_win(directive: MouseDirective, window: Window) -> bool:
    logger.debug(
        f"Sending mouse directive to window \"{window.title}\": {directive['type']}"
    )

    method = directive["method"]
    if method == "move" and "pos" in directive:
        logger.error(
            f"Mouse move directive cannot have pos specified. Specify offset or use move_to instead."
        )
        return False
    if method == "click" and "pos" in directive:
        logger.error(
            f"Mouse click directive cannot have pos specified. Use click_at instead."
        )
        return False
    if "offset" in directive and method != "move":
        logger.error(
            f"Mouse directive {method} cannot have offset specified. Specify pos instead, if necessary."
        )
        return False

    [x, y] = pyautogui.position()
    x = int(x)
    y = int(y)

    [left, top, right, bottom] = window.bbox
    logger.debug(
        f'Got window "{window.title}"\'s bbox: left={left}, top={top}, right={right}, bottom={bottom}'
    )

    if directive["method"] != "click":
        if "pos" in directive:
            pos = directive["pos"]
            if isinstance(pos, list):
                [x, y] = pos
            else:
                if pos == "center":
                    [x, y] = window.center
                elif pos == "top_left":
                    [x, y] = [left + 1, top + 1]
                elif pos == "top_right":
                    [x, y] = [right - 1, top + 1]
                elif pos == "bottom_left":
                    [x, y] = [left + 1, bottom - 1]
                elif pos == "bottom_right":
                    [x, y] = [right - 1, bottom - 1]
                else:
                    logger.error(f"Unknown pos {pos}")
                    return False
                logger.info(f"Non-trivial pos {pos} translated to ({x}, {y}).")
        elif "offset" in directive:
            [dx, dy] = directive["offset"]
            x += dx
            y += dy
            logger.info(f"Applied move offset ({dx}, {dy}) and got ({x}, {y}).")
        else:
            logger.warning("No pos specified, defaulting to current mouse position.")

    # check if mouse position is in window
    if not point_in_rect_inclusive(x, y, left, top, right, bottom):
        logger.error(f'Mouse position ({x}, {y}) is not in window "{window.title}"')
        return False

    # check if mouse position is out of screen. This may happen if the window is
    # bigger than the screen.
    [screen_width, screen_height] = pyautogui.size()
    if not point_in_rect_inclusive(x, y, 0, 0, 0 + screen_width, 0 + screen_height):
        logger.warning(f"Mouse position ({x}, {y}) is out of screen.")
        x = 0 if x < 0 else x
        x = screen_width if x > screen_width else x
        y = 0 if y < 0 else y
        y = screen_height if y > screen_height else y
        logger.warning(
            f"Due to the previous warning, mouse position is adjusted to ({x}, {y})."
        )

    # check if window is the topmost window at mouse position
    topmost_window = pywinctl.getTopWindowAt(x, y)
    if topmost_window != window:
        logger.warning(
            f'Window "{window.title}" is not the topmost window at position ({x}, {y}), we need to activate it first.'
        )
        window.activate(wait=True)

    if directive["method"] == "move_to":
        pyautogui.moveTo(x, y, duration=0.25, tween=pyautogui.easeOutQuad)  # type: ignore

    if directive["method"] == "click_at":
        button = directive["button"] if "button" in directive else "primary"
        pyautogui.click(x, y, duration=0.25, tween=pyautogui.easeOutQuad, button=button)  # type: ignore

    if directive["method"] == "click":
        button = directive["button"] if "button" in directive else "primary"
        pyautogui.click(duration=0.25, button=button)

    return True


def _send_keyboard_directive_to_win(
    directive: KeyboardDirective, window: Window
) -> bool:
    key_str = directive["key"]
    key_str = key_str if isinstance(key_str, str) else ",".join(key_str)
    logger.debug(
        f"Sending keyboard directive to window \"{window.title}\": {directive['type']} {key_str}"
    )

    if directive["method"] == "key_down":
        key = directive["key"]
        if isinstance(key, list):
            for k in key:
                pyautogui.keyDown(k)
        elif isinstance(key, str):
            pyautogui.keyDown(key)
        else:
            logger.error(f"Unknown key type: {type(key)}")
            # TODO: should we release all key-down keys as cleanup?
            return False

    if directive["method"] == "key_up":
        key = directive["key"]
        if isinstance(key, list):
            for k in key:
                pyautogui.keyUp(k)
        elif isinstance(key, str):
            pyautogui.keyUp(key)
        else:
            logger.error(f"Unknown key type: {type(key)}")
            return False

    if directive["method"] == "type":
        key = directive["key"]
        if isinstance(key, list):
            for k in key:
                pyautogui.press(k)
        elif isinstance(key, str):
            pyautogui.press(key)
        else:
            logger.error(f"Unknown key type: {type(key)}")
            return False

    if directive["method"] == "delete":
        pyautogui.press("backspace")

    if directive["method"] == "hotkey":
        key = directive["key"]
        if isinstance(key, list):
            pyautogui.hotkey(*key)
        elif isinstance(key, str):
            pyautogui.hotkey(key)
        else:
            logger.error(f"Unknown key type: {type(key)}")
            return False

    return True


def _wait_sleep_directive(directive: SleepDirective) -> bool:
    logger.debug(f"Waiting for {directive['time_ms']} ms...")
    time.sleep(directive["time_ms"] / 1000)
    return True


def _exec_directive(directive: AllDirective, window: Window) -> bool:
    if directive["type"] == "set_active_state":
        logger.info(f"Setting window active state to {directive['state']}...")
        return _set_active_state_of_win(directive, window)
    elif directive["type"] == "mouse":
        logger.info(f"Sending mouse directive of type {directive['type']}...")
        return _send_mouse_directive_to_win(directive, window)
    elif directive["type"] == "keyboard":
        logger.info(f"Sending keyboard directive of type {directive['type']}...")
        return _send_keyboard_directive_to_win(directive, window)
    elif directive["type"] == "sleep":
        logger.info(f"Sleeping for {directive['time_ms']} ms...")
        return _wait_sleep_directive(directive)
    else:
        logger.error(f"Unknown directive type: {directive['type']}")
        return False


def _perform_action(action: Action, window: Window) -> bool:
    directive = action["directive"]
    exec_count = 1 if "exec_count" not in action else action["exec_count"]

    type_str = "sequence" if isinstance(directive, list) else directive["type"]
    logger.info(f"Performing action of type {type_str} {exec_count} times...")

    if isinstance(directive, list):
        if exec_count == "inf":
            while True:
                for d in directive:
                    if not _exec_directive(d, window):
                        return False
                    if sleep_ms > 0:
                        logger.debug(f"Sleeping between directives for {sleep_ms}ms...")
                        time.sleep(sleep_ms / 1000)
        else:
            for i in range(exec_count):
                for d in directive:
                    if not _exec_directive(d, window):
                        return False
                    if sleep_ms > 0 and i < exec_count - 1:
                        logger.debug(f"Sleeping between directives for {sleep_ms}ms...")
                        time.sleep(sleep_ms / 1000)
    else:
        if exec_count == "inf":
            logger.error("Executing inf times on a single directive: sleep missing?")
        else:
            for i in range(exec_count):
                if not _exec_directive(directive, window):
                    return False
                if sleep_ms > 0 and i < exec_count - 1:
                    logger.debug(f"Sleeping between directives for {sleep_ms}ms...")
                    time.sleep(sleep_ms / 1000)

    return True


def perform_actions(actions: List[Action], window: Window) -> bool:
    for action in actions:
        if not _perform_action(action, window):
            logger.error(f"Failed to perform action: {action['directive']}")
            return False
        if sleep_ms > 0 and action != actions[-1]:
            logger.debug(f"Sleeping between actions for {sleep_ms}ms...")
            time.sleep(sleep_ms / 1000)

    return True
