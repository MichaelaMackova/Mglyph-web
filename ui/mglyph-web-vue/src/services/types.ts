import type { UUID } from 'crypto'

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
  rank: number
  author: User
  // glyph_src: ???
  flags: string[]

  constructor(id: UUID, rank: number, author: User, flags: string[]) {
    this.id = id
    this.rank = rank
    this.author = author
    this.flags = flags
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
  mglyph_submitted = 'mglyph_submitted',
}

function getChallengeUserSolverRelationshipTypeFromString(
  relationship: string,
): ChallengeUserSolverRelationshipType {
  if (relationship === 'registered') {
    return ChallengeUserSolverRelationshipType.registered
  } else if (relationship === 'mglyph_submitted') {
    return ChallengeUserSolverRelationshipType.mglyph_submitted
  } else {
    return ChallengeUserSolverRelationshipType.none
  }
}

enum ChallengeUserEvaluatorRelationshipType {
  none = 'none',
  registered = 'registered',
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
  } else {
    return ChallengeUserEvaluatorRelationshipType.none
  }
}

class ChallengeMiniDetail {
  challenge: ChallengeSimple
  glyphs: ChallengeGlyph[]
  user_relationship: {
    user_solver_relationship?: ChallengeUserSolverRelationshipType
    user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
  } | null

  constructor(
    challenge: ChallengeSimple,
    glyphs: ChallengeGlyph[],
    user_relationship: {
      user_solver_relationship?: ChallengeUserSolverRelationshipType
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
      new Date(2022, 0, 1), // TODO: Replace with actual evaluation deadline from response
      apiResponse.state,
    )
    const glyphs = apiResponse.mglyph_evaluations.map((glyph: any) => {
      return new ChallengeGlyph(
        glyph.malleable_glyph.id,
        glyph.rank,
        new User(glyph.malleable_glyph.creator.id, glyph.malleable_glyph.creator.username),
        new Array<string>(), // TODO: Replace with actual flags from response
      )
    })
    const user_relationship = {
      user_solver_relationship: getChallengeUserSolverRelationshipTypeFromString(
        apiResponse.user_relationship?.solver_relationship ?? 'none',
      ),
      user_evaluator_relationship: getChallengeUserEvaluatorRelationshipTypeFromString(
        apiResponse.user_relationship?.evaluator_relationship ?? 'none',
      ),
    }
    return new ChallengeMiniDetail(challenge, glyphs, user_relationship)
  }
}

class ChallengeDetail {
  challenge: ChallengeSimple
  user_relationship: {
    user_solver_relationship?: ChallengeUserSolverRelationshipType
    user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
  } | null

  constructor(
    challenge: ChallengeSimple,
    user_relationship: {
      user_solver_relationship?: ChallengeUserSolverRelationshipType
      user_evaluator_relationship?: ChallengeUserEvaluatorRelationshipType
    } | null,
  ) {
    this.challenge = challenge
    this.user_relationship = user_relationship
  }

  public static fromAPIResponse(apiResponse: any): ChallengeDetail {
    const challenge = new ChallengeSimple(
      apiResponse.id,
      apiResponse.name,
      new Date(apiResponse.creation_time),
      new Date(apiResponse.glyph_submit_deadline),
      new Date(2022, 0, 1), // TODO: Replace with actual evaluation deadline from response
      apiResponse.state,
    )
    const user_relationship = {
      user_solver_relationship: getChallengeUserSolverRelationshipTypeFromString(
        apiResponse.user_relationship?.solver_relationship ?? 'none',
      ),
      user_evaluator_relationship: getChallengeUserEvaluatorRelationshipTypeFromString(
        apiResponse.user_relationship?.evaluator_relationship ?? 'none',
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
  ChallengeUserEvaluatorRelationshipType,
  ChallengeDetail,
}
