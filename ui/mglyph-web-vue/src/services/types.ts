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

  constructor(
    id: UUID,
    title: string,
    start_time: Date,
    end_time: Date,
    state: string
  ) {
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

export { ChallengeStateEnum, ChallengeSimple, ChallengeGlyph, User }
