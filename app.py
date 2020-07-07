from flask import Flask, render_template, request
import requests, json
  
app = Flask(__name__) 
  
@app.route("/", methods=['POST', 'GET']) 
def home_view(): 
	if request.method == 'POST':
		handle = request.form['user_handle']
		print("User handle is:" + str(handle))
		payload = {'handle': handle}
		print("Connecting to Codeforces API...")
		r = requests.get('https://codeforces.com/api/user.status', params=payload)
		print("Connected to Codeforces server.")
		response_data = r.json()
		status = response_data['status']
		if status == 'OK':
			print("Status is OK")
			submissions = response_data['result']
			counter = 1
			unsolved_problem_set = set([])
			solved_problem_set = set([])
			for submission in submissions:
				verdict = submission['verdict']
				problem = submission['problem']
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
				if len(contestId) <= 4:
					link = f"<a href=\"https://codeforces.com/contest/{contestId}/problem/{index}\">{name}</a>"
				else:
					link = f"<a href=\"https://codeforces.com/problemset/gymProblem/{contestId}/{index})\">{name}</a>"
				chunk = f": {index}. {link}\n"
				unsolved_problem_by_index[letter].append(chunk)
			final_dict = {}
			for index in unsolved_problem_by_index:
				if len(unsolved_problem_by_index[index]) > 0:
					final_dict.update({index: unsolved_problem_by_index[index]})

			print("Unsolved Problems have been identified. Check 'unsolved.txt' file.")
			print(final_dict)
			print("Status:" + str(status))
			return render_template('home.html', status=status, total_unsolved=total_unsolved, final_dict=final_dict)
		else:
			comment = response_data['comment']
			print("Invalid Request")
			print(comment)
			return render_template('home.html', status=status, comment=comment)
	else:
		print("This is Get")
		return render_template('home.html') 
