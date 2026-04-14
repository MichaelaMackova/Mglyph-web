from fastapi import Depends, Query
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

from api.users.schemas import UserPublicSimpleDTO
from api.mglyph.schemas import MGlyphEvaluationPublicDTO

from db.models.challengeModel import ChallengeModel
from db.models.evaluationRoundModel import EvaluationRoundModel
from db.models.challengeEvaluatorModel import InvitationState, InvitationType, ChallengeEvaluatorModel



class EvaluationRoundCreateDTO(BaseModel):
    estimated_end_time: datetime

class EvaluationRoundPublicDTO(BaseModel):
    id: UUID
    sequence_number: int
    estimated_end_time: datetime
    creation_time: datetime
    next_round_id: UUID | None

    @staticmethod
    def from_model(evaluationRoundModel: EvaluationRoundModel) -> "EvaluationRoundPublicDTO":
        return EvaluationRoundPublicDTO(
            id=evaluationRoundModel.id,
            sequence_number=evaluationRoundModel.sequence_number,
            estimated_end_time=evaluationRoundModel.estimated_end_time,
            creation_time=evaluationRoundModel.creation_time,
            next_round_id=evaluationRoundModel.next_round_id
        )


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

class ChallengeFilterParams(BaseModel):
    name_contains: Optional[str] = Field(Query(default=None, description="Filter challenges whose name contains the specified string (case-insensitive)."))
    state: Optional[set[ChallengeState]] = Field(Query(default=None, description="Filter challenges by their state. Can specify multiple states. If not specified, challenges of all states will be returned."))

ChallengeFilterParamsAsQuery = Annotated[ChallengeFilterParams, Depends()]


class ChallengeBase(BaseModel):
    name: str
    glyph_submit_deadline: datetime

class ChallengeCreateDTO(ChallengeBase):
    first_evaluation_round: EvaluationRoundCreateDTO
    

class ChallengePublicSimpleDTO(ChallengeBase):
    id: UUID
    state: ChallengeState
    creation_time: datetime
    last_evaluation_round: EvaluationRoundPublicDTO | None

    @staticmethod
    def from_model(challengeModel: ChallengeModel) -> "ChallengePublicSimpleDTO":
        last_round = max(challengeModel.evaluation_rounds, key=lambda round: round.sequence_number, default=None)
        return ChallengePublicSimpleDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            creation_time=challengeModel.creation_time,
            glyph_submit_deadline=challengeModel.glyph_submit_deadline,
            state=ChallengeState.from_model_params(challengeModel.challenge_finished, challengeModel.submissions_ended),
            last_evaluation_round=EvaluationRoundPublicDTO.from_model(last_round) if last_round else None
        )
    

class ChallengeUserSolverRelationshipType(Enum):
    NONE = "none"
    REGISTERED = "registered"
    MGLYPH_SUBMITTED = "mglyph_submitted"

class ChallengeUserEvaluatorRelationshipType(Enum):
    NONE = "none"
    PENDING_INVITED = "pending_invited"
    PENDING_VOLUNTEER = "pending_volunteer"
    REJECTED_INVITED = "rejected_invited"
    REJECTED_VOLUNTEER = "rejected_volunteer"
    REGISTERED = "registered"
    EVALUATION_AWAITING = "evaluation_awaiting"
    EVALUATION_FINISHED = "evaluation_finished"

class EvaluatorInvitationInfo(BaseModel):
    invitation_type: InvitationType
    invitation_state: InvitationState

class ChallengeUserEvaluatorRelationship(BaseModel):
    relationship_type: ChallengeUserEvaluatorRelationshipType
    invitation_info: EvaluatorInvitationInfo | None


class ChallengeUserRelationshipDTO(BaseModel):
    solver_relationship: ChallengeUserSolverRelationshipType
    evaluator_relationship: ChallengeUserEvaluatorRelationship | None

    @staticmethod
    def from_relationship_flags(is_solver: bool, has_submitted_mglyph: bool, is_active_evaluator: bool, evaluator_state: EvaluatorInvitationInfo | None, waiting_for_evaluation: bool) -> "ChallengeUserRelationshipDTO":
        if is_solver:
            if has_submitted_mglyph:
                solver_relationship = ChallengeUserSolverRelationshipType.MGLYPH_SUBMITTED
            else:
                solver_relationship = ChallengeUserSolverRelationshipType.REGISTERED
        else:
            solver_relationship = ChallengeUserSolverRelationshipType.NONE

        if is_active_evaluator:
            if waiting_for_evaluation:
                evaluator_relationship = ChallengeUserEvaluatorRelationshipType.EVALUATION_AWAITING
            else:
                evaluator_relationship = ChallengeUserEvaluatorRelationshipType.EVALUATION_FINISHED
        else:
            if evaluator_state:
                if evaluator_state.invitation_type == InvitationType.volunteer and evaluator_state.invitation_state == InvitationState.pending:
                    evaluator_relationship = ChallengeUserEvaluatorRelationshipType.PENDING_VOLUNTEER
                elif evaluator_state.invitation_type == InvitationType.invited and evaluator_state.invitation_state == InvitationState.pending:
                    evaluator_relationship = ChallengeUserEvaluatorRelationshipType.PENDING_INVITED
                elif evaluator_state.invitation_type == InvitationType.volunteer and evaluator_state.invitation_state == InvitationState.rejected:
                    evaluator_relationship = ChallengeUserEvaluatorRelationshipType.REJECTED_VOLUNTEER
                elif evaluator_state.invitation_type == InvitationType.invited and evaluator_state.invitation_state == InvitationState.rejected:
                    evaluator_relationship = ChallengeUserEvaluatorRelationshipType.REJECTED_INVITED
                else:
                    evaluator_relationship = ChallengeUserEvaluatorRelationshipType.REGISTERED
            else:
                evaluator_relationship = ChallengeUserEvaluatorRelationshipType.NONE

        return ChallengeUserRelationshipDTO(
            solver_relationship=solver_relationship,
            evaluator_relationship=ChallengeUserEvaluatorRelationship(
                relationship_type=evaluator_relationship,
                invitation_info=evaluator_state if evaluator_state else None)
        )

class ChallengePublicMiniDetailDTO(ChallengePublicSimpleDTO):
    mglyph_evaluations: list[MGlyphEvaluationPublicDTO]
    user_relationship: ChallengeUserRelationshipDTO | None


class ChallengePublicDTO(ChallengeBase):
    id: UUID
    creation_time: datetime
    state: ChallengeState
    creator: UserPublicSimpleDTO
    solvers: list[UserPublicSimpleDTO]
    rounds: list[EvaluationRoundPublicDTO]
    user_relationship: ChallengeUserRelationshipDTO | None

    @staticmethod
    def from_model(challengeModel: ChallengeModel, user_relationship: ChallengeUserRelationshipDTO | None = None) -> "ChallengePublicDTO":
        return ChallengePublicDTO(
            id=challengeModel.id,
            name=challengeModel.name,
            creation_time=challengeModel.creation_time,
            glyph_submit_deadline=challengeModel.glyph_submit_deadline,
            state=ChallengeState.from_model_params(challengeModel.challenge_finished, challengeModel.submissions_ended),
            creator=UserPublicSimpleDTO.from_model(challengeModel.creator),
            solvers=[UserPublicSimpleDTO.from_model(solver) for solver in challengeModel.solvers],
            rounds=[EvaluationRoundPublicDTO.from_model(round) for round in challengeModel.evaluation_rounds],
            user_relationship=user_relationship
        )

class ChallengeUpdateDTO(BaseModel):
    name: str | None = None
    glyph_submit_deadline: datetime | None = None


class ChallengeEvaluatorInviteStatesInfoDTO(BaseModel):
    challenge: ChallengePublicSimpleDTO
    active_evaluator_count: int
    has_pending_invites: bool

    @staticmethod
    def from_model(challengeModel: ChallengeModel, active_evaluator_count: int, has_pending_invites: bool) -> "ChallengeEvaluatorInviteStatesInfoDTO":
        return ChallengeEvaluatorInviteStatesInfoDTO(
            challenge=ChallengePublicSimpleDTO.from_model(challengeModel),
            active_evaluator_count=active_evaluator_count,
            has_pending_invites=has_pending_invites
        )


class ChallengeEvaluatorInfoBase(BaseModel):
    id: UUID
    invitation_state: InvitationState
    invitation_type: InvitationType


class ChallengeEvaluatorInfoWithChallengeDTO(ChallengeEvaluatorInfoBase):
    challenge: ChallengePublicSimpleDTO

    @staticmethod
    def from_model(challengeEvaluatorModel: ChallengeEvaluatorModel) -> "ChallengeEvaluatorInfoWithChallengeDTO":
        return ChallengeEvaluatorInfoWithChallengeDTO(
            id=challengeEvaluatorModel.id,
            invitation_state=challengeEvaluatorModel.invitation_state,
            invitation_type=challengeEvaluatorModel.invitation_type,
            challenge=ChallengePublicSimpleDTO.from_model(challengeEvaluatorModel.challenge)
        )

class ChallengeEvaluatorInfoWithEvaluatorDTO(ChallengeEvaluatorInfoBase):
    evaluator: UserPublicSimpleDTO

    @staticmethod
    def from_model(challengeEvaluatorModel: ChallengeEvaluatorModel) -> "ChallengeEvaluatorInfoWithEvaluatorDTO":
        return ChallengeEvaluatorInfoWithEvaluatorDTO(
            id=challengeEvaluatorModel.id,
            invitation_state=challengeEvaluatorModel.invitation_state,
            invitation_type=challengeEvaluatorModel.invitation_type,
            evaluator=UserPublicSimpleDTO.from_model(challengeEvaluatorModel.evaluator)
        )