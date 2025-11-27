from typing import Callable, Optional, Any

class FCForms:
    class Label:
        lAccount: "FCForms.Label"
        lSync: "FCForms.Label"
        lSyncInfo: "FCForms.Label"
        lLocal: "FCForms.Label"
        lLocalInfo: "FCForms.Label"

    class Button:
        bExit: "FCForms.Button"
        bSync: "FCForms.Button"
        bLocal: "FCForms.Button"

    @staticmethod
    def Run() -> None: ...
    
    @staticmethod
    def Test() -> None: ...

    @staticmethod
    def HomeT(label: "FCForms.Label", text: str) -> None: ...

    @staticmethod
    def HomeT(button: "FCForms.Button", text: str) -> None: ...

    @staticmethod
    def HomeBA(button: "FCForms.Button", action: Callable[[], Any]) -> None: ...
