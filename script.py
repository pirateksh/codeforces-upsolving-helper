import requests, json
handle = input("Enter user handle: ")
payload = {'handle': handle}
print("Connecting to Codeforces API...")
try:
	r = requests.get('https://codeforces.com/api/user.status', params=payload)
	print("Connected to Codeforces server.")
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
				link = f"(https://codeforces.com/contest/{contestId}/problem/{index})"
			else:
				link = f"(https://codeforces.com/problemset/gymProblem/{contestId}/{index})"
			chunk = str(1 + len(unsolved_problem_by_index[letter])) + ": "
			chunk += index + ". "
			chunk += name + " "
			chunk += link + "\n"
			unsolved_problem_by_index[letter].append(chunk)

		filename = "unsolved.txt"
		with open(filename, 'w') as fd:
			fd.write("Thankyou for using 'Codeforces Upsolving Helper', written by 'pirateksh' (https://github.com/pirateksh). Good Luck and High Rating!\n\n")
			fd.write(f"User Handle: {handle} | Total Attempted (atleast once) but Unsolved: {total_unsolved}\n\n");
			for index in unsolved_problem_by_index:
				if len(unsolved_problem_by_index[index]) > 0:
					fd.write(f"{index}\n")
					for problem in unsolved_problem_by_index[index]:
						fd.write(problem)
					fd.write("\n")
		print("Unsolved Problems have been identified. Check 'unsolved.txt' file.")
	else:
		comment = response_data['comment']
		print("Invalid Request")
		print(comment)
except:
	print("ERROR: An Exception occured. Try Again.")