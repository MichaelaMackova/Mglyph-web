enum ApiErrorCode {
  Unauthorized = 401,
  Forbidden = 403,
  NotFound = 404,
  InternalServerError = 500,
  TokenExpired = 498,
}

class ApiError extends Error {
  public code: ApiErrorCode

  constructor(code: ApiErrorCode, message?: string) {
    super(message)
    this.name = 'ApiError'
    this.code = code
  }
}

export { ApiError, ApiErrorCode }
