import type { UUID } from 'crypto'
import { Temporal } from 'temporal-polyfill'

enum ChallengeStateEnum {
  open = 'Submissions Open',
  progress = 'Evaluation in Progress',
  finished = 'Results Finished',
}

function getChallengeStateEnumFromString(state: string): ChallengeStateEnum {
  if (state === 'finished') {
    return ChallengeStateEnum.finished
  } else if (state === 'evaluating') {
    return ChallengeStateEnum.progress
  } else {
    return ChallengeStateEnum.open
  }
}

class ChallengeSimple {
  id: UUID
  title: string
  start_time: Date
  submission_deadline: Date
  evaluation_deadline: Date
  state: ChallengeStateEnum

  constructor(
    id: UUID,
    title: string,
    start_time: Date,
    submission_deadline: Date,
    evaluation_deadline: Date,
    state: string,
  ) {
    this.id = id
    this.title = title
    this.start_time = start_time
    this.submission_deadline = submission_deadline
    this.evaluation_deadline = evaluation_deadline
    this.state = getChallengeStateEnumFromString(state)
  }
}

class User {
  id: UUID
  username: string

  constructor(id: UUID, username: string) {
    this.id = id
    this.username = username
  }
}

class ChallengeGlyph {
  id: UUID
  rank: number | null
  score: number | null
  author: User
  file_id: UUID
  flags: string[]

  constructor(
    id: UUID,
    rank: number | null,
    score: number | null,
    author: User,
    file_id: UUID,
    flags: string[],
  ) {
    this.id = id
    this.rank = rank
    this.score = score
    this.author = author
    this.file_id = file_id
    this.flags = flags
  }

  public static fromAPIResponse(apiResponse: any): ChallengeGlyph {
    return new ChallengeGlyph(
      apiResponse.malleable_glyph.id,
      apiResponse.rank,
      apiResponse.score,
      new User(
        apiResponse.malleable_glyph.creator.id,
        apiResponse.malleable_glyph.creator.username,
      ),
      apiResponse.malleable_glyph.zip_file_id,
      new Array<string>(), // TODO: Replace with actual flags from response
    )
  }
}

class FilterOption {
  label: string
  selected: boolean
  onClick: () => void

  constructor(label: string, selected: boolean = false, onClick: () => void = () => {}) {
    this.label = label
    this.onClick = onClick
    this.selected = selected
  }
}

enum ChallengeUserSolverRelationshipType {
  none = 'none',
  registered = 'registered',
  mglyph_uploaded = 'mglyph_uploaded',
  mglyph_submitted = 'mglyph_submitted',
}

function getChallengeUserSolverRelationshipTypeFromString(
  relationship: string,
): ChallengeUserSolverRelationshipType {
  if (relationship === 'registered') {
    return ChallengeUserSolverRelationshipType.registered
  } else if (relationship === 'mglyph_submitted') {
    return ChallengeUserSolverRelationshipType.mglyph_submitted
  } else if (relationship === 'mglyph_uploaded') {
    return ChallengeUserSolverRelationshipType.mglyph_uploaded
  } else {
    return ChallengeUserSolverRelationshipType.none
  }
}

class ChallengeUserSolverRelationship {
  relationship_type: ChallengeUserSolverRelationshipType
  malleable_glyph_id?: UUID

  constructor(relationship_type: ChallengeUserSolverRelationshipType, malleable_glyph_id?: UUID) {
    this.relationship_type = relationship_type
    this.malleable_glyph_id = malleable_glyph_id
  }
}

enum ChallengeUserEvaluatorRelationshipType {
  none = 'none',
  registered = 'registered',
  pending_volunteer = 'pending_volunteer',
  pending_invited = 'pending_invited',
  rejected_volunteer = 'rejected_volunteer',
  rejected_invited = 'rejected_invited',
  evaluation_awaiting = 'evaluation_awaiting',
  evaluation_finished = 'evaluation_finished',
}

function getChallengeUserEvaluatorRelationshipTypeFromString(
  relationship: string,
): ChallengeUserEvaluatorRelationshipType {
  if (relationship === 'evaluation_awaiting') {
    return ChallengeUserEvaluatorRelationshipType.evaluation_awaiting
  } else if (relationship === 'evaluation_finished') {
    return ChallengeUserEvaluatorRelationshipType.evaluation_finished
  } else if (relationship === 'registered') {
    return ChallengeUserEvaluatorRelationshipType.registered
  } else if (relationship === 'pending_volunteer') {
    return ChallengeUserEvaluatorRelationshipType.pending_volunteer
  } else if (relationship === 'pending_invited') {
    return ChallengeUserEvaluatorRelationshipType.pending_invited
  } else if (relationship === 'rejected_volunteer') {
    return ChallengeUserEvaluatorRelationshipType.rejected_volunteer
  } else if (relationship === 'rejected_invited') {
    return ChallengeUserEvaluatorRelationshipType.rejected_invited
  } else {
    return ChallengeUserEvaluatorRelationshipType.none
  }
}

class ChallengeMiniDetail {
  challenge: ChallengeSimple
  glyphs: ChallengeGlyph[]
  user_relationship: {
    user_solver_relationship?: ChallengeUserSolverRelationship
    user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
  } | null

  constructor(
    challenge: ChallengeSimple,
    glyphs: ChallengeGlyph[],
    user_relationship: {
      user_solver_relationship?: ChallengeUserSolverRelationship
      user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
    } | null,
  ) {
    this.challenge = challenge
    this.glyphs = glyphs
    this.user_relationship = user_relationship
  }

  public static fromAPIResponse(apiResponse: any): ChallengeMiniDetail {
    const challenge = new ChallengeSimple(
      apiResponse.id,
      apiResponse.name,
      new Date(apiResponse.creation_time),
      new Date(apiResponse.glyph_submit_deadline),
      new Date(apiResponse.last_evaluation_round.estimated_end_time),
      apiResponse.state,
    )
    const glyphs = apiResponse.mglyph_evaluations.map((glyph: any) => {
      return ChallengeGlyph.fromAPIResponse(glyph)
    })
    const user_relationship = {
      user_solver_relationship: new ChallengeUserSolverRelationship(
        getChallengeUserSolverRelationshipTypeFromString(
          apiResponse.user_relationship?.solver_relationship.relationship_type ?? 'none',
        ),
        apiResponse.user_relationship?.solver_relationship.malleable_glyph_id,
      ),
      user_evaluator_relationship: getChallengeUserEvaluatorRelationshipTypeFromString(
        apiResponse.user_relationship?.evaluator_relationship?.relationship_type ?? 'none',
      ),
    }
    return new ChallengeMiniDetail(challenge, glyphs, user_relationship)
  }
}

class ChallengeDetail {
  challenge: ChallengeSimple
  user_relationship: {
    user_solver_relationship?: ChallengeUserSolverRelationship
    user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
  } | null

  constructor(
    challenge: ChallengeSimple,
    user_relationship: {
      user_solver_relationship?: ChallengeUserSolverRelationship
      user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
    } | null,
  ) {
    this.challenge = challenge
    this.user_relationship = user_relationship
  }

  public static fromAPIResponse(apiResponse: any): ChallengeDetail {
    const last_evaluation_round = apiResponse.rounds.find(
      (round: any) => round.next_round_id === null,
    )
    const challenge = new ChallengeSimple(
      apiResponse.id,
      apiResponse.name,
      new Date(apiResponse.creation_time),
      new Date(apiResponse.glyph_submit_deadline),
      new Date(last_evaluation_round.estimated_end_time),
      apiResponse.state,
    )
    const user_relationship = {
      user_solver_relationship: new ChallengeUserSolverRelationship(
        getChallengeUserSolverRelationshipTypeFromString(
          apiResponse.user_relationship?.solver_relationship.relationship_type ?? 'none',
        ),
        apiResponse.user_relationship?.solver_relationship.malleable_glyph_id,
      ),
      user_evaluator_relationship: getChallengeUserEvaluatorRelationshipTypeFromString(
        apiResponse.user_relationship?.evaluator_relationship?.relationship_type ?? 'none',
      ),
    }
    return new ChallengeDetail(challenge, user_relationship)
  }
}

class PaginatedData<T> {
  items: T[]
  total_count: number
  total_pages: number
  current_page: number
  page_size: number

  constructor(
    items: T[],
    total_count: number,
    total_pages: number,
    current_page: number,
    page_size: number,
  ) {
    this.items = items
    this.total_count = total_count
    this.total_pages = total_pages
    this.current_page = current_page
    this.page_size = page_size
  }

  public static fromAPIResponse<T>(
    apiResponse: any,
    itemFromAPIResponse: (item: any) => T,
  ): PaginatedData<T> {
    const items = apiResponse.items.map(itemFromAPIResponse)
    return new PaginatedData(
      items,
      apiResponse.total,
      apiResponse.total_pages,
      apiResponse.page,
      apiResponse.size,
    )
  }
}

class MGlyphDetail {
  id: UUID
  short_name: string
  long_name: string
  last_updated: Date
  submission_time: Date | null
  file_id: UUID
  author: User
  code: string | null
  is_code_public: boolean
  challenge: { id: UUID; title: string; state: ChallengeStateEnum }
  evaluation: { id: UUID; rank: number; score: number }

  constructor(
    id: UUID,
    short_name: string,
    long_name: string,
    last_updated: Date,
    submission_time: Date | null,
    file_id: UUID,
    author: User,
    code: string | null,
    is_code_public: boolean,
    challenge: { id: UUID; title: string; state: ChallengeStateEnum },
    evaluation: { id: UUID; rank: number; score: number },
  ) {
    this.id = id
    this.short_name = short_name
    this.long_name = long_name
    this.last_updated = last_updated
    this.submission_time = submission_time
    this.file_id = file_id
    this.author = author
    this.code = code
    this.is_code_public = is_code_public
    this.challenge = challenge
    this.evaluation = evaluation
  }

  public static fromAPIResponse(apiResponse: any): MGlyphDetail {
    return new MGlyphDetail(
      apiResponse.id,
      apiResponse.short_name,
      apiResponse.long_name,
      new Date(apiResponse.last_updated_time),
      apiResponse.submission_time ? new Date(apiResponse.submission_time) : null,
      apiResponse.zip_file_id,
      new User(apiResponse.creator.id, apiResponse.creator.username),
      apiResponse.code,
      apiResponse.is_code_public,
      {
        id: apiResponse.challenge.id,
        title: apiResponse.challenge.name,
        state: getChallengeStateEnumFromString(apiResponse.challenge.state),
      },
      {
        id: apiResponse.last_evaluation.id,
        rank: apiResponse.last_evaluation.rank,
        score: apiResponse.last_evaluation.score,
      },
    )
  }
}

class ChallengeEvaluatorInvitesInfo {
  challenge: ChallengeSimple
  active_evaluator_count: number
  has_pending_invites: boolean

  constructor(
    challenge: ChallengeSimple,
    active_evaluator_count: number,
    has_pending_invites: boolean,
  ) {
    this.challenge = challenge
    this.active_evaluator_count = active_evaluator_count
    this.has_pending_invites = has_pending_invites
  }

  public static fromAPIResponse(apiResponse: any): ChallengeEvaluatorInvitesInfo {
    const challenge = new ChallengeSimple(
      apiResponse.challenge.id,
      apiResponse.challenge.name,
      new Date(apiResponse.challenge.creation_time),
      new Date(apiResponse.challenge.glyph_submit_deadline),
      new Date(apiResponse.challenge.last_evaluation_round.estimated_end_time),
      apiResponse.challenge.state,
    )
    return new ChallengeEvaluatorInvitesInfo(
      challenge,
      apiResponse.active_evaluator_count,
      apiResponse.has_pending_invites,
    )
  }
}

enum InvitationStateEnum {
  pending = 'pending',
  confirmed = 'confirmed',
  rejected = 'rejected',
}

function getInvitationStateEnumFromString(state: string): InvitationStateEnum {
  if (state === 'confirmed') {
    return InvitationStateEnum.confirmed
  } else if (state === 'rejected') {
    return InvitationStateEnum.rejected
  } else {
    return InvitationStateEnum.pending
  }
}

enum InvitationTypeEnum {
  volunteer = 'volunteer',
  invited = 'invited',
}

function getInvitationTypeEnumFromString(type: string): InvitationTypeEnum {
  if (type === 'invited') {
    return InvitationTypeEnum.invited
  } else {
    return InvitationTypeEnum.volunteer
  }
}

class ChallengeEvaluatorInfoBase {
  id: UUID
  invitation_state: InvitationStateEnum
  invitation_type: InvitationTypeEnum

  constructor(
    id: UUID,
    invitation_state: InvitationStateEnum,
    invitation_type: InvitationTypeEnum,
  ) {
    this.id = id
    this.invitation_state = invitation_state
    this.invitation_type = invitation_type
  }
}

class ChallengeEvaluatorInfoWithChallenge extends ChallengeEvaluatorInfoBase {
  challenge: ChallengeSimple

  constructor(
    id: UUID,
    invitation_state: InvitationStateEnum,
    invitation_type: InvitationTypeEnum,
    challenge: ChallengeSimple,
  ) {
    super(id, invitation_state, invitation_type)
    this.challenge = challenge
  }

  public static fromAPIResponse(apiResponse: any): ChallengeEvaluatorInfoWithChallenge {
    const challenge = new ChallengeSimple(
      apiResponse.challenge.id,
      apiResponse.challenge.name,
      new Date(apiResponse.challenge.creation_time),
      new Date(apiResponse.challenge.glyph_submit_deadline),
      new Date(apiResponse.challenge.last_evaluation_round.estimated_end_time),
      apiResponse.challenge.state,
    )
    return new ChallengeEvaluatorInfoWithChallenge(
      apiResponse.id,
      getInvitationStateEnumFromString(apiResponse.invitation_state),
      getInvitationTypeEnumFromString(apiResponse.invitation_type),
      challenge,
    )
  }
}

class ChallengeEvaluatorInfoWithEvaluator extends ChallengeEvaluatorInfoBase {
  evaluator: User

  constructor(
    id: UUID,
    invitation_state: InvitationStateEnum,
    invitation_type: InvitationTypeEnum,
    evaluator: User,
  ) {
    super(id, invitation_state, invitation_type)
    this.evaluator = evaluator
  }

  public static fromAPIResponse(apiResponse: any): ChallengeEvaluatorInfoWithEvaluator {
    const evaluator = new User(apiResponse.evaluator.id, apiResponse.evaluator.username)
    return new ChallengeEvaluatorInfoWithEvaluator(
      apiResponse.id,
      getInvitationStateEnumFromString(apiResponse.invitation_state),
      getInvitationTypeEnumFromString(apiResponse.invitation_type),
      evaluator,
    )
  }
}

class EvaluateAnswer {
  malleable_glyph_id: UUID
  first_glyph_value: number
  second_glyph_value: number
  glyph_distance: number
  answered_symbol: 'greater' | 'equal' | 'less'
  time_taken: Temporal.Duration
  rotation_type?: 'same' | 'different'
  first_glyph_rotation_angle?: number
  second_glyph_rotation_angle?: number

  constructor(
    malleable_glyph_id: UUID,
    first_glyph_value: number,
    second_glyph_value: number,
    glyph_distance: number,
    answered_symbol: 'greater' | 'equal' | 'less',
    time_taken: Temporal.Duration,
    rotation_type?: 'same' | 'different',
    first_glyph_rotation_angle?: number,
    second_glyph_rotation_angle?: number,
  ) {
    this.first_glyph_value = first_glyph_value
    this.second_glyph_value = second_glyph_value
    this.glyph_distance = glyph_distance
    this.answered_symbol = answered_symbol
    this.time_taken = time_taken
    this.rotation_type = rotation_type
    this.malleable_glyph_id = malleable_glyph_id
    this.first_glyph_rotation_angle = first_glyph_rotation_angle
    this.second_glyph_rotation_angle = second_glyph_rotation_angle
  }
}

export {
  ChallengeStateEnum,
  ChallengeSimple,
  ChallengeGlyph,
  User,
  ChallengeMiniDetail,
  PaginatedData,
  FilterOption,
  ChallengeUserSolverRelationshipType,
  ChallengeUserSolverRelationship,
  ChallengeUserEvaluatorRelationshipType,
  ChallengeDetail,
  MGlyphDetail,
  ChallengeEvaluatorInvitesInfo,
  InvitationStateEnum,
  InvitationTypeEnum,
  ChallengeEvaluatorInfoWithChallenge,
  ChallengeEvaluatorInfoWithEvaluator,
  EvaluateAnswer,
}
