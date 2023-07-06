from typing import List
from src.stub_types import Action


actions: List[Action] = [
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
