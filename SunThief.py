import time, sched, json, requests, os, datetime
from datetime import timedelta
from pytz import timezone

def post():
	auth = {'Authorization': os.environ["SUN_THIEF_TOKEN"]}

	wcb = requests.get(f'{os.environ["SUN_THIEF_FROM_CHANNEL"]}?limit=10', headers=auth).json()[::-1]
	wcb_ids = list(map(lambda x: f'{x["id"]}\n', wcb))
	new_posts = list(set(wcb_ids) - set(history))
	print('Found these ids:', new_posts)

	length = 0

	for i in wcb_ids:
		if i in new_posts:
			post = wcb[wcb_ids.index(i)]
			if ("WCB Schedule Channel Information" not in post["content"]):
				send_name(post)
				send_post(post)
				length += 1

	return length

def send_name(p):
	curr_author = p["author"]["id"]
	global prev_author
	if curr_author == prev_author:
		return

	time.sleep(1)

	title = format_title(p)
	resp = requests.post(
		os.environ["SUN_THIEF_WEBHOOK"], 
		headers={'Content-Type':'application/x-www-form-urlencoded'}, 
		data={'content': title})
	
	# if unauthorized get a new token and post again
	if resp.status_code == 401:
		refresh_token()
		resp = requests.post(
			os.environ["SUN_THIEF_WEBHOOK"], 
			headers={'Content-Type':'application/x-www-form-urlencoded'}, 
			data={'content': title})

	# retry request after certain time if 429
	if resp.status_code == 429:
		time.sleep(2)
		resp = requests.post(
			os.environ["SUN_THIEF_WEBHOOK"], 
			headers={'Content-Type':'application/x-www-form-urlencoded'}, 
			data={'content': title})

	if resp.status_code == 204:
		prev_author = curr_author

	else:
		print(f'{resp.status_code} {resp.content}')

def send_post(p):
	time.sleep(1)

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
		time.sleep(int(resp.headers["Retry-After"]))
		resp = requests.post(
			os.environ["SUN_THIEF_WEBHOOK"], 
			headers={'Content-Type':'application/x-www-form-urlencoded'}, 
			data={'content': formatted_post})

	if (resp.status_code == 204):
		record_post(p)

	else:
		print(f'Error: {resp.status_code} {resp.content}')

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
		time.sleep(30 - ((time.time() - start_time) % 30))

def format_title(post):
	return f'**{post["author"]["username"]}**'

def format_post(post):
	content = f'{post["content"]}'
	if (post["attachments"] != ""):
		for a in post["attachments"]:
			content += a["url"]
	return content

def format_time(post):
	eastern = timezone('US/Eastern')
	now = datetime.datetime.today()
	timestamp = datetime.datetime.strptime(post["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")

	if timestamp.date() == now.date():
		formatted_time = timestamp.astimezone(eastern).strftime('Today at %I:%M %p %Z')
	elif timestamp.date() == (now - timedelta(days = 1)).date():
		formatted_time = timestamp.astimezone(eastern).strftime('Yesterday at %I:%M %p %Z')
	else:
		formatted_time = timestamp.astimezone(eastern).strftime('%m-%d-%Y at %I:%M %p %Z')
	return formatted_time

def record_post(post):
	print(f'Adding post {post["id"]}')
	history.append(f'{post["id"]}\n')
	file = open("history.txt", "a")
	file.write(f'{post["id"]}\n')
	file.close()

def load_history():
	global history
	file = open("history.txt", "r")
	history = file.readlines()
	file.close()

def main():
	global prev_author
	prev_author = None
	load_history()
	loop()

main()