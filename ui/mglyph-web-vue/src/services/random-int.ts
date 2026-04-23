function getRandomInt(min: number, max: number, digits?: number): number {
  if (digits != undefined) {
    min = (min / 100) * 10 ** digits
    max = (max / 100) * 10 ** digits
  }

  let randomInt = Math.floor(Math.random() * (max - min + 1)) + min

  if (digits != undefined) {
    return (randomInt / 10 ** digits) * 100
  }

  return randomInt
}

export { getRandomInt }
