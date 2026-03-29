import type { LocationQuery } from 'vue-router'

function initializePageFromQuery(query: LocationQuery): number {
  var newpage = 1
  const pageParam = query.page
  if (typeof pageParam === 'string') {
    const pageNum = parseInt(pageParam, 10)
    if (!isNaN(pageNum) && pageNum > 0) {
      newpage = pageNum
    }
  }
  return newpage
}

function changePageInQuery(query: LocationQuery, page: number): LocationQuery {
  const newQuery = { ...query }
  if (page === 1) {
    delete newQuery.page
  } else {
    newQuery.page = page.toString()
  }
  return newQuery
}

export { initializePageFromQuery, changePageInQuery }
