# python scratch sheet for [⊼₂] nand2tetris2's OS unit: math.jack
# :author kiwi
# :date 2023.07.31


def multiply(x: int, y: int):
	result: int = 0
	shiftedX: int = x

	w: int = 15  # word length in jack
	for i in range(w):  # recall range(3) gives [0, 1, 2]
		# output i-th bit of y
		if getIthBit(y, i) == 1:
			result += shiftedX
		shiftedX += shiftedX
	return result


# returns a string of the binary representation of the input base 10 number
def getBinaryStr(number: int) -> str:
	binaryRep: str = bin(number)

	# the binary representation is prefixed with '0b'. slice to get rid of it
	return binaryRep[2:]


# returns padded binary string to 16-bit word: 15 → 0000000000001111
def getBinaryStrPadded(number: int) -> str:
	return format(number, '016b')


# returns the i-th bit of the input number
def getIthBit(number: int, i: int) -> int:
	wordLength: int = 16

	# get 16-bit padded binary string for the input number
	binaryRep: str = getBinaryStrPadded(number)

	# return the i-th bit
	result: str = binaryRep[wordLength - 1 - i]
	assert result in ['0', '1']

	return int(result)


# eyeball test for multiply methods
def multTest():
	target: int = 14
	for index in range(16):
		print(f'the {index}-th bit of {target} is {getIthBit(target, index)}')

	print(f'{multiply(0, 0)}')


# log n runtime division algorithm
# uses the recursive logic → x/y is equal to twice of x/2y
# 	plus some adjustment for large remainders
def divide(dividend: int, divisor: int) -> int:
	"""
	:param dividend: the number we're dividing
	:param divisor: what we're dividing by
	:return: result of integer division: dividend/divisor
	"""
	assert dividend != 0

	if divisor > dividend:
		return 0

	quotient: int = divide(dividend, 2 * divisor)
	remainder: int = dividend - 2 * divisor * quotient

	if remainder >= divisor:
		return 2 * quotient + 1
	else:
		return 2 * quotient


# eyeball test for divide method
# 🐛 range started at 0. exceeded recursion limit because division by zero
# 🐛 checking remainder > divisor instead of remainder >= divisor
def divideTest():
	dividend: int = 32
	for index in range(1, 17):
		print(f'🐳 {dividend}/{index}={divide(dividend, index)}')


divideTest()