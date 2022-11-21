from typing import Sequence

from upgrade_knausj.types.condition import Condition, ConditionResult


class CompoundCondition(Condition):
    _conditions: Sequence[Condition]

    def __init__(self, *conditions: Condition):
        self._conditions = conditions

    def __call__(self) -> ConditionResult:
        for condition in self._conditions:
            result = condition()

            if not result.success:
                return result

        return ConditionResult(True, "")
