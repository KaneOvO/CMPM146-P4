import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method (name, rule):
	def method (state, ID):
		# your code here
		#pass
		method = []
		#add requires
		if ('Requires' in rule):
			for require in rule['Requires']:
				method.append(('have_enough', ID, require, rule['Requires'][require]))
		#add consumes
		if ('Consumes' in rule):
			for consume in rule['Consumes']:
				method.append(('have_enough', ID, consume, rule['Consumes'][consume]))
		#add produces
		method.append("op_" + name, ID)
		return method
	#change method name
	method.__name__ = name	
	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	#pass

	produces = {}

	for recipe in data['Recipes']:
		#change name
		newName = recipe.replace(' ', '_')
		#make method
		method = make_method(newName, data['Recipes'][recipe])
		#define produce
		produce = list(data['Recipes'][recipe]["Produces"].keys())

		#check if produce is in produces dic
		if produce not in produces:
			produces[produce] = []
		#add method to produces
		produces[produce].append(method)
		#sort by time
		produces[produce].sort(key=lambda p: data["Recipes"][p.__name__]["Time"])

	for produce in produces:
		pyhop.declare_methods(str("produce_" + produce), *produces[produce])

		

				

def make_operator (rule):
	
	def operator (state, ID):
		# your code here

		#constrant time
		#check if there is enought time left if not then return F
		if state.time[ID] < rule["Time"]:
			return False

		#if there another constrant from requires
		if "Requires" in rule:
			#get required item
			required_item=str(*rule["requires"])
			#check for required item
			#if not enough of the required item return False
			if state.required_item[ID] < rule["requires"][required_item]:
				return False

		#check for enough of consumed items
		if "Consumes" in rule:
			#loop through consumes dictionary
			for consumed in rule["Consumes"]:
				#check each key and if there isnt enough then return false
				if state.consumed[ID] < rule["Consumes"][consumed]:
					return False

		# everything is set so now 
	
		# product is added
		
		#find product
		item_produced=str(*rule["Produces"])
		#add it
		state.item_produced[ID] += rule["Produces"][item_produced]

		# consumed items are subtracted 

		if "Consumes" in rule:
			#loop through consumes dictionary
			for consumed in rule["Consumes"]:
				state.consumed[ID] -= rule["Consumes"][consumed]

		# time is subtracted

		state.time[ID] -= rule["Time"]


		return state



	return operator

def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)

	#go through recipes in data
	for recipe in data['Recipes']:

		#pass a dictionary into make_operator
		new_function=make_operator(data['Recipes'][recipe])

		# new operator funtion is renamed 
		new_function.__name__= "op_"+recipe.replace(" ", "_")

		# declare new function
		pyhop.declare_operators(new_function)



def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		# your code here










		return False # if True, prune this branch

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=239) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	# pyhop.print_operators()
	# pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=3)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)
