from rich.prompt import Prompt


class Prompter:
    def ask(self, msg) -> str:
        return Prompt.ask(msg)
