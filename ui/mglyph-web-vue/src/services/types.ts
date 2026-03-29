import type { UUID } from 'crypto'

enum ChallengeStateEnum {
  open = 'Submissions Open',
  progress = 'Evaluation in Progress',
  finished = 'Results Finished',
}

class ChallengeSimple {
  id: UUID
  title: string
  start_time: Date
  end_time: Date
  state: ChallengeStateEnum

  constructor(id: UUID, title: string, start_time: Date, end_time: Date, state: string) {
    this.id = id
    this.title = title
    this.start_time = start_time
    this.end_time = end_time
    if (state === 'finished') {
      this.state = ChallengeStateEnum.finished
    } else if (state === 'evaluating') {
      this.state = ChallengeStateEnum.progress
    } else {
      this.state = ChallengeStateEnum.open
    }
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

enum ChallengeUserEvaluatorRelationshipType {
  none = 'none',
  registered = 'registered',
  evaluation_awaiting = 'evaluation_awaiting',
  evaluation_finished = 'evaluation_finished',
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
      new Date(2021, 0, 1), // TODO: Replace with actual start time from response,
      new Date(apiResponse.glyph_submit_deadline), // TODO: Replace with actual end time from response
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
    let solver_relationship = ChallengeUserSolverRelationshipType.none
    if (apiResponse.user_relationship?.solver_relationship) {
      const apiSolverRelationship: string = apiResponse.user_relationship.solver_relationship
      if (apiSolverRelationship === 'registered') {
        solver_relationship = ChallengeUserSolverRelationshipType.registered
      } else if (apiSolverRelationship === 'mglyph_submitted') {
        solver_relationship = ChallengeUserSolverRelationshipType.mglyph_submitted
      }
    }
    let evaluator_relationship = ChallengeUserEvaluatorRelationshipType.none
    if (apiResponse.user_relationship?.evaluator_relationship) {
      const apiEvaluatorRelationship: string = apiResponse.user_relationship.evaluator_relationship
      if (apiEvaluatorRelationship === 'evaluation_awaiting') {
        evaluator_relationship = ChallengeUserEvaluatorRelationshipType.evaluation_awaiting
      } else if (apiEvaluatorRelationship === 'evaluation_finished') {
        evaluator_relationship = ChallengeUserEvaluatorRelationshipType.evaluation_finished
      } else if (apiEvaluatorRelationship === 'registered') {
        evaluator_relationship = ChallengeUserEvaluatorRelationshipType.registered
      }
    }
    const user_relationship = {
      user_solver_relationship: solver_relationship,
      user_evaluator_relationship: evaluator_relationship,
    }
    return new ChallengeMiniDetail(challenge, glyphs, user_relationship)
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
}
