from flask import Flask, render_template, request, flash, url_for
import requests, json
  
app = Flask(__name__) 
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

INF = 10000


def generate_problem_link(problemset_name ,contestId, index):
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


@app.route("/", methods=['POST', 'GET']) 
def home_view(): 

	if request.method == 'POST':

		handle = request.form['user_handle']

		try:
			r = requests.get('https://codeforces.com/api/user.status', params={'handle': handle}, timeout=10)
		except requests.exceptions.ConnectTimeout:
			flash("ConnectTimeout: Could not connect to Codeforces server. Check your Internet Connection and Try Again!", 'error')
			return render_template('home.html') 
		except requests.exceptions.ReadTimeout:
			flash("ReadTimeout: Connected to Codeforces server but it took too long to respond. Try Again!", 'error')
			return render_template('home.html') 

		response_data = r.json()
		status = response_data['status']

		if status == 'OK':

			submissions = response_data['result']
			counter = 1
			unsolved_problem_set = set([])
			solved_problem_set = set([])

			# Segregating solved and unsolved problems
			for submission in submissions:
				verdict = submission['verdict']
				problem = submission['problem']
				handle = submission['author']['members'][0]['handle']
				if verdict == 'OK':
					solved_problem_set.add(json.dumps(problem))
				else:
					unsolved_problem_set.add(json.dumps(problem))

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

			# Segregating unsolved problems by levels
			unsolved_problem_by_index = {'A':[], 'B':[], 'C':[], 'D':[], 'E':[], 'F':[],'G':[], 'H':[], 'I':[], 'J':[], 'K':[], 'L':[], 'M':[], 'N':[], 'O':[], 'P':[], 'R':[], 'S':[], 'T':[], 'U':[], 'V':[], 'W':[], 'X':[], 'Y':[], 'Z':[], '#':[]}
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
					if letter in unsolved_problem_by_index:
						unsolved_problem_by_index[letter].append([index, name, link, rating])
					else:
						unsolved_problem_by_index['#'].append([index, name, link, rating])

			# Creating final dictionary to pass to template
			final_dict = {}
			for index in unsolved_problem_by_index:
				if len(unsolved_problem_by_index[index]) > 0:
					unsolved_problem_by_index[index] = sorted(unsolved_problem_by_index[index], key = lambda rating: rating[3])
					final_dict.update({index: unsolved_problem_by_index[index]})

			# Fetching User Info
			try:
				r = requests.get('https://codeforces.com/api/user.info', params={'handles': handle}, timeout=10)
			except requests.exceptions.ConnectTimeout:
				flash("ConnectTimeout: Could not connect to Codeforces server. Check your Internet Connection and Try Again!", 'error')
				return render_template('home.html') 
			except requests.exceptions.ReadTimeout:
				flash("ReadTimeout: Connected to Codeforces server but it took too long to respond. Try Again!", 'error')
				return render_template('home.html') 

			response_data = r.json()
			user_info_full = response_data['result'][0]
			user_info = {
				'handle': handle,
				'first_name': user_info_full['firstName'] if 'firstName' in user_info_full else "",
				'last_name': user_info_full['lastName'] if 'lastName' in user_info_full else "",
				'rating': user_info_full['rating'] if 'rating' in user_info_full else 0,
				'title': get_title(int(user_info_full['rating']))[0] if 'rating' in user_info_full else "Unrated",
				'color': get_title(int(user_info_full['rating']))[1] if 'rating' in user_info_full else "text-dark",
				'max_rating': user_info_full['maxRating'] if 'maxRating' in user_info_full else 0,
				'max_title': get_title(int(user_info_full['maxRating']))[0] if 'maxRating' in user_info_full else "Unrated",
				'max_color': get_title(int(user_info_full['maxRating']))[1] if 'maxRating' in user_info_full else "text-dark",
				'organization': user_info_full['organization'] if 'organization' in user_info_full else "",
			}
			flash("Connected to Codeforces server. Scroll down to see results.", 'success')
			return render_template('home.html', status=status, user_info=user_info, total_unsolved=total_unsolved, final_dict=final_dict)
		else:
			comment = response_data['comment']
			return render_template('home.html', status=status, comment=comment)
	else:
		return render_template('home.html') 
