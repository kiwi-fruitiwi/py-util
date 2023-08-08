# python scratch sheet for [⊼₂] nand2tetris2's OS unit: math.jack
# :author kiwi
# :date 2023.07.31
import random
accumulatedProduct: int = 0


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
	# format(number, '016b')
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
	# dividend - accumulatedProduct = remainder
	global accumulatedProduct
	assert dividend != 0

	if divisor > dividend:
		# every divide call is guaranteed to reach the base case first
		# we reset accumulatedProduct here
		# on the first return after the base case, we're guaranteed our
		# accumulatedProduct is equal to the divisor, as it's the smallest value
		# before doubling it makes it exceed the dividend.
		#
		# e.g. in 16/3, the divisor increases like this: [3, 6, 12, 24]
		# 	on 24, we reach the base case and return 0
		#	on 12, the accumulated product is the divisor itself, 12
		#	on divisor=6, the accumulated product is still 12
		#		because divide(16, 12) returns 2q+1=1 ← q=0 from divide(16, 24)
		# the multiply-based accumulatedProduct expression is
		#	2 * divisor * quotient
		# and the remainder is thus dividend - (2 * divisor * quotient)
		accumulatedProduct = 0
		return 0

	accumulatedProduct = divisor

	# TODO how can we accumulate 2 * quotient * divisor in our recursive call?
	quotient: int = divide(dividend, 2 * divisor)

	# TODO prof. schocken says this algorithm only requires addition
	# 	how can we find divisor * quotient?
	# quotient = dividend / divisor
	# divisor * quotient = dividend?
	# remainder: int = dividend - 2 * divisor * quotient
	remainder: int = dividend - accumulatedProduct

	# information whether it's +1 or just 2 * quotient is only present here
	# how do we transfer this out of this return function?
	if remainder >= divisor:
		accumulatedProduct += divisor
		return 2 * quotient + 1
	else:
		# previous does not change
		return 2 * quotient


# eyeball test for divide method
# 🐛 range started at 0. exceeded recursion limit because division by zero
# 🐛 checking remainder > divisor instead of remainder >= divisor
def simpleDivideTest():
	dividend: int = 32
	for index in range(1, 10):
		print(f'🐳 {dividend}/{index}={divide(dividend, index)}')


# use python integer division to test our divide algorithm
def randomDivideTest():
	for trialNum in range(100):
		dividend: int = random.randint(1, 32768)
		divisor: int = random.randint(1, 32768)

		quotient: int = int(dividend / divisor)
		print(f'{dividend} / {divisor} = {quotient}')
		assert divide(dividend, divisor) == quotient


# the sqrt function has two appealing properties:
# 	its inverse function n² can be easily calculated
#	the function is monotonically increasing, allowing for search
#
# this is similar to finding the binary representation of a decimal number,
# except you square each result to check if it exceeds the number. this bit flip
# strategy from most significant to least significant place value ensures we'll
# find the integer square root.
def sqrt():
	# y = 0
	# for j = n/2-1 to 0:
	# 	if (y+2^j)² ≤ x:
	#		y += 2^j
	# return y

	pass


randomDivideTest()
# simpleDivideTest()