from flask import Flask, render_template, request, flash
import requests, json
  
app = Flask(__name__) 
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def generate_problem_link(contestId, index):
	if len(contestId) <= 4:
		return f"https://codeforces.com/contest/{contestId}/problem/{index}"
	return f"https://codeforces.com/problemset/gymProblem/{contestId}/{index}"

@app.route("/", methods=['POST', 'GET']) 
def home_view(): 
	if request.method == 'POST':
		handle = request.form['user_handle']
		print("User handle is:" + str(handle))
		payload = {'handle': handle}
		# flash("Connecting to Codeforces API...")
		r = requests.get('https://codeforces.com/api/user.status', params=payload)
		flash("Connected to Codeforces server.")
		response_data = r.json()
		status = response_data['status']
		if status == 'OK':
			submissions = response_data['result']
			counter = 1
			unsolved_problem_set = set([])
			solved_problem_set = set([])
			for submission in submissions:
				verdict = submission['verdict']
				problem = submission['problem']
				handle = submission['author']['members'][0]['handle']
				if verdict == 'OK':
					solved_problem_set.add(json.dumps(problem))
				else:
					unsolved_problem_set.add(json.dumps(problem))
			for problem in solved_problem_set:
				if problem in unsolved_problem_set:
					unsolved_problem_set.remove(problem)
			unsolved_problem_list = []
			for problem in unsolved_problem_set:
				unsolved_problem_list += [json.loads(problem)]
			total_unsolved = len(unsolved_problem_list)
			unsolved_problem_list = sorted(unsolved_problem_list, key = lambda problem: problem['contestId'], reverse=True)
			unsolved_problem_by_index = {'A':[], 'B':[], 'C':[], 'D':[], 'E':[], 'F':[],'G':[], 'H':[], 'I':[], 'J':[], 'K':[], 'L':[], 'M':[], 'N':[], 'O':[], 'P':[], 'R':[], 'S':[], 'T':[], 'U':[], 'V':[], 'W':[], 'X':[], 'Y':[], 'Z':[]}
			for problem in unsolved_problem_list:
				contestId = str(problem['contestId'])
				index = str(problem['index'])
				letter = index[0]
				name = str(problem['name'])
				link = generate_problem_link(contestId, index)
				unsolved_problem_by_index[letter].append([index, name, link])
			final_dict = {}
			for index in unsolved_problem_by_index:
				if len(unsolved_problem_by_index[index]) > 0:
					final_dict.update({index: unsolved_problem_by_index[index]})
			return render_template('home.html', status=status, handle=handle, total_unsolved=total_unsolved, final_dict=final_dict)
		else:
			comment = response_data['comment']
			return render_template('home.html', status=status, comment=comment)
	else:
		return render_template('home.html') 
