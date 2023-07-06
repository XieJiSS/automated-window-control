from pywinctl import Re

from src.stub_types import ExecuteDirectiveConfig, FindWindowConfig


find_window_config: FindWindowConfig = {
    "window_name": "Microsoft Teams",
    "window_name_match_policy": Re.CONTAINS,
    # "position": [0, 0],
}

execute_directive_config: ExecuteDirectiveConfig = {
    "sleep_ms_between_directives": 200,
}
