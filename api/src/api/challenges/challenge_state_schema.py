from enum import Enum

class ChallengeState(str, Enum):
    open = "open"
    evaluating = "evaluating"
    finished = "finished"

    @staticmethod
    def from_model_params(challenge_finished: bool, submissions_ended: bool) -> "ChallengeState":
        if challenge_finished:
            return ChallengeState.finished
        elif submissions_ended:
            return ChallengeState.evaluating
        else:
            return ChallengeState.open
        
    def to_model_params(self) -> tuple[bool, bool]:
        """
        Converts the ChallengeState back to the corresponding model parameters.

        Returns:
            tuple: A tuple of (challenge_finished, submissions_ended) corresponding to the ChallengeState.
        """
        if self == ChallengeState.finished:
            return (True, True)
        elif self == ChallengeState.evaluating:
            return (False, True)
        else:
            return (False, False)