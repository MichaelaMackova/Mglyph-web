function dateToLocalISOLikeString(date: Date, withSeconds = false): string {
  const isoLikeString = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(
    date.getDate(),
  ).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}:${String(
    date.getMinutes(),
  ).padStart(2, '0')}`
  if (withSeconds) {
    return `${isoLikeString}:${String(date.getSeconds()).padStart(2, '0')}`
  }
  return isoLikeString
}

function validateDateIsInFuture(dateStr: string): boolean {
  const inputDate = new Date(dateStr)
  const now = new Date()
  return inputDate > now
}

export { dateToLocalISOLikeString, validateDateIsInFuture }
