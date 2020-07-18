import requests, json, time
from flask import Flask, render_template, request, flash, url_for
from helper_functions import generate_problem_link, get_title, get_rating_category, \
                             safeHitURL, parse_problems, recommender, allProblems
  
app = Flask(__name__) 
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

INF = 10000
HOME_TEMPLATE = 'home.html'
TEAM_TEMPLATE = 'team_mode.html'


@app.route("/", methods=['POST', 'GET']) 
def home_view(): 

	start = time.process_time()
	if request.method == 'POST':

		handle = request.form['user_handle']
		url, payload, timeout = 'https://codeforces.com/api/user.status', {'handle': handle}, 10
		response_data = json.loads(safeHitURL(url=url, payload=payload, timeout=timeout, template=HOME_TEMPLATE))
		
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

			unsolved_info = parse_problems(solved_problem_set, unsolved_problem_set)

			# Fetching User Info
			url, payload, timeout = 'https://codeforces.com/api/user.info', {'handles': handle}, 10
			response_data = json.loads(safeHitURL(url=url, payload=payload, timeout=timeout, template=HOME_TEMPLATE))

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
			user_rating = user_info_full['rating'] if 'rating' in user_info_full else 0
			print(f"Time Taken before recommender = {time.process_time() - start}")
			# recommender([(handle, user_rating)], unsolved_info['final_unsolved_problem_list'], unsolved_info['final_solved_problem_list'])
			print(f"Time Taken final = {time.process_time() - start}")
			flash("Connected to Codeforces server. Scroll down to see results.", 'success')
			return render_template('home.html', status=status, user_info=user_info, unsolved_info=unsolved_info)
		else:
			comment = response_data['comment']
			flash(comment, 'danger')
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
		if len(processed_handles) > 5:
			flash("Too many handles! You can enter maximum of 5 handles.", 'warning')
			return render_template('team_mode.html')
		if len(processed_handles) < 2:
			flash("Enter atleast 2 handles. For single user go to Normal Mode!", 'warning')
			return render_template('team_mode.html')
			
		# Fetching User Info
		url, payload, timeout = 'https://codeforces.com/api/user.info', {'handles': str(';'.join(processed_handles))}, 10
		response_data = json.loads(safeHitURL(url=url, payload=payload, timeout=timeout, template=TEAM_TEMPLATE))

		status = response_data['status']

		if status == 'OK':
			team = response_data['result']
			team_info = []
			for user in team:
				team_info.append({
					'handle': user['handle'],
					'rating': user['rating'] if 'rating' in user else 0,
					'title': get_title(int(user['rating']))[0] if 'rating' in user else "Unrated",
					'color': get_title(int(user['rating']))[1] if 'rating' in user else "text-dark",
				})

			# Problem Data
			unsolved_problem_set = set([])
			solved_problem_set = set([])
			queued_problem_set = set([]) # Problems whose submission is still in queue.
			for handle in processed_handles:
				url, payload, timeout = 'https://codeforces.com/api/user.status', {'handle': handle}, 10
				response_data = json.loads(safeHitURL(url=url, payload=payload, timeout=timeout, template=TEAM_TEMPLATE))
				 
				status = response_data['status']
				
				if status == 'OK':
					submissions = response_data['result']

					# Segregating solved and unsolved problems
					for submission in submissions:
						verdict = submission['verdict'] if 'verdict' in submission else 'QUEUED'
						problem = submission['problem']
						if verdict == 'OK':
							solved_problem_set.add(json.dumps(problem))
						elif verdict == 'QUEUED':
							queued_problem_set.add(json.dumps(problem))
						else:
							unsolved_problem_set.add(json.dumps(problem))
				else:
					comment = response_data['comment']
					return render_template('team_mode.html', status=status, comment=comment)

			unsolved_info = parse_problems(solved_problem_set, unsolved_problem_set)
			flash("Connected to Codeforces server. Scroll down to see results.", 'success')
			return render_template('team_mode.html', status=status, team_info=team_info, unsolved_info=unsolved_info)
		else:
			comment = response_data['comment']
			flash(comment, 'danger')
			return render_template('team_mode.html', status=status, comment=comment)
		return render_template('team_mode.html')
	else:
		return render_template('team_mode.html') 



