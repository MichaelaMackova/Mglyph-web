enum ApiResponseCode {
  Unauthorized = 401,
  Forbidden = 403,
  NotFound = 404,
  InternalServerError = 500,
  TokenExpired = 498,
}

class ApiError extends Error {
  public code: ApiResponseCode

  constructor(code: ApiResponseCode, message?: string) {
    super(message)
    this.name = 'ApiError'
    this.code = code
  }
}

export { ApiError, ApiResponseCode }
