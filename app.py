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


# def user_information(handles):
# 	"""
# 		Function to return relevant user information in form of dictionary.
# 	"""
# 	payload = {'handles': str(';'.join(handles))}
# 	try:
# 		r = requests.get('https://codeforces.com/api/user.info', params=payload, timeout=10)
# 	except requests.exceptions.ConnectTimeout:
# 		flash("ConnectTimeout: Could not connect to Codeforces server. Check your Internet Connection and Try Again!", 'error')
# 		return render_template('team_mode.html')
# 	except requests.exceptions.ReadTimeout:
# 		flash("ReadTimeout: Connected to Codeforces server but it took too long to respond. Try Again!", 'error')
# 		return render_template('team_mode.html')

# 	try:
# 		response_data = r.json()
# 	except json.decoder.JSONDecodeError:
# 		flash("Internal Server Error: Could not fetch data. Probably Codeforces Server is down. Try again!", 'error')
# 		return render_template('team_mode.html') 


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

		try:
			response_data = r.json()
		except json.decoder.JSONDecodeError:
			flash("Internal Server Error: Could not fetch data. Probably Codeforces Server is down. Try again!", 'error')
			return render_template('home.html') 
		status = response_data['status']

		if status == 'OK':
			"""
				Connected to Codeforces Server and got response.
			"""
			submissions = response_data['result']
			unsolved_problem_set = set([])
			solved_problem_set = set([])
			queued_problem_set = set([]) # Problems whose submission is still in queue.
			# Segregating solved and unsolved problems
			for submission in submissions:
				verdict = submission['verdict'] if 'verdict' in submission else 'QUEUED'
				problem = submission['problem']
				handle = submission['author']['members'][0]['handle']
				if verdict == 'OK':
					solved_problem_set.add(json.dumps(problem))
				elif verdict == 'QUEUED':
					queued_problem_set.add(json.dumps(problem))
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

			unsolved_info = {
				# Unsolved information to send to template.
				'total_unsolved': total_unsolved,
				'unsolved_problem_by_index': final_unsolved_by_index,
				'unsolved_problem_by_rating': final_unsolved_by_rating,
			}

			# Fetching User Info
			try:
				r = requests.get('https://codeforces.com/api/user.info', params={'handles': handle}, timeout=10)
			except requests.exceptions.ConnectTimeout:
				flash("ConnectTimeout: Could not connect to Codeforces server. Check your Internet Connection and Try Again!", 'error')
				return render_template('home.html') 
			except requests.exceptions.ReadTimeout:
				flash("ReadTimeout: Connected to Codeforces server but it took too long to respond. Try Again!", 'error')
				return render_template('home.html') 

			try:
				response_data = r.json()
			except json.decoder.JSONDecodeError:
				flash("Internal Server Error: Could not fetch data. Probably Codeforces Server is down. Try again!", 'error')
				return render_template('home.html') 
			user_info_full = response_data['result'][0]
			user_info = {
				# User information to send to template.
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
			return render_template('home.html', status=status, user_info=user_info, unsolved_info=unsolved_info)
		else:
			comment = response_data['comment']
			return render_template('home.html', status=status, comment=comment)
	else:
		return render_template('home.html') 



@app.route("/team_mode/", methods=['POST', 'GET']) 
def team_mode(): 
	if request.method == 'POST':
		handles = str(request.form['team_user_handles']).split(',')
		if len(handles) > 5:
			flash("Too many handles! You can enter maximum of 5 handles.", 'warning')
			return render_template('team_mode.html')
		print(handles)
		processed_handles = []
		for handle in handles:
			handle = str(handle).strip()
			if handle:
				processed_handles.append(handle)
		if len(handles) > 5:
			flash("Too many handles! You can enter maximum of 5 handles.", 'warning')
			return render_template('team_mode.html')
		payload = {'handles': str(';'.join(processed_handles))}
		print(processed_handles)
		# Fetching User Info
		try:
			r = requests.get('https://codeforces.com/api/user.info', params=payload, timeout=10)
		except requests.exceptions.ConnectTimeout:
			flash("ConnectTimeout: Could not connect to Codeforces server. Check your Internet Connection and Try Again!", 'error')
			return render_template('team_mode.html')
		except requests.exceptions.ReadTimeout:
			flash("ReadTimeout: Connected to Codeforces server but it took too long to respond. Try Again!", 'error')
			return render_template('team_mode.html')

		try:
			response_data = r.json()
		except json.decoder.JSONDecodeError:
			flash("Internal Server Error: Could not fetch data. Probably Codeforces Server is down. Try again!", 'error')
			return render_template('team_mode.html') 
		# print(response_data)
		status = response_data['status']

		if status == 'OK':
			team = response_data['result']
			team_info = []
			for user in team:
				team_info.append({
					'handle': user['handle'],
					# 'first_name': user['firstName'] if 'firstName' in user else "",
					# 'last_name': user['lastName'] if 'lastName' in user else "",
					'rating': user['rating'] if 'rating' in user else 0,
					'title': get_title(int(user['rating']))[0] if 'rating' in user else "Unrated",
					'color': get_title(int(user['rating']))[1] if 'rating' in user else "text-dark",
					# 'max_rating': user['maxRating'] if 'maxRating' in user else 0,
					# 'max_title': get_title(int(user['maxRating']))[0] if 'maxRating' in user else "Unrated",
					# 'max_color': get_title(int(user['maxRating']))[1] if 'maxRating' in user else "text-dark",
					# 'organization': user['organization'] if 'organization' in user else "",
				})
			print(team_info)
			flash('Connected to Codeforces Server.', 'success')
			return render_template('team_mode.html', status=status, team_info=team_info)
		else:
			comment = response_data['comment']
			flash(comment, 'error')
			return render_template('team_mode.html', status=status, comment=comment)
		return render_template('team_mode.html')
	else:
		return render_template('team_mode.html') 