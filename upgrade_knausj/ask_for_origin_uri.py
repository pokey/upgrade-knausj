from upgrade_knausj.stdio.prompter import Prompter


class AskForOriginUri:
    _prompter: Prompter

    def __init__(self, prompter: Prompter):
        self._prompter = prompter

    def __call__(self) -> str:
        return self._prompter.ask("Enter your repository remote")
