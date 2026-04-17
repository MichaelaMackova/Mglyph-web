function debounce<T extends (...args: Parameters<T>) => ReturnType<T>>(
  func: T,
  delay: number | undefined,
): (...args: Parameters<T>) => void {
  let timeout: string | number | NodeJS.Timeout | undefined
  return function (this: ThisParameterType<T>, ...args: Parameters<T>) {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      func.apply(this, args)
    }, delay)
  }
}

export { debounce }
