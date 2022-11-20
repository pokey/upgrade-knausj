from upgrade_knausj.types.condition import Condition, ConditionResult


class AlwaysTrue(Condition):
    def __call__(self) -> ConditionResult:
        return ConditionResult(True, "")
