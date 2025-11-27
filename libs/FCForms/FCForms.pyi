from typing import Callable, Any


class FCForms:

    @staticmethod
    def Run() -> None: ...

    @staticmethod
    def Test() -> None: ...

    class Forms:
        Home: 'FCForms.Forms'

    @staticmethod
    def Hide(form: 'FCForms.Forms') -> None: ...

    @staticmethod
    def Show(form: 'FCForms.Forms') -> None: ...

    class Label:
        lAccount: 'FCForms.Label'
        lSync: 'FCForms.Label'
        lSyncInfo: 'FCForms.Label'
        lLocal: 'FCForms.Label'
        lLocalInfo: 'FCForms.Label'

    @staticmethod
    def LabelText(
        form: 'FCForms.Forms',
        label: 'FCForms.Label',
        text: str
    ) -> None: ...

    class Button:
        bExit: 'FCForms.Button'
        bSync: 'FCForms.Button'
        bLocal: 'FCForms.Button'

    @staticmethod
    def ButtonText(
        form: 'FCForms.Forms',
        button: 'FCForms.Button',
        text: str
    ) -> None: ...

    @staticmethod
    def ButtonAssign(
        form: 'FCForms.Forms',
        button: 'FCForms.Button',
        action: Callable[[], Any]
    ) -> None: ...

    @staticmethod
    def ReadyThen(action: Callable[[], Any]) -> None: ...
