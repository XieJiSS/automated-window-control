import sys
from typing import List, Literal, Union

if sys.version_info < (3, 11):
    from typing_extensions import TypedDict, NotRequired
else:
    from typing import TypedDict, NotRequired


class FindWindowConfig(TypedDict):
    window_name: NotRequired[str]
    # window_name_match_policy: please refer to pywinctl.Re
    # e.g. Re.IS, Re.CONTAINS, Re.STARTS_WITH, Re.ENDS_WITH
    window_name_match_policy: NotRequired[int]
    position: NotRequired[List[int]]


class ExecuteDirectiveConfig(TypedDict):
    sleep_ms_between_directives: NotRequired[int]


class SetActiveStateDirective(TypedDict):
    type: Literal["set_active_state"]
    state: Literal["active", "inactive", "front_but_inactive"]


class MouseDirective(TypedDict):
    type: Literal["mouse"]
    method: Literal["move", "move_to", "click_at", "click"]
    # pos: for move_to and click_at
    pos: NotRequired[
        Union[
            List[int],
            Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"],
        ]
    ]
    # offset: for move
    offset: NotRequired[List[int]]
    # button: default is primary
    button: NotRequired[Literal["left", "middle", "right", "primary", "secondary"]]


KEYBOARD_KEYS = Literal[
    "\t",
    "\n",
    "\r",
    " ",
    "!",
    '"',
    "#",
    "$",
    "%",
    "&",
    "'",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
    "@",
    "[",
    "\\",
    "]",
    "^",
    "_",
    "`",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "{",
    "|",
    "}",
    "~",
    "accept",
    "add",
    "alt",
    "altleft",
    "altright",
    "apps",
    "backspace",
    "browserback",
    "browserfavorites",
    "browserforward",
    "browserhome",
    "browserrefresh",
    "browsersearch",
    "browserstop",
    "capslock",
    "clear",
    "convert",
    "ctrl",
    "ctrlleft",
    "ctrlright",
    "decimal",
    "del",
    "delete",
    "divide",
    "down",
    "end",
    "enter",
    "esc",
    "escape",
    "execute",
    "f1",
    "f10",
    "f11",
    "f12",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f2",
    "f20",
    "f21",
    "f22",
    "f23",
    "f24",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "final",
    "fn",
    "hanguel",
    "hangul",
    "hanja",
    "help",
    "home",
    "insert",
    "junja",
    "kana",
    "kanji",
    "launchapp1",
    "launchapp2",
    "launchmail",
    "launchmediaselect",
    "left",
    "modechange",
    "multiply",
    "nexttrack",
    "nonconvert",
    "num0",
    "num1",
    "num2",
    "num3",
    "num4",
    "num5",
    "num6",
    "num7",
    "num8",
    "num9",
    "numlock",
    "pagedown",
    "pageup",
    "pause",
    "pgdn",
    "pgup",
    "playpause",
    "prevtrack",
    "print",
    "printscreen",
    "prntscrn",
    "prtsc",
    "prtscr",
    "return",
    "right",
    "scrolllock",
    "select",
    "separator",
    "shift",
    "shiftleft",
    "shiftright",
    "sleep",
    "space",
    "stop",
    "subtract",
    "tab",
    "up",
    "volumedown",
    "volumemute",
    "volumeup",
    "win",
    "winleft",
    "winright",
    "yen",
    "command",
    "option",
    "optionleft",
    "optionright",
]


class KeyboardDirective(TypedDict):
    type: Literal["keyboard"]
    method: Literal["key_down", "key_up", "type", "delete", "hotkey"]
    key: Union[KEYBOARD_KEYS, List[KEYBOARD_KEYS]]


class SleepDirective(TypedDict):
    type: Literal["sleep"]
    time_ms: float


AllDirective = Union[
    MouseDirective, KeyboardDirective, SetActiveStateDirective, SleepDirective
]


class Action(TypedDict):
    directive: Union[AllDirective, List[AllDirective]]
    exec_count: NotRequired[Union[int, Literal["inf"]]]
