
# https://en.wikipedia.org/wiki/Fictitious_play
# If fictitious play converges to any distribution, then it must be a nash equilibrium
# If the game satisfies 4 properties, then fictitious play is guaranteed to converge

import random

possible_hands = range(10) # possible hand strengths
possible_p1Actions = range(10) # possible bet sizes
possible_p2Actions = ["fold", "call"]

def randomHand():
	return random.choice(possible_hands)

# value of hand from player 1 point of view given both hands, both actions, and the pot size
def valueP1Action(p1Hand, p1Action, p2Hand, p2Action, potSize):
	if p2Action == "fold":
		return potSize / 2.0
	elif p2Action == "call":
		if p1Hand > p2Hand:
			return (p1Action + potSize / 2.0)
		elif p1Hand == p2Hand:
			return 0
		elif p1Hand < p2Hand:
			return -(p1Action + potSize / 2.0)
	else:
		print("error: unknown p2Action %s" % (p2Action))

# value of hand from player 2 point of view
def valueP2Action(p1Hand, p1Action, p2Hand, p2Action, potSize):
	return -valueP1Action(p1Hand, p1Action, p2Hand, p2Action, potSize)

# expected value of player 2's action given their hand, the pot size, player 1's action, and table of player 1's action history
def E_p2Action(p2Action, p2Hand, potSize, p1Action, p1ActionCounts):
	e = 0
	counts = [p1ActionCounts[p1Hand][p1Action] for p1Hand in possible_hands]
	sumCounts = sum(counts)
	for p1Hand in possible_hands:
		e += valueP2Action(p1Hand, p1Action, p2Hand, p2Action, potSize) * counts[p1Hand] / sumCounts
	return e

# return the highest expected value action for player 2 given their hand, the pot size, player 1's action, and table of player 1's action history
def bestP2Action(p2Hand, potSize, p1Action, p1ActionCounts):
	expectedValues = [E_p2Action(p2Action, p2Hand, potSize, p1Action, p1ActionCounts) for p2Action in possible_p2Actions]
	p2Action = possible_p2Actions[expectedValues.index(max(expectedValues))]
	# maybe should randomize between all bet sizes tied for max
	return p2Action

# expected value of player 1's bet size given their hand, the pot size, and table of player 2's action history
def E_p1Action(p1Action, p1Hand, potSize, p2ActionCounts):
	e = 0
	for p2Hand in possible_hands:
		counts = {p2Action: p2ActionCounts[p2Hand][p1Action][p2Action] for p2Action in possible_p2Actions}
		sumCounts = sum(counts.values())
		for p2Action in possible_p2Actions:
			e += valueP1Action(p1Hand, p1Action, p2Hand, p2Action, potSize) * (1.0 / len(possible_hands)) * counts[p2Action] / sumCounts
	return e

# return the highest expected value action for player 1 given their hand, the pot size, and table of player 2's action history
def bestP1Action(p1Hand, potSize, p2ActionCounts):
	expectedValues = [E_p1Action(p1Action, p1Hand, potSize, p2ActionCounts) for p1Action in possible_p1Actions]
	p1Action = expectedValues.index(max(expectedValues))
	# maybe should randomize between all bet sizes tied for max
	return p1Action

# return net gain/loss for the hand for player 1
def playHand(p1ActionCounts, p2ActionCounts, shouldPrint=False):
	ante = 2
	potSize = 2 * ante
	p1Hand = randomHand() # player 1 is first to act
	p2Hand = randomHand() # player 2 is second to act
	p1Action = bestP1Action(p1Hand, potSize, p2ActionCounts)
	p2Action = bestP2Action(p2Hand, potSize, p1Action, p1ActionCounts)
	if shouldPrint:
		print("p1Hand = %d, p2Hand = %d" % (p1Hand, p2Hand))
		print("p1 bet = %d, p2Action = %s" % (p1Action, p2Action))
	value = valueP1Action(p1Hand, p1Action, p2Hand, p2Action, potSize)
	if shouldPrint:
		print("p1 hand winnings = %d" % (value))
	p1ActionCounts[p1Hand][p1Action] += 1
	p2ActionCounts[p2Hand][p1Action][p2Action] += 1
	return value

def printP1ActionCounts(p1ActionCounts):
	print("player 1 actions")
	for p1Hand in possible_hands:
		sumCounts = sum(p1ActionCounts[p1Hand])
		print("%d:" % (p1Hand), end="")
		for p1Action in possible_p1Actions:
			print(" %.2f," % (p1ActionCounts[p1Hand][p1Action] / sumCounts), end="")
		print("")

def printP2ActionCounts(p2ActionCounts):
	print("player 2 actions")
	for p2Hand in possible_hands:
		#sumCounts = sum(p1ActionCounts[p1Hand])
		print("%d:" % (p2Hand), end="")
		for p1Action in possible_p1Actions:
			foldCount = p2ActionCounts[p2Hand][p1Action]["fold"]
			callCount = p2ActionCounts[p2Hand][p1Action]["call"]
			print(" %.2f," % (callCount / (foldCount + callCount)), end="")
		print("")

def run():
	# p1ActionCounts[p1Hand][p1Action] = of all the times p1 found himself in the situation of having p1Hand, how many times did he play p1Action
	p1ActionCounts = [[0.01 for p1Action in possible_p1Actions] for p1Hand in possible_hands]
	# p2ActionCounts[p2Hand][p1Action][p2Action] = of all the times p2 found himself in the situation of having p2Hand and facing p1Action, how many times did he play p2Action
	p2ActionCounts = [[{p2Action: 0.01 for p2Action in possible_p2Actions} for p1Action in possible_p1Actions] for p2Hand in possible_hands]
	
	winnings = 0
	numHands = 5000000
	for i in range(numHands):
		shouldPrint = (i > numHands - 100)
		winnings += playHand(p1ActionCounts, p2ActionCounts, shouldPrint)
	print("numHands = %d" % (numHands))
	print("total p1 winnings = %d" % (winnings))
	print("p1 winnings per hand = %f" % (winnings / numHands))
	#print(p1ActionCounts)
	printP1ActionCounts(p1ActionCounts)
	printP2ActionCounts(p2ActionCounts)
	#print(p2ActionCounts)

run()





# In the tables below approximating the nash equilibrium, the row is always the players hand.
# In the player 1 table, the columns are the probabilities of what he chooses to bet and should sum to 1.
# In the player 2 table, the column is what the other player bet, and the value is the probability that player 2 calls.
# It looks like the tables are converging as number of hands increases.

# Sanity checks:
# The bottom row of player 2's table is all 1.00 because he should never fold the strongest hand.
# The first column of player 2's table is all 1.00 because he should never fold to a bet of 0.
# The first row of player 2's table (ignoring the first column) is all 0.00 because he should never call a nonzero bet with the weakest hand.

# Player 1's equilibrium strategy:
# Player 1 will never check hand 0, instead he will always bluff it.
# Player 1 will usually check hand 1, but sometimes bluff it.
# Player 1 will always check hands 2, 3, 4, 5, hoping to win the showdown without risking a bet.
# Player 1 will usually check hand 6, but sometimes bets a small amount for value.
# Player 1 will never check hands 7, 8, 9, and will always bet them for value.
# Player 1 bets small with hand 7, medium with hand 8, and big with hand 9.
# Player 1's big bets with hand 9 are balanced out with big bluffs with hands 0 and 1.

# Player 2's equilibrium strategy is simpler:
# Player 2 is more likely to call with a stronger hand than a weaker hand.
# Player 2 is more likely to call a smaller bet than a bigger bet.

#numHands = 10000
#total p1 winnings = 2475
#p1 winnings per hand = 0.247500
#player 1 actions
#0: 0.03, 0.21, 0.06, 0.23, 0.02, 0.00, 0.02, 0.16, 0.15, 0.10,
#1: 0.63, 0.06, 0.05, 0.09, 0.02, 0.00, 0.01, 0.06, 0.02, 0.05,
#2: 0.96, 0.00, 0.00, 0.00, 0.00, 0.01, 0.01, 0.00, 0.00, 0.01,
#3: 0.99, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#4: 0.98, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#5: 0.98, 0.00, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#6: 0.30, 0.67, 0.01, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00,
#7: 0.00, 0.72, 0.18, 0.06, 0.01, 0.00, 0.00, 0.02, 0.00, 0.00,
#8: 0.00, 0.00, 0.09, 0.65, 0.16, 0.03, 0.02, 0.03, 0.02, 0.01,
#9: 0.00, 0.00, 0.00, 0.00, 0.01, 0.02, 0.04, 0.35, 0.28, 0.30,
#player 2 actions
#0: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#1: 1.00, 0.14, 0.17, 0.06, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#2: 1.00, 0.65, 0.32, 0.24, 0.40, 0.00, 0.00, 0.02, 0.00, 0.09,
#3: 1.00, 0.71, 0.40, 0.32, 0.26, 0.38, 0.17, 0.10, 0.00, 0.16,
#4: 1.00, 0.76, 0.44, 0.44, 0.25, 0.43, 0.00, 0.17, 0.11, 0.14,
#5: 1.00, 0.83, 0.65, 0.41, 0.23, 0.33, 0.45, 0.19, 0.31, 0.23,
#6: 1.00, 1.00, 0.93, 0.61, 0.43, 0.20, 0.75, 0.33, 0.33, 0.31,
#7: 1.00, 1.00, 1.00, 1.00, 0.81, 0.60, 0.43, 0.37, 0.33, 0.29,
#8: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.82, 0.87, 0.82, 0.47,
#9: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,


#numHands = 50000
#total p1 winnings = 12366
#p1 winnings per hand = 0.247320
#player 1 actions
#0: 0.02, 0.22, 0.07, 0.26, 0.02, 0.01, 0.02, 0.12, 0.17, 0.09,
#1: 0.62, 0.07, 0.02, 0.06, 0.01, 0.01, 0.02, 0.06, 0.06, 0.08,
#2: 0.99, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#3: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#4: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#5: 0.99, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#6: 0.57, 0.42, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#7: 0.00, 0.90, 0.09, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#8: 0.00, 0.00, 0.15, 0.72, 0.07, 0.02, 0.01, 0.02, 0.01, 0.01,
#9: 0.00, 0.00, 0.00, 0.00, 0.02, 0.02, 0.05, 0.29, 0.35, 0.27,
#player 2 actions
#0: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#1: 1.00, 0.11, 0.10, 0.01, 0.03, 0.07, 0.00, 0.00, 0.00, 0.01,
#2: 1.00, 0.69, 0.41, 0.31, 0.22, 0.09, 0.23, 0.22, 0.09, 0.15,
#3: 1.00, 0.67, 0.58, 0.36, 0.33, 0.26, 0.19, 0.17, 0.11, 0.21,
#4: 1.00, 0.70, 0.47, 0.38, 0.38, 0.38, 0.14, 0.20, 0.17, 0.17,
#5: 1.00, 0.83, 0.56, 0.49, 0.31, 0.29, 0.32, 0.17, 0.23, 0.24,
#6: 1.00, 1.00, 0.64, 0.57, 0.46, 0.23, 0.38, 0.31, 0.27, 0.24,
#7: 1.00, 1.00, 1.00, 0.77, 0.64, 0.57, 0.33, 0.36, 0.39, 0.22,
#8: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.88, 0.73, 0.74, 0.43,
#9: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,


#numHands = 200000
#total p1 winnings = 47102
#p1 winnings per hand = 0.235510
#player 1 actions
#0: 0.00, 0.18, 0.05, 0.27, 0.01, 0.00, 0.01, 0.12, 0.23, 0.13,
#1: 0.68, 0.08, 0.02, 0.06, 0.00, 0.00, 0.00, 0.05, 0.04, 0.07,
#2: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#3: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#4: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#5: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#6: 0.71, 0.28, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01,
#7: 0.00, 0.92, 0.06, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#8: 0.00, 0.00, 0.18, 0.76, 0.04, 0.00, 0.00, 0.01, 0.00, 0.00,
#9: 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.02, 0.28, 0.43, 0.26,
#player 2 actions
#0: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#1: 1.00, 0.06, 0.05, 0.00, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00,
#2: 1.00, 0.70, 0.47, 0.44, 0.24, 0.07, 0.17, 0.26, 0.15, 0.12,
#3: 1.00, 0.72, 0.48, 0.40, 0.29, 0.33, 0.21, 0.26, 0.16, 0.17,
#4: 1.00, 0.75, 0.53, 0.42, 0.25, 0.26, 0.23, 0.25, 0.22, 0.16,
#5: 1.00, 0.80, 0.57, 0.44, 0.39, 0.13, 0.32, 0.25, 0.23, 0.17,
#6: 1.00, 1.00, 0.66, 0.44, 0.51, 0.44, 0.31, 0.27, 0.23, 0.27,
#7: 1.00, 1.00, 1.00, 0.69, 0.68, 0.67, 0.48, 0.33, 0.37, 0.37,
#8: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.77, 0.61, 0.53, 0.38,
#9: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,


#numHands = 1000000
#total p1 winnings = 243060
#p1 winnings per hand = 0.243060
#player 1 actions
#0: 0.00, 0.20, 0.04, 0.27, 0.00, 0.00, 0.01, 0.15, 0.24, 0.08,
#1: 0.69, 0.03, 0.02, 0.07, 0.00, 0.00, 0.01, 0.06, 0.07, 0.05,
#2: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#3: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#4: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#5: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#6: 0.87, 0.12, 0.00, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#7: 0.00, 0.96, 0.04, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#8: 0.00, 0.00, 0.16, 0.82, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00,
#9: 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.03, 0.31, 0.49, 0.17,
#player 2 actions
#0: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#1: 1.00, 0.06, 0.03, 0.00, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00,
#2: 1.00, 0.72, 0.55, 0.41, 0.26, 0.00, 0.27, 0.23, 0.14, 0.20,
#3: 1.00, 0.72, 0.57, 0.41, 0.23, 0.08, 0.24, 0.24, 0.15, 0.20,
#4: 1.00, 0.73, 0.56, 0.41, 0.26, 0.33, 0.29, 0.25, 0.15, 0.21,
#5: 1.00, 0.73, 0.57, 0.41, 0.39, 0.33, 0.26, 0.26, 0.15, 0.21,
#6: 1.00, 1.00, 0.57, 0.53, 0.43, 0.54, 0.31, 0.30, 0.29, 0.22,
#7: 1.00, 1.00, 1.00, 0.73, 0.78, 0.62, 0.33, 0.36, 0.46, 0.28,
#8: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.76, 0.55, 0.55, 0.35,
#9: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,


#numHands = 5000000
#total p1 winnings = 1245105
#p1 winnings per hand = 0.249021
#player 1 actions
#0: 0.00, 0.17, 0.02, 0.33, 0.00, 0.00, 0.00, 0.15, 0.24, 0.08,
#1: 0.72, 0.04, 0.01, 0.07, 0.00, 0.00, 0.00, 0.06, 0.06, 0.03,
#2: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#3: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#4: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#5: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#6: 0.93, 0.07, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#7: 0.00, 0.98, 0.02, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#8: 0.00, 0.00, 0.06, 0.93, 0.00, 0.00, 0.00, 0.02, 0.00, 0.00,
#9: 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.36, 0.46, 0.18,
#player 2 actions
#0: 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#1: 1.00, 0.07, 0.08, 0.00, 0.01, 0.00, 0.00, 0.00, 0.00, 0.00,
#2: 1.00, 0.71, 0.52, 0.44, 0.26, 0.10, 0.26, 0.22, 0.21, 0.18,
#3: 1.00, 0.71, 0.53, 0.43, 0.35, 0.06, 0.25, 0.22, 0.21, 0.18,
#4: 1.00, 0.71, 0.54, 0.44, 0.32, 0.10, 0.29, 0.23, 0.21, 0.18,
#5: 1.00, 0.72, 0.54, 0.43, 0.44, 0.31, 0.29, 0.23, 0.21, 0.18,
#6: 1.00, 1.00, 0.54, 0.55, 0.31, 0.73, 0.27, 0.26, 0.26, 0.20,
#7: 1.00, 1.00, 1.00, 0.70, 0.65, 0.60, 0.33, 0.33, 0.35, 0.31,
#8: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.75, 0.59, 0.40, 0.40,
#9: 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00,


