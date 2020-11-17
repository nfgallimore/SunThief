import time, sched, json, requests, os, datetime

def post():
	auth = {'Authorization': os.environ["SUN_THIEF_TOKEN"]}

	wcb = requests.get(f'{os.environ["SUN_THIEF_FROM_CHANNEL"]}?limit=10', headers=auth).json()
	versus = requests.get(f'{os.environ["SUN_THIEF_TO_CHANNEL"]}', headers=auth).json()

	# format posts to similar way and check if we've already posted it
	wcb_posts = list(map(lambda x: f'{x["id"]}\n', wcb))
	new_posts = list(set(wcb_posts) - set(history))[::-1]

	print(history)
	print(wcb_posts)
	print(new_posts)

	for i in new_posts:
		post = wcb[new_posts.index(i)]
		send_name(post)
		send_post(post)

	return len(new_posts)

def send_name(p):
	formatted_name = format_name(p)
	resp = requests.post(
		os.environ["SUN_THIEF_WEBHOOK"], 
		headers={'Content-Type':'application/x-www-form-urlencoded'}, 
		data={'content': formatted_name})
	
	# if unauthorized get a new token and post again
	if resp.status_code == 401:
		refresh_token()
		resp = requests.post(
			os.environ["SUN_THIEF_WEBHOOK"], 
			headers={'Content-Type':'application/x-www-form-urlencoded'}, 
			data={'content': formatted_name})

	# retry request after certain time if 429
	if resp.status_code == 429:
		time.sleep(int(response.headers["Retry-After"]))
		resp = requests.post(
			os.environ["SUN_THIEF_WEBHOOK"], 
			headers={'Content-Type':'application/x-www-form-urlencoded'}, 
			data={'content': formatted_name})

	else:
		print (f'{resp.status_code} - {resp.text}')

def send_post(p):
	formatted_post = format_post(p)

	resp = requests.post(
		os.environ["SUN_THIEF_WEBHOOK"], 
		headers={'Content-Type':'application/x-www-form-urlencoded'}, 
		data={'content': formatted_post})
	
	# if unauthorized get a new token and post again
	if resp.status_code == 401:
		refresh_token()
		resp = requests.post(
			os.environ["SUN_THIEF_WEBHOOK"], 
			headers={'Content-Type':'application/x-www-form-urlencoded'}, 
			data={'content': formatted_post})

	# retry request after certain time if 429
	if resp.status_code == 429:
		time.sleep(int(response.headers["Retry-After"]))
		resp = requests.post(
			os.environ["SUN_THIEF_WEBHOOK"], 
			headers={'Content-Type':'application/x-www-form-urlencoded'}, 
			data={'content': formatted_post})

	if (resp.status_code == 204):
		record_post(p)

	else:
		print (f'Error: {resp.status_code} {resp.content}')

	time.sleep(int(1))

def refresh_token():
	resp = requests.post(
		os.environ["SUN_THIEF_AUTH_URL"], 
		headers = {
			'Host': 'discord.com', 
			'Content-Type':'application/json'
		},
		json = {
			'login': os.environ["SUN_THIEF_LOGIN"], 
			'password': os.environ["SUN_THIEF_PASSWORD"]
		})

	if (resp.status_code == 200):
		print("Successfully obtained a new token")
	else: 
		print("Failed to obtain a new token")

	os.environ["SUN_THIEF_TOKEN"] = resp.json()["token"]

def loop(): 
	start_time = time.time()
	print("=========Welcome to Sun Thief 1.0===========")

	while True:
		print("Starting new analysis...")
		new_posts = post()
		print("Analysis finished. %s new posts."%new_posts)
		time.sleep(10 - ((time.time() - start_time) % 10))

def format_name(post):
	formatted_time = datetime.datetime.strptime(post["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime('%m-%d-%Y at %H:%M')
	return f'**{post["author"]["username"]}** *{formatted_time}*'

def format_post(post):
	content = f'{post["content"]}'
	if (post["attachments"] != ""):
		for a in post["attachments"]:
			content += a["url"]
	return content

def record_post(post):
	print(f'Adding post {post["id"]}')
	history.append(post["id"])
	file = open("history.txt", "a")
	file.write(f'{post["id"]}\n')
	file.close()

def load_history():
	file = open("history.txt", "r")
	global history
	history = file.readlines()
	file.close()

def main():
	load_history()
	loop()

main()