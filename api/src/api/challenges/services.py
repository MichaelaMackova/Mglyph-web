from typing import Annotated
from fastapi import Depends, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from db.database import SessionDep
from uuid import UUID
from datetime import datetime, timedelta, timezone
import errors as mglyph_errors
from db.pagination import PagedResponse
from calculate_score import calculate_score

from db.models.challengeModel import ChallengeModel
from db.models.userModel import UserModel
from db.models.evaluationRoundModel import EvaluationRoundModel
from db.models.challengeEvaluatorModel import ChallengeEvaluatorModel, InvitationState, InvitationType
from db.models.mglyphEvaluationModel import MGlyphEvaluationModel
from db.models.answerModel import AnsweredSymbol

from db.repos.challengeRepository import ChallengeRepository, ChallengeRepositoryDep
from db.repos.evaluationRoundRepository import EvaluationRoundRepository, EvaluationRoundRepositoryDep
from db.repos.challengeEvaluatorRepository import ChallengeEvaluatorRepository, ChallengeEvaluatorRepositoryDep
from db.repos.mglyphEvaluationRepository import MGlyphEvaluationRepository, MGlyphEvaluationRepositoryDep
from db.repos.answerRepository import AnswerRepository, AnswerRepositoryDep

from api.challenges.schemas import ChallengeFilterParams, ChallengeCreateDTO, ChallengeUpdateDTO, CreateAnswerDTO


class EvaluationRoundService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


    async def create_initial_evaluation_round(self, challenge_id: UUID, estimated_end_time: datetime) -> EvaluationRoundModel:
        evaluation_round = EvaluationRoundModel(
            id=None,
            sequence_number=1,
            estimated_end_time=estimated_end_time,
            challenge_id=challenge_id
        )
        self.db_session.add(evaluation_round)
        await self.db_session.commit()
        await self.db_session.refresh(evaluation_round)
        return evaluation_round



def get_evaluation_round_service(db_session: SessionDep):
    return EvaluationRoundService(db_session)

EvaluationRoundServiceDep = Annotated[EvaluationRoundService, Depends(get_evaluation_round_service)]





class AnswerService:
    def __init__(self, db_session: AsyncSession, answer_repository: AnswerRepository):
        self.db_session = db_session
        self.answer_repository = answer_repository

    def __evaluate_answer_correctness(self, answer: CreateAnswerDTO) -> bool:
        if answer.answered_symbol == AnsweredSymbol.equal:
            return answer.first_glyph_value == answer.second_glyph_value
        elif answer.answered_symbol == AnsweredSymbol.greater:
            return answer.first_glyph_value > answer.second_glyph_value
        elif answer.answered_symbol == AnsweredSymbol.less:
            return answer.first_glyph_value < answer.second_glyph_value

    async def bulk_add_answers(self, answers: list[CreateAnswerDTO], challenge_evaluator_id: UUID, evaluation_round_id: UUID, commit: bool = True):
        """
        NOTE: challenge_evaluator_id is id of ChallengeEvaluatorModel
        """
        # TODO: check if glyph is submitted in the challenge and if the evaluator is assigned to evaluate it
        answers_data = []
        for answer in answers:
            answer_data = answer.model_dump()
            answer_data["is_answer_correct"] = self.__evaluate_answer_correctness(answer)
            answer_data["glyph_distance"] = abs(answer.first_glyph_value - answer.second_glyph_value)
            if not answer_data["first_glyph_rotation_angle"]:
                answer_data["first_glyph_rotation_angle"] = 0.0
            if not answer_data["second_glyph_rotation_angle"]:
                answer_data["second_glyph_rotation_angle"] = 0.0
            answers_data.append(answer_data)

        await self.answer_repository.bulk_insert(answers_data, challenge_evaluator_id, evaluation_round_id)
        if commit:
            await self.db_session.commit()


def get_answer_service(db_session: SessionDep, answer_repository: AnswerRepositoryDep):
    return AnswerService(db_session, answer_repository)

AnswerServiceDep = Annotated[AnswerService, Depends(get_answer_service)]




class ChallengeEvaluatorService:
    def __init__(self, db_session: AsyncSession, challenge_evaluator_repository: ChallengeEvaluatorRepository):
        self.db_session = db_session
        self.challenge_evaluator_repository = challenge_evaluator_repository


    async def change_invitation_state_of_challenge_evaluator(self, challenge_id: UUID, evaluator_user_id: UUID, new_state: InvitationState, confirm_old_state: InvitationState | None = None, confirm_invitation_type: InvitationType | None = None) -> ChallengeEvaluatorModel:
        challenge_evaluator_db = await self.challenge_evaluator_repository.get_challenge_evaluator_by_challenge_id_and_user_id(challenge_id, evaluator_user_id, load_options=ChallengeEvaluatorRepository.LoadOptions(load_challenge=True))
        if not challenge_evaluator_db:
            raise mglyph_errors.NotFoundError("Challenge Evaluator link", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if challenge_evaluator_db.challenge.challenge_finished:
            raise mglyph_errors.BadRequestError("Challenge has already ended", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        if confirm_invitation_type is not None and challenge_evaluator_db.invitation_type != confirm_invitation_type:
            raise mglyph_errors.BadRequestError("Challenge Evaluator invitation type does not match", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        if confirm_old_state is not None and challenge_evaluator_db.invitation_state != confirm_old_state:
            raise mglyph_errors.BadRequestError("Challenge Evaluator state does not match", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        challenge_evaluator_db.invitation_state = new_state
        self.db_session.add(challenge_evaluator_db)
        await self.db_session.commit()
        return challenge_evaluator_db


    async def create_challenge_evaluator(self, challenge_id: UUID, evaluator_user_id: UUID, is_volunteer: bool) -> ChallengeEvaluatorModel:
        new_challenge_evaluator = ChallengeEvaluatorModel(
            id=None,
            challenge_id=challenge_id,
            evaluator_id=evaluator_user_id,
            invitation_type=InvitationType.volunteer if is_volunteer else InvitationType.invited,
            invitation_state=InvitationState.pending
        )
        self.db_session.add(new_challenge_evaluator)
        await self.db_session.commit()
        await self.db_session.refresh(new_challenge_evaluator)
        return new_challenge_evaluator

    async def get_paginated_challenge_evaluators_by_current_user_id(self, current_user_id: UUID, page: int = 1, size: int = 20, order_by: list[ChallengeEvaluatorRepository.OrderByOption] = None) -> PagedResponse[ChallengeEvaluatorModel]:
        current_user = await self.db_session.get(UserModel, current_user_id)
        if not current_user:
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        paged_challenge_evaluators = await self.challenge_evaluator_repository.get_paginated_challenge_evaluators_by_user_id(
            current_user_id,
            page=page,
            size=size,
            order_by=order_by,
            load_options=ChallengeEvaluatorRepository.LoadOptions(load_challenge=True, load_challenge_evaluation_rounds=True)
        )
        return paged_challenge_evaluators
    
    async def get_paginated_challenge_evaluators_by_challenge_id(self, challenge_id: UUID, page: int = 1, size: int = 20, order_by: list[ChallengeEvaluatorRepository.OrderByOption] = None) -> PagedResponse[ChallengeEvaluatorModel]:
        paged_challenge_evaluators = await self.challenge_evaluator_repository.get_paginated_challenge_evaluators_by_challenge_id(
            challenge_id,
            page=page,
            size=size,
            order_by=order_by,
            load_options=ChallengeEvaluatorRepository.LoadOptions(load_evaluator=True)
        )
        return paged_challenge_evaluators

def get_challenge_evaluator_service(db_session: SessionDep, challenge_evaluator_repository: ChallengeEvaluatorRepositoryDep):
    return ChallengeEvaluatorService(db_session, challenge_evaluator_repository)

ChallengeEvaluatorServiceDep = Annotated[ChallengeEvaluatorService, Depends(get_challenge_evaluator_service)]




# TODO: při přidělování challenge evaluator to mglyph (new mglyph evaluator) check if glyph is submitted



# TODO: přidat kontroly:
#           - challenge creation_time < glyph_submit_deadline < first evaluation round estimated_end_time
#           - při přidávání solvera zkontrolovat, že nejsou uzavřené submissiony
#           - při updatu zkontrolovat, že nenastane stav (submissions_ended = False and challenge_finished = True)
#           - při updatu zkontrolovat, že se nemění submissions_ended nebo challenge_finished z True na False

class ChallengeService:
    def __init__(
            self,
            db_session: AsyncSession,
            challenge_repository: ChallengeRepository,
            evaluation_round_repository: EvaluationRoundRepository,
            mglyph_evaluation_repository: MGlyphEvaluationRepository,
            challenge_evaluator_repository: ChallengeEvaluatorRepository,
            evaluation_round_service: EvaluationRoundService,
            challenge_evaluator_service: ChallengeEvaluatorService,
            answer_service: AnswerService
        ):
        self.db_session = db_session
        self.challenge_repository = challenge_repository
        self.evaluation_round_repository = evaluation_round_repository
        self.mglyph_evaluation_repository = mglyph_evaluation_repository
        self.challenge_evaluator_repository = challenge_evaluator_repository
        self.evaluation_round_service = evaluation_round_service
        self.challenge_evaluator_service = challenge_evaluator_service
        self.answer_service = answer_service


    async def get_challenge_by_id_with_user_relationship(self, challenge_id: UUID, current_user_id: UUID | None = None) -> tuple[ChallengeModel, dict | None]:
        db_challenge = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        if not db_challenge:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        
        user_relationship = None
        if current_user_id:
            user_relationship = (await self.challenge_repository.get_user_relationship_for_challenges(user_id=current_user_id, challenge_ids=[challenge_id])).get(challenge_id, None)

        return db_challenge, user_relationship


    
    async def get_paginated_challenges_with_glyphs_and_user_relationship(self, filters: ChallengeFilterParams, current_user_id: UUID | None = None, glyph_count: int = 0, page: int = 1, size: int = 20) -> PagedResponse[dict]:
        """
        Returns:
            tuple: Tuple containing the following elements:
                list: A list of dicts containing challenge, glyphs and user relationship information for each challenge in the paginated result.
                    Each dict has the following format:
                    {
                        "challenge": ChallengeModel,
                        "glyphs": list[MGlyphEvaluationModel],
                        "user_relationship": dict | None
                    }
                int: total number of challenges matching the filters (without pagination)
                int: total number of pages
                int: current page number
                int: page size
        """
        
        filter_params = ChallengeRepository.FilterParams(
            name_contains=filters.name_contains,
            state=[state.to_model_params() for state in filters.state] if filters.state else None
        )
        paginated_challenges_db = await self.challenge_repository.get_paginated_challenges(filters=filter_params, page=page, size=size, load_options=ChallengeRepository.LoadOptions(load_evaluation_rounds=True))
        challenge_ids = [challenge.id for challenge in paginated_challenges_db.items]
        glyphs_per_challenge = await self.mglyph_evaluation_repository.get_mglyph_evaluations_in_challenges(challenge_ids, only_submitted=True, order_by=MGlyphEvaluationRepository.OrderByOption.RANK_ASC, limit_per_challenge=glyph_count, load_options=MGlyphEvaluationRepository.LoadOptions(load_malleable_glyph=True, load_malleable_glyph_creator=True))
        user_relationships_per_challenge = await self.challenge_repository.get_user_relationship_for_challenges(user_id=current_user_id, challenge_ids=challenge_ids)
        paginated_challenges_db.items = [
            {
                "challenge": challenge,
                "glyphs": glyphs_per_challenge[challenge.id] if challenge.id in glyphs_per_challenge else [],
                "user_relationship": user_relationships_per_challenge[challenge.id] if challenge.id in user_relationships_per_challenge else None
            }
            for challenge in paginated_challenges_db.items
        ]
        return paginated_challenges_db
        


    async def get_paginated_challenges_where_user_is_participant_with_glyphs_and_user_relationship(self, user_id: UUID, filters: ChallengeFilterParams, as_solver: bool | None = None, glyph_count: int = 0, page: int = 1, size: int = 20) -> PagedResponse[dict]:
        filter_params = ChallengeRepository.FilterParams(
            name_contains=filters.name_contains,
            state=[state.to_model_params() for state in filters.state] if filters.state else None
        )
        paginated_challenges_db = await self.challenge_repository.get_paginated_challenges_with_participating_user(user_id=user_id, filters=filter_params, as_solver=as_solver, page=page, size=size, load_options=ChallengeRepository.LoadOptions(load_evaluation_rounds=True))
        challenge_ids = [challenge.id for challenge in paginated_challenges_db.items]
        glyphs_per_challenge = await self.mglyph_evaluation_repository.get_mglyph_evaluations_in_challenges(challenge_ids, only_submitted=True, order_by=MGlyphEvaluationRepository.OrderByOption.RANK_ASC, limit_per_challenge=glyph_count, load_options=MGlyphEvaluationRepository.LoadOptions(load_malleable_glyph=True, load_malleable_glyph_creator=True))
        user_relationships_per_challenge = await self.challenge_repository.get_user_relationship_for_challenges(user_id=user_id, challenge_ids=challenge_ids)
        paginated_challenges_db.items = [
            {
                "challenge": challenge,
                "glyphs": glyphs_per_challenge[challenge.id] if challenge.id in glyphs_per_challenge else [],
                "user_relationship": user_relationships_per_challenge[challenge.id] if challenge.id in user_relationships_per_challenge else None
            }
            for challenge in paginated_challenges_db.items
        ]
        return paginated_challenges_db
    


    async def get_paginated_challenges_with_evaluator_invites_info(self, filters: ChallengeFilterParams, order_by: list[ChallengeRepository.EvaluatorInvitesInfoOrderByOptions] | None = None, page: int = 1, size: int = 20) -> PagedResponse[dict]:
        """
        Returns:
            PagedResponse[dict]: A paginated response containing dicts with challenge information and evaluator invite states info for each challenge in the paginated result.
            Each dict has the following format:
                {
                    "challenge": ChallengeModel,
                    "active_evaluator_count": int,
                    "has_pending_invites": bool
                }
        """
        filter_params = ChallengeRepository.FilterParams(
            name_contains=filters.name_contains,
            state=[state.to_model_params() for state in filters.state] if filters.state else None
        )
        paginated_challenges = await self.challenge_repository.get_paginated_challenges_with_evaluator_invites_info(filters=filter_params, order_by=order_by, page=page, size=size, load_options=ChallengeRepository.LoadOptions(load_evaluation_rounds=True))
        return paginated_challenges



    async def create_challenge(self, challenge: ChallengeCreateDTO, current_user_id: UUID) -> ChallengeModel:
        try:
            challenge_data = challenge.model_dump()
            is_valid_unique_params = await self.challenge_repository.validate_unique_challenge_params(name=challenge_data["name"])
            if not is_valid_unique_params:
                raise mglyph_errors.BadRequestError("Challenge with the same name already exists", mglyph_errors.ErrorCode.BAD_REQUEST_CREATE_CHALLENGE_NAME_TAKEN)
            current_user = await self.db_session.get(UserModel, current_user_id)
            if not current_user:
                raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
            challenge_data["creator_id"] = current_user_id
            first_round_data = challenge_data.pop("first_evaluation_round")
            db_challenge = ChallengeModel.model_validate(challenge_data)
            db_challenge.id = None  # Ensure ID is None for new records
        except ValidationError as e:
            raise mglyph_errors.BadRequestError(f"Invalid challenge data: {e}")
        self.db_session.add(db_challenge)
        await self.db_session.flush()

        # Add first evaluation round
        await self.evaluation_round_service.create_initial_evaluation_round(db_challenge.id, first_round_data["estimated_end_time"])
        db_challenge = await self.challenge_repository.get_challenge_by_id(db_challenge.id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return db_challenge
    


    async def update_challenge(self, challenge_id: UUID, challenge_update: ChallengeUpdateDTO) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        challenge_data = challenge_update.model_dump(exclude_unset=True)
        is_valid_unique_params = await self.challenge_repository.validate_unique_challenge_params(name=challenge_data["name"], exclude_challenge_id=challenge_id)
        if not is_valid_unique_params:
            raise mglyph_errors.BadRequestError("Challenge with the same name already exists", mglyph_errors.ErrorCode.BAD_REQUEST_CREATE_CHALLENGE_NAME_TAKEN)
        challenge_db.sqlmodel_update(challenge_data)
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db
    


    async def end_challenge_submissions(self, challenge_id: UUID) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if challenge_db.challenge_finished:
            raise mglyph_errors.BadRequestError("This challenge has already ended", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        if challenge_db.submissions_ended:
            raise mglyph_errors.BadRequestError("Malleable glyph submissions for this challenge already ended", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        challenge_db.submissions_ended = True
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db
    


    async def end_challenge(self, challenge_id: UUID) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if challenge_db.submissions_ended == False:
            raise mglyph_errors.BadRequestError("Malleable glyph submissions for this challenge have not ended yet", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        if challenge_db.challenge_finished:
            raise mglyph_errors.BadRequestError("This challenge has already ended", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        challenge_db.challenge_finished = True
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db


    async def get_paginated_challenge_glyphs(self, challenge_id: UUID, order_by: MGlyphEvaluationRepository.OrderByOption | None, page: int = 1, size: int = 20) -> PagedResponse[MGlyphEvaluationModel]:
        if order_by is None:
            order_by = MGlyphEvaluationRepository.OrderByOption.RANK_ASC
        last_round = await self.evaluation_round_repository.get_last_round_in_challenge(challenge_id)
        if not last_round:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        return await self.mglyph_evaluation_repository.get_paginated_mglyph_evaluations_in_challenge_round(last_round.id, only_submitted=True, order_by=order_by, page=page, size=size, load_options=MGlyphEvaluationRepository.LoadOptions(load_malleable_glyph=True, load_malleable_glyph_creator=True))
    

    async def delete_challenge(self, challenge_id: UUID):
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        first_round = await self.evaluation_round_repository.get_first_round_in_challenge(challenge_id, load_options=EvaluationRoundRepository.LoadOptions(load_mglyph_evaluation_links=True))
        if first_round:
            if first_round.mglyph_evaluation_links:
                raise mglyph_errors.BadRequestError("Cannot delete challenge with existing assigned malleable glyphs", mglyph_errors.ErrorCode.BAD_REQUEST_DELETE_CONFLICT)
        await self.db_session.delete(challenge_db)
        await self.db_session.commit()
    

    async def add_solver_to_challenge(self, challenge_id: UUID, solver_id: UUID) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_solvers=True))
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if challenge_db.submissions_ended:
            raise mglyph_errors.BadRequestError("Challenge has ended submissions", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        user_db = await self.db_session.get(UserModel, solver_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if user_db in challenge_db.solvers:
            raise mglyph_errors.BadRequestError("User is already a solver of this challenge", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        challenge_db.solvers.append(user_db)
        self.db_session.add(challenge_db)
        await self.db_session.commit()
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_db.id, load_options=ChallengeRepository.LoadOptions(load_creator=True, load_solvers=True, load_challenge_evaluator_links=True, load_evaluation_rounds=True))
        return challenge_db

    
    async def add_evaluator_to_challenge(self, challenge_id: UUID, evaluator_id: UUID, is_volunteer: bool) -> ChallengeModel:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id, load_options=ChallengeRepository.LoadOptions(load_challenge_evaluator_links=True))
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if challenge_db.challenge_finished:
            raise mglyph_errors.BadRequestError("Challenge has already ended", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        user_db = await self.db_session.get(UserModel, evaluator_id)
        if not user_db:
            raise mglyph_errors.NotFoundError("User", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        for link in challenge_db.challenge_evaluator_links:
            if link.evaluator_id == evaluator_id:
                # TODO: ? is volunteer_pending and not is_volunteer -> change state to confirmed
                # TODO: ? if invited_pending and is_volunteer -> change state to confirmed
                raise mglyph_errors.BadRequestError("User is already an evaluator of this challenge", mglyph_errors.ErrorCode.BAD_REQUEST_ALREADY_DONE)
        await self.challenge_evaluator_service.create_challenge_evaluator(challenge_id, evaluator_id, is_volunteer)
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_db.id, load_options=ChallengeRepository.LoadOptions.all_options())
        return challenge_db


    async def get_mglyphs_for_evaluation(self, challenge_id: UUID, current_user_id: UUID) -> list[MGlyphEvaluationModel]:
        challenge_db = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge_db:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if challenge_db.challenge_finished:
            raise mglyph_errors.BadRequestError("Challenge has already ended", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        if not challenge_db.submissions_ended:
            raise mglyph_errors.BadRequestError("Challenge submissions have not ended yet", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        challenge_evaluator = await self.challenge_evaluator_repository.get_challenge_evaluator_by_challenge_id_and_user_id(challenge_id, current_user_id)
        if not challenge_evaluator or challenge_evaluator.invitation_state != InvitationState.confirmed:
            raise mglyph_errors.NotFoundError("Challenge Evaluator link", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        last_round = await self.evaluation_round_repository.get_last_round_in_challenge(challenge_id)
        if not last_round:
            raise mglyph_errors.NotFoundError("Challenge round", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        mglyph_evaluations = await self.mglyph_evaluation_repository.get_mglyph_evaluations_for_evaluation_round_and_evaluator(
            last_round.id,
            challenge_evaluator.id,
            only_submitted=True,
            load_options=MGlyphEvaluationRepository.LoadOptions(load_malleable_glyph=True, load_malleable_glyph_creator=True)
        )
        return mglyph_evaluations


    async def evaluate_challenge(self, challenge_id: UUID, current_user_id: UUID, answers: list[CreateAnswerDTO]):
        challenge = await self.challenge_repository.get_challenge_by_id(challenge_id)
        if not challenge:
            raise mglyph_errors.NotFoundError("Challenge", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        if challenge.challenge_finished:
            raise mglyph_errors.BadRequestError("Challenge has already ended", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        if not challenge.submissions_ended:
            raise mglyph_errors.BadRequestError("Challenge submissions have not ended yet", mglyph_errors.ErrorCode.BAD_REQUEST_WRONG_STATE)
        last_round = await self.evaluation_round_repository.get_last_round_in_challenge(challenge_id)
        if not last_round:
            raise mglyph_errors.NotFoundError("Challenge round", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        challenge_evaluator = await self.challenge_evaluator_repository.get_challenge_evaluator_by_challenge_id_and_user_id(challenge_id, current_user_id)
        if not challenge_evaluator or challenge_evaluator.invitation_state != InvitationState.confirmed:
            raise mglyph_errors.NotFoundError("Challenge Evaluator link", mglyph_errors.ErrorCode.NOT_FOUND_ID)
        try:
            await self.answer_service.bulk_add_answers(answers, challenge_evaluator.id, last_round.id, commit=False)
        except Exception as e:
            await self.db_session.rollback()
            raise mglyph_errors.BadRequestError(f"Error while adding answers - one or more answers might contain:\na) Mglyph for which user is not an assigned evaluator;\nb) Mglyph is not assigned to active challenge round;\nc) Mglyph does not exist;\nd) or otherwise invalid data.", mglyph_errors.ErrorCode.BAD_REQUEST_ADD_ANSWERS)
        malleable_glyph_ids = [answer.malleable_glyph_id for answer in answers]
        mglyph_evaluations_calculation_helpers = await self.mglyph_evaluation_repository.get_mglyph_evaluations_score_calculation_helpers(last_round.id, malleable_glyph_ids)
        mglyph_evaluations_scores = [{'id': mglyph_evaluation_id, 'score': calculate_score(answers_grouped_by_distance)} for mglyph_evaluation_id, answers_grouped_by_distance in mglyph_evaluations_calculation_helpers]
        await self.mglyph_evaluation_repository.bulk_update_score_of_mglyph_evaluations(mglyph_evaluations_scores, commit=False)
        await self.mglyph_evaluation_repository.update_rank_of_all_mglyph_evaluations_in_evaluation_round(last_round.id, commit=False)
        await self.db_session.commit()


def get_challenge_service(
        db_session: SessionDep,
        challenge_repository: ChallengeRepositoryDep,
        evaluation_round_repository: EvaluationRoundRepositoryDep,
        mglyph_evaluation_repository: MGlyphEvaluationRepositoryDep,
        challenge_evaluator_repository: ChallengeEvaluatorRepositoryDep,
        evaluation_round_service: EvaluationRoundServiceDep,
        challenge_evaluator_service: ChallengeEvaluatorServiceDep,
        answer_service: AnswerServiceDep
    ):
    return ChallengeService(db_session, challenge_repository, evaluation_round_repository, mglyph_evaluation_repository, challenge_evaluator_repository, evaluation_round_service, challenge_evaluator_service, answer_service)

ChallengeServiceDep = Annotated[ChallengeService, Depends(get_challenge_service)]
