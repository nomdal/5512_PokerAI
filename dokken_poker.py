
import random

possible_hands = range(10)
possible_bets = range(10)

def randomHand():
	return random.randrange(10)

# bet completely randomly
def probBetGivenHand_uniform(bet, hand):
	return 1.0 / 10.0

# bet roughly proportional to hand strength
def probBetGivenHand_1(bet, hand):
	table = {
		0: [0.7, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
		1: [0.3, 0.4, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
		2: [0.1, 0.2, 0.4, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0],
		3: [0.0, 0.1, 0.2, 0.4, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0],
		4: [0.0, 0.0, 0.1, 0.2, 0.4, 0.2, 0.1, 0.0, 0.0, 0.0],
		5: [0.0, 0.0, 0.0, 0.1, 0.2, 0.4, 0.2, 0.1, 0.0, 0.0],
		6: [0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.4, 0.2, 0.1, 0.0],
		7: [0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.4, 0.2, 0.1],
		8: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.4, 0.3],
		9: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.7],
	}
	return table[hand][bet]

# bet strongest hands for value and weakest hands as a bluff
def probBetGivenHand_2(bet, hand):
	handsToBet = [0, 1, 6, 7, 8, 9]
	if bet == 4 and hand in handsToBet:
		return 1
	elif bet == 0 and hand not in handsToBet:
		return 1
	else:
		return 0

# generate opponent's bet according to probability function
def randomBet(hand, probBetGivenHand):
	r = random.random()
	for bet in range(10):
		r -= probBetGivenHand(bet, hand)
		if r <= 0:
			return bet
	print("error: probs sum to less than 1?")
	return 0

# expected value of our action given our hand, opponent's hand, bet, and pot size
def E_action(action, ourHand, oppHand, bet, potSize):
	if action == "fold":
		return 0
	elif action == "call":
		if ourHand > oppHand:
			return potSize + bet
		elif ourHand == oppHand:
			return potSize / 2.0
		elif ourHand < oppHand:
			return -bet

# return the highest expected value action given our hand, the bet, pot size, and our guess of opponent's betting function
def bestAction(ourHand, bet, potSize, probBetGivenHand):
	e = 0
	for oppHand in range(10):
		e += probBetGivenHand(bet, oppHand) * E_action("call", ourHand, oppHand, bet, potSize)
	if e > 0:
		return "call"
	else:
		return "fold"

# return our net gain/loss for the hand
def playHand():
	ante = 2
	potSize = 2 * ante
	oppHand = randomHand()
	ourHand = randomHand()
	bet = randomBet(oppHand, probBetGivenHand_1)
	#print("ourHand = %d, oppHand = %d, bet = %d" % (ourHand, oppHand, bet))
	ourAction = bestAction(ourHand, bet, potSize, probBetGivenHand_uniform)
	if ourAction == "fold":
		#print("fold")
		return -ante
	elif ourAction == "call":
		if ourHand > oppHand:
			#print("call, won pot")
			return ante + bet
		elif ourHand == oppHand:
			#print("call, split pot")
			return 0
		elif ourHand < oppHand:
			#print("call, lost pot")
			return -(ante + bet)
			
def run():
	winnings = 0
	numHands = 10000
	for i in range(numHands):
		winnings += playHand()
	print("numHands = %d" % (numHands))
	print("total winnings = %d" % (winnings))
	print("winnings per hand = %f" % (winnings / numHands))

run()


