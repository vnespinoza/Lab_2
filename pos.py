#Build a bigram POS tagger using Viterbi algorithm

import pickle, math

def logP(prob):
	if prob == 0:
		return -1e+100 #'huge big negative number'
	else:
		return math.log(prob)

#1. Write a function that builds a trellis for an input sentence 
#the input is sentence needing to be tagged, output is trellis with deltas and breadcrumbs from left to write

#(3) dict keys = states, values = (deltas, crumb)
def build_trellis(words, tp, ep):
	trellis = [] #(1)Define trellis as list
		#words is a list of words from a single sentence
		#words is padded: beginning with <s> and ending with </s>
		#1. very first column {'<s>':(0.0, None)}
	trellis.append({'<s>':(0.0, None)}) #First column of dictionary created (each colum of trellis is a dict)
		#2. Create a dictionary corresponding to the next column in the sequence and add that to the list
	for i in range (1, len(words)):
		#create a dictionary matching the column 
		#(1) identify the states that'll show up in the column
		#(1-1) The states to access in the current column must be worth accessing(eg. can be reached
		#from prev column) There exists a previous state q that tp[q][state] > 0
		state_list = []
		reachables = []# states that can be reached
		for prev_state in trellis[-1]: #points to previous columns(e.g. dict of states in column)
			#cur_reachables = tp[prev_state].keys() (can use this code if keys tp always > 0)
			#Prev state points to a dictionary containing keys that can be reached.
			for destination in tp[prev_state]:
				if tp[prev_state][destination] > 0:
					reachables.append(destination)
		#(1-2) States must also generate the current word output  (ep[state][words[i]] > 0)
		for state in reachables: 
			current_word = words[i]
			#if ep[state][current_word] > 0: #creates an issue when that current word does 
			#not exist in the list
			if ep[state].get(current_word, 0.0) > 0: #get and append word iff tp > 0
				state_list.append(state)
		#(2) for each state, calculate the delta and the crumb
		d= {} #dict containing {'state': (delta, crumb)}
		for state in state_list:
			#calculate delta
			#(1) iterate over states in prev column
			prev_column =trellis[-1] #point to prev column
			best_score_sofar = -1e+100
			best_prev_state_sofar = None
			for prev_state in prev_column: 
				#Calculate score from prev state
				# (log-)delta from prev state
				score = prev_column[prev_state][0]
				# log(tp(prev_state -> state))
				score += logP(tp[prev_state].get(state, 0.0))
				# log(ep(state -> words[i]))
				score += logP(ep[state].get(words[i], 0.0))		#Compare score with best_score_sofar
				if score > best_score_sofar:
					best_score_sofar = score #delta
					best_prev_state_sofar = prev_state #crumb
			d[state] = (best_score_sofar, best_prev_state_sofar) #put state:(delta,crumb) in d, i.e. d[state] = delta, crumb
		trellis.append(d)#add it to the list
	#print trellis	
	return trellis #list of dictionaries

#2. Write a function that traces back along the trellis to find the best path 
#from right to left by looking at bread crumbs
def backtrace(trellis):
	best_path = ['</s>']
	for i in range(len(trellis)-1, 0, -1):
		crumb = trellis[i][best_path[-1]][1]
		best_path.append(crumb)
	best_path.reverse()
	return best_path

#1 & 2 combined implements Viterbi Alg

#3. Interpret the best path as pos tsg sequence for the input at compare that with the correct answer
if __name__ == '__main__': 
	a = pickle.load(open('A.pickle')) #transitional probalilies 
	#a is dict whose keys are prev states which link to another dictionary carrying destination states 
	#(nested dictionary)
	#a[prev-state][next-state] = prob of prev-state -> next-state
	b = pickle.load(open('B.pickle')) # emission probabilities
	# b[state][output] = prob of generating output from state
	num_correct = 0.0
	num_total = 0.0
	f = open('brown.test.answers')
	for line in f:
		wtl = line.split() #split by wtspc
		words = []
		answer_tags = []
		for wt in wtl: #word type, word type list
			w, t = wt.split('_#_')
			words.append(w)
			answer_tags.append(t)
		words = ['<s>'] + words + ['</s>']
		t = build_trellis(words, a, b)
		best_path = backtrace(t)
		predicted_tags = best_path[1:-1]
		for i in range(len(answer_tags)):
			if answer_tags[i] == predicted_tags[i]:
				num_correct += 1
			num_total += 1
	f.close()
	print num_correct / num_total
			
