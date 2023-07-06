# Automated Window Control

## Requirements

Python >= 3.9

## Dependencies

```bash
python -m pip install -r requirements.txt
```

## Usage

```bash
git clone https://github.com/XieJiSS/automated-window-control.git
cd automated-window-control
python -m pip install -r requirements.txt
# modify config.py and actions.py, and then:
python main.py
```

### 1. Specify the Target Window

You can specify the target window by providing its title. Or, you can specify a position, and the topmost window at that position will become the target window.

Information should be provided in the `config.py` file.

```python
find_window_config: FindWindowConfig = {
    "window_name": "Microsoft Teams",
    # You can change Re.CONTAINS to other matching policies, like Re.IS or Re.STARTS_WITH
    "window_name_match_policy": Re.CONTAINS,
    # "position": [0, 0],
}

execute_directive_config: ExecuteDirectiveConfig = {
    "sleep_ms_between_directives": 200,
}
```

### 2. Provide a Sequence of Actions

Actions should be provided in the `actions.py` file.

```python
actions = a_list_of_actions
```

The variable `actions` should contain all actions you'd like the program to execute. Each action can contain one or more directive. A directive represents a smallest unit this program can execute, like a mouse movement, a key stroke, or simply sleeping for a while. Actions, merely as a wrapper of directives, can specify `exec_count`, which enables you to combine several directives together, and loop them sequentially:

```
action_a = {
  "directive": [foo, bar],
  "exec_count": 3,
}
action_b = {
  "directive": baz,
}

actions = [
  action_a,
  action_b,
]
```

In the example shown above, all directives in `action_a` will be executed 3 times sequentially, and then the only directive in `action_b` will be executed once.

All available directives' type definitions are as follows (but you don't need to understand them, so I hide them in `<details>`).

<details>

```python
class SetActiveStateDirective(TypedDict):
    type: Literal["set_active_state"]
    state: Literal["active", "inactive", "front_but_inactive"]

class MouseDirective(TypedDict):
    type: Literal["mouse"]
    method: Literal["move", "move_to", "click_at", "click"]
    # pos: for move_to and click_at
    pos: NotRequired[
        List[int]
        | Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ]
    # offset: for move
    offset: NotRequired[List[int]]
    # button: default is primary
    button: NotRequired[Literal["left", "middle", "right", "primary", "secondary"]]

class KeyboardDirective(TypedDict):
    type: Literal["keyboard"]
    method: Literal["key_down", "key_up", "type", "delete", "hotkey"]
    key: KEYBOARD_KEYS | List[KEYBOARD_KEYS]

class SleepDirective(TypedDict):
    type: Literal["sleep"]
    time_ms: float
```

</details>

#### `SetActiveStateDirective`

```python
{
  "type": "set_active_state",
  "state": "active", # or "inactive", "front_but_inactive"
}
```

- `state`: the state you want to set the target window to.
  - `active`: set the target window to active state, so it will be focused and can accept keyboard input.
  - `inactive`: set the target window to inactive state, so it will be unfocused.
  - `front_but_inactive`: set the target window to be the frontmost window, while still be in inactive state.

#### `MouseDirective`

```python
{
  "type": "mouse",
  "method": "move", # or "move_to", "click_at", "click"
  "pos": [0, 0], # or "center", "top_left", "top_right", "bottom_left", "bottom_right"
  "offset": [0, 0], # can be omitted
  "button": "left", # or "middle", "right", "primary", "secondary". can be omitted and default is "primary"
}
```

- `method`: the method you want to use to interact with the mouse.
  - `move`: move the mouse cursor by the offset specified in `offset`.
  - `move_to`: move the mouse cursor to the position specified in `pos`.
  - `click_at`: move the mouse cursor to the position specified in `pos`, and then click the mouse button specified in `button`.
  - `click`: click the mouse button specified in `button` at the current mouse cursor position.
- `pos`: the position you want to move the mouse cursor to. The origin point of the axis is the top-left corner of the screen.
  - `[0, 0]`: the top-left corner of the screen.
  - `[x, y]`: the point at the x-th column (pixel) and y-th row (pixel) of the screen.
  - `"center"`: the center of the target window.
  - `"top_left"`: the top-left corner of the target window.
  - `"top_right"`: the top-right corner of the target window.
  - `"bottom_left"`: the bottom-left corner of the target window.
  - `"bottom_right"`: the bottom-right corner of the target window.
- `offset`: the offset you want to move the mouse cursor by. The origin point of the axis is the current mouse cursor position.
  - `[x, y]`: move the mouse cursor by x pixels horizontally and y pixels vertically.
  - affective only when `method` is not `move`, and should be omitted otherwise.
- `button`: the mouse button you want to click.
  - `"primary"`: the primary mouse button, which is usually the left mouse button. This is the default value.
  - `"secondary"`: the secondary mouse button, which is usually the right mouse button.
  - `"left"`: the left mouse button.
  - `"middle"`: the middle mouse button.
  - `"right"`: the right mouse button.
  - affective only when `method` is `click_at` or `click`.

#### `KeyboardDirective`

```python
{
  "type": "keyboard",
  "method": "key_down", # or "key_up", "type", "delete", "hotkey"
  "key": "a", # or ["a", "b", "c"], ["Ctrl", "Alt", "Delete"]
}
```

- `method`: the method you want to use to interact with the keyboard.
  - `key_down`: press the key specified in `key`, and keep them pressed down until a corresponding `key_up`.
  - `key_up`: release the key specified in `key`.
  - `type`: type the key specified in `key`, i.e. the same as pressing the key down and then release it.
  - `delete`: press the delete key.
  - `hotkey`: press the keys specified in `key` as a hotkey, i.e. press them down and then release them altogether.
- `key`: the key you want to press.
  - `"a"`: the key "a".
  - `["a", "b", "c"]`: the keys "a", "b", and "c".
  - `["Ctrl", "Alt", "Delete"]`: the keys "Ctrl", "Alt", and "Delete".
  - Full list of available keys can be found in `src/stub_types.py`, in the `KEYBOARD_KEYS` type variable.

#### `SleepDirective`

```python
{
  "type": "sleep",
  "time_ms": 1000,
}
```

- `time_ms`: the time you want to sleep in milliseconds.

### Example

```python
# config.py
from pywinctl import Re

find_window_config: FindWindowConfig = {
    "window_name": "Microsoft Teams",
    "window_name_match_policy": Re.CONTAINS,
}

execute_directive_config: ExecuteDirectiveConfig = {
    "sleep_ms_between_directives": 200,
}


# actions.py
actions = [
    {
        "directive": {
            "type": "set_active_state",
            "state": "active",
        }
    },
    {
        "directive": {
            "type": "mouse",
            "method": "move_to",
            "pos": "center",
        }
    },
    {
        "directive": [
            {
                "type": "set_active_state",
                "state": "active",
            },
            {
                "type": "mouse",
                "method": "move_to",
                "pos": "top_left",
            },
            {
                "type": "sleep",
                "time_ms": 1000 * 60 * 2,
            },
            {
                "type": "mouse",
                "method": "move_to",
                "pos": "center",
            },
            {
                "type": "sleep",
                "time_ms": 1000 * 60 * 2,
            },
        ],
        "exec_count": "inf",
    },
]
```

## Debug

Change `logging.basicConfig`'s `level` from `logging.INFO` to `logging.DEBUG` in `src/directive.py` and `main.py`:

```python
# Before:
logging.basicConfig(level=logging.INFO, ...)
# After:
logging.basicConfig(level=logging.DEBUG, ...)
```

And then run `main.py` again.
