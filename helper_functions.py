import requests, json, time, math
from problems import PROBLEM_RESPONSE

INF = 10000
HOME_TEMPLATE = 'home.html'
TEAM_TEMPLATE = 'team_mode.html'

def generate_problem_link(problemset_name, contestId, index):
	"""
		Function to generate problem link using contestID and index.
	"""
	if problemset_name:
		return f"https://codeforces.com/problemsets/{problemset_name}/problem/99999/{index}"
	if contestId == -1:
		return "#"
	if len(contestId) <= 4:
		return f"https://codeforces.com/contest/{contestId}/problem/{index}"
	return f"https://codeforces.com/problemset/gymProblem/{contestId}/{index}"


def get_title(rating):
	"""
		Function that returns [user's title, title's color] based on user's rating.
	"""
	title = ""
	if rating < 1200:
		title = ["Newbie", "grey-text"]
	elif rating < 1400:
		title = ["Pupil", "light-green-text"]
	elif rating < 1600:
		title = ["Specialist", "cyan-text"]
	elif rating < 1900:
		title = ["Expert", "indigo-text"]
	elif rating < 2100:
		title = ["Candidate Master", "purple-text"]
	elif rating < 2300:
		title = ["Master", "amber-text"]
	elif rating < 2400:
		title = ["International Master", "orange-text"]
	elif rating < 2600:
		title = ["Grandmaster", "red-text"]
	elif rating < 3000:
		title = ["International Grandmaster", "red-text"]
	else:
		title = ["Legendary Grandmaster", "red-text"]
	return title


def get_rating_category(rating):
	category = ''
	if rating < 1000:
		category = '1'
	elif rating < 1300:
		category = '2'
	elif rating < 1500:
		category = '3'
	elif rating < 1700:
		category = '4'
	elif rating < 2000:
		category = '5'
	elif rating < 2300:
		category = '6'
	elif rating < 2500:
		category = '7'
	elif rating < 2700:
		category = '8'
	elif rating < 3000:
		category = '9'
	elif rating < 3300:
		category = '10'
	elif rating < 3500:
		category = '11'
	else:
		category = '12'
	return category


def safeHitURL(url, payload={}, timeout=10, template=HOME_TEMPLATE):
	"""
		Function to safely HIT an API with all exceptions being handled.
	"""
	try:
		r = requests.get(url, params=payload, timeout=timeout)
		try:
			response_data = r.json()
			return json.dumps(response_data)
		except json.decoder.JSONDecodeError:
			flash("Internal Server Error: Could not fetch data. Probably Codeforces Server is down. Try again!", 'danger')
			return render_template(template) 
	except requests.exceptions.ConnectTimeout:
		flash("ConnectTimeout: Could not connect to Codeforces server. Check your Internet Connection and Try Again!", 'danger')
		return render_template(template) 
	except requests.exceptions.ReadTimeout:
		flash("ReadTimeout: Connected to Codeforces server but it took too long to respond. Try Again!", 'danger')
		return render_template(template) 
	except requests.exceptions.ConnectionError:
		flash("ConnectionError: Could not connect to Codeforces server. Check your Internet Connection and Try Again!", 'danger')
		return render_template(template)


# def user_information(handles):
# 	"""
# 		Function to return relevant user information in form of dictionary.
# 	"""


def parse_problems(solved_problem_set, unsolved_problem_set):
	# Further segregating dummy unsolved problems
	for problem in solved_problem_set:
		if problem in unsolved_problem_set:
			unsolved_problem_set.remove(problem)

	unsolved_problem_list = []
	for problem in unsolved_problem_set:
		unsolved_problem_list += [json.loads(problem)]

	solved_problem_list = []
	for problem in solved_problem_set:
		solved_problem_list += [json.loads(problem)]

	"""
		Further Segregation of dummy unsolved problems:
		Checking for same problem which appears in parallel Div. 1 and Div. 2
		contest with different contestId.
	"""
	dummy_unsolved_problem_list = []
	for unsolved_problem in unsolved_problem_list:
		for solved_problem in solved_problem_list:
			if solved_problem['name'] == unsolved_problem['name']:
				solved_contest_id = solved_problem['contestId'] if 'contestId' in solved_problem else -1
				unsolved_contest_id = unsolved_problem['contestId'] if 'contestId' in unsolved_problem else -1

				if unsolved_contest_id != -1 and (unsolved_contest_id + 1 == solved_contest_id or unsolved_contest_id - 1 == solved_contest_id):
					# This problem appeared in both Div. 1 and Div. 2 rounds and has been solved in one of them
					dummy_unsolved_problem_list.append(unsolved_problem)

	# Calculating total unsolved problems
	total_unsolved = len(unsolved_problem_list) - len(dummy_unsolved_problem_list)

	# Final Solved and Unsolved Problems List
	final_unsolved_problem_list = []
	final_solved_problem_list = solved_problem_list
	for problem in unsolved_problem_list:
		if problem not in dummy_unsolved_problem_list:
			final_unsolved_problem_list.append(problem)

	# Segregating unsolved problems by levels
	unsolved_problem_by_index = {'A':{'r':[], 'u':[]}, 'B':{'r':[], 'u':[]}, 'C':{'r':[], 'u':[]}, 'D':{'r':[], 'u':[]}, 'E':{'r':[], 'u':[]}, 'F':{'r':[], 'u':[]},'G':{'r':[], 'u':[]}, 'H':{'r':[], 'u':[]}, 'I':{'r':[], 'u':[]}, 'J':{'r':[], 'u':[]}, 'K':{'r':[], 'u':[]}, 'L':{'r':[], 'u':[]}, 'M':{'r':[], 'u':[]}, 'N':{'r':[], 'u':[]}, 'O':{'r':[], 'u':[]}, 'P':{'r':[], 'u':[]}, 'R':{'r':[], 'u':[]}, 'S':{'r':[], 'u':[]}, 'T':{'r':[], 'u':[]}, 'U':{'r':[], 'u':[]}, 'V':{'r':[], 'u':[]}, 'W':{'r':[], 'u':[]}, 'X':{'r':[], 'u':[]}, 'Y':{'r':[], 'u':[]}, 'Z':{'r':[], 'u':[]}, '#':{'r':[], 'u':[]}}
	unsolved_problem_by_rating = {'1':[], '2':[], '3':[], '4':[], '5':[], '6':[], '7':[], '8':[], '9':[], '10':[], '11':[], '12':[], '13':[]}
	for problem in unsolved_problem_list:
		if problem not in dummy_unsolved_problem_list:
			# Checking if it is not a dummy unsolved problem.
			contestId = str(problem['contestId']) if 'contestId' in problem else -1
			problemset_name = problem['problemsetName'] if 'problemsetName' in problem else ""
			index = str(problem['index'])
			letter = index[0]
			if not letter.isalpha():
				letter = chr(int(index) + 64)
			name = str(problem['name'])
			rating = problem['rating'] if 'rating' in problem else INF
			link = generate_problem_link(problemset_name, contestId, index)
			if letter not in unsolved_problem_by_index:
				letter = '#'
			if rating == INF:  # Unrated Problem
				unsolved_problem_by_index[letter]['u'].append([index, name, link, rating])
			else:  # Rated Problem
				unsolved_problem_by_index[letter]['r'].append([index, name, link, rating])

			rating_category = get_rating_category(int(rating)) if 'rating' in problem else '13'
			unsolved_problem_by_rating[rating_category].append([index, name, link, rating])
	
	# Creating final dictionary to pass to template
	final_unsolved_by_index = {}
	for index in unsolved_problem_by_index:
		if len(unsolved_problem_by_index[index]['r']) + len(unsolved_problem_by_index[index]['u']) > 0:
			if len(unsolved_problem_by_index[index]['r']) > 0:
				unsolved_problem_by_index[index]['r'] = sorted(unsolved_problem_by_index[index]['r'], key = lambda rating: rating[3])
			final_unsolved_by_index.update({index: unsolved_problem_by_index[index]})
	final_unsolved_by_rating = {}
	for rating_category in unsolved_problem_by_rating:
		if len(unsolved_problem_by_rating[rating_category]) > 0:
			unsolved_problem_by_rating[rating_category] = sorted(unsolved_problem_by_rating[rating_category], key = lambda rating: rating[3])
			final_unsolved_by_rating.update({rating_category: unsolved_problem_by_rating[rating_category]})

	return {
		'total_unsolved': total_unsolved, 
		'unsolved_problem_by_index': final_unsolved_by_index, 
		'unsolved_problem_by_rating': final_unsolved_by_rating,
		'final_unsolved_problem_list': final_unsolved_problem_list,
		'final_solved_problem_list': final_solved_problem_list,
	}


def recommender(users, unsolved_problem_list, solved_problem_list):
	"""
		params
		@handles: List of user handles.
	"""
	contest_set = set()
	avg_user_rating = 0
	avg_solved_problem_rating = 0
	solved_problem_with_rating_count = 0
	solved_contest_dict = {}
	unsolved_contest_dict = {}
	attempted_contest_dict = {} # Attempted but unsolved
	for user in users:
		handle = user[0]
		rating = user[1]
		max_rating = user[2]
		avg_user_rating += 0.7 * rating + 0.3 * max_rating
		url, payload, timeout = 'https://codeforces.com/api/user.rating', {'handle': handle}, 10
		response_data = json.loads(safeHitURL(url=url, payload=payload, timeout=timeout, template=HOME_TEMPLATE))
		status = response_data['status']

		if status == 'OK':
			rating_changes = response_data['result']
			for rating_change in rating_changes:
				contestId = rating_change['contestId']
				if contestId not in solved_contest_dict:
					solved_contest_dict.update({int(contestId): []})
					unsolved_contest_dict.update({int(contestId): []})
					attempted_contest_dict.update({int(contestId): []})
				contest_set.add(int(contestId))
		else:
			comment = response_data['comment']
			flash(comment, 'danger')
			return render_template('home.html', status=status, comment=comment)

	avg_user_rating /= len(users)

	contest_set = sorted(contest_set)

	for solved_problem in solved_problem_list:
		if 'contestId' in solved_problem:
			contestId = solved_problem['contestId']
			if int(contestId) in solved_contest_dict:
				solved_contest_dict[int(contestId)].append(solved_problem)

		# Calculating Average Solved Problem Rating
		if 'rating' in solved_problem:
			rating = int(solved_problem['rating'])
			avg_solved_problem_rating += rating
			solved_problem_with_rating_count += 1

	avg_solved_problem_rating /= solved_problem_with_rating_count

	final_rating = math.ceil(0.8 * avg_user_rating + 0.2 * avg_solved_problem_rating)
	print(f"User Rating = {avg_user_rating} Solved Rating = {avg_solved_problem_rating}")
	print(f"Final Rating = {final_rating}")

	for unsolved_problem in unsolved_problem_list:
		if 'contestId' in unsolved_problem:
			contestId = unsolved_problem['contestId']
			if int(contestId) in attempted_contest_dict:
				attempted_contest_dict[int(contestId)].append(unsolved_problem)
	
	# problems_dict = json.loads(allProblems())
	# all_problems = problems_dict['problems']
	# problems_statistics = problems_dict['problemStatistics']
	all_problems = PROBLEM_RESPONSE['problems']
	problems_statistics = PROBLEM_RESPONSE['problemStatistics']

	# for problem, stats in zip(all_problems, problems_statistics):
	for problem in all_problems:
		if 'contestId' in problem:
			contestId = problem['contestId']
			# solvedCount = stats['solvedCount']

			# This chnges the dictioanry itself
			# if 'rating' in problem:
			# 	problem['rating'] = solvedCount
			# else:
			# 	problem.update({'rating': solvedCount})
			if int(contestId) in solved_contest_dict:
				if problem not in solved_contest_dict[int(contestId)]:
					if problem not in attempted_contest_dict[int(contestId)]:
						unsolved_contest_dict[int(contestId)].append(problem)

	# recommended_problems = {'0':[], '1':[], '2':[], '3':[], '4':[], '5':[], '6':[], '7':[]}
	recommended_problems = {'1':[], '2':[], '3':[], '4':[], '5':[], '6':[]}
	for contestId in unsolved_contest_dict:
		# unsolved_contest_dict[contestId] = sorted(unsolved_contest_dict[contestId], key = lambda prblm: prblm['rating'])
		for problem in unsolved_contest_dict[contestId]:
			if 'rating' in problem:
				category = recommender_category(final_rating, int(problem['rating']))
			else:
				category = '6'
			contestId = str(problem['contestId']) if 'contestId' in problem else -1
			problemset_name = problem['problemsetName'] if 'problemsetName' in problem else ""
			index = str(problem['index'])
			name = str(problem['name'])
			rating = problem['rating'] if 'rating' in problem else INF
			link = generate_problem_link(problemset_name, contestId, index)
			if len(recommended_problems[category]) < 10:
				recommended_problems[category].append([index, name, link, rating])
	
	for category in recommended_problems:
		recommended_problems[category] = sorted(recommended_problems[category], key = lambda prblm: prblm[3])
	for category in recommended_problems:
		if len(recommended_problems[category]) > 0:
			if category == '1':
				print(f"Level Easy:")
			elif category == '2':
				print(f"Level Medium:")
			elif category == '3':
				print(f"Level Hard:")
			elif category == '4':
				print(f"Level Extreme:")
			elif category == '5':
				print(f"Level Impossible:")
			else: 
				print(f"Level Unrated:")
			
			for problems in recommended_problems[category]:
				print(f"\t{problems[0]}. {problems[1]} ({problems[2]}) ({problems[3]})")

def recommender_category(user_rating, problem_rating):
	category = ''
	# if problem_rating >= 30000:
	# 	category = '0'
	# if problem_rating >= 10000:
	# 	category = '1'
	# elif problem_rating >= 7000:
	# 	category = '2'
	# elif problem_rating >= 4500:
	# 	category = '3'
	# elif problem_rating >= 2000:
	# 	category = '4'
	# elif problem_rating >= 1000:
	# 	category = '5'
	# elif problem_rating >= 300:
	# 	category = '6'
	# elif problem_rating >= 10:
	# 	category = '7'
	if user_rating >= 2000:
		if problem_rating <= user_rating - 300:
			category = '1'
		elif problem_rating <= user_rating + 200:
			category = '2'
		elif problem_rating <= user_rating + 400:
			category = '3'
		elif problem_rating <= user_rating + 700:
			category = '4'
		else:
			category = '5'
	else:
		if problem_rating <= user_rating - 100:
			category = '1'
		elif problem_rating <= user_rating + 200:
			category = '2'
		elif problem_rating <= user_rating + 400:
			category = '3'
		elif problem_rating <= user_rating + 600:
			category = '4'
		else:
			category = '5'
	return category

def allProblems():
	pass
# 	url = 'https://codeforces.com/api/problemset.problems'
# 	response_data = json.loads(safeHitURL(url=url))
# 	status = response_data['status']
# 	if status == 'OK':
# 		return json.dumps(response_data['result'])
# 	else:
# 		comment = response_data['comment']
# 		flash(comment, 'danger')
# 		return render_template('home.html', status=status, comment=comment)