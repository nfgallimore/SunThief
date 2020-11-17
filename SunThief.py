import time, sched, json, requests, os

def post():
	auth = {'Authorization': os.environ["SUN_THIEF_TOKEN"]}

	wcb = requests.get(f'{os.environ["SUN_THIEF_FROM_CHANNEL"]}?limit=10', headers=auth).json()
	versus = requests.get(f'{os.environ["SUN_THIEF_TO_CHANNEL"]}', headers=auth).json()

	# format posts to similar way and check if we've already posted it
	wcb_posts = list(map(lambda x: f'**{x["author"]["username"]}**\n{x["content"]}', wcb))
	versus_posts = list(map(lambda x: x["content"], versus))
	new_posts = list(set(wcb_posts) - set(versus_posts))

	for x in wcb:
		if f'**{x["author"]["username"]}**\n{x["content"]}' in new_posts:

			# format post
			content = f'**{x["author"]["username"]}**\n{x["content"]}'

			# post content to webhook
			resp = requests.post(
				os.environ["SUN_THIEF_WEBHOOK"], 
				headers={'Content-Type':'application/x-www-form-urlencoded'}, 
				data={'content': content})
			
			# if unauthorized get a new token and post again
			if resp.status_code == 401:
				refresh_token()
				resp = requests.post(
					os.environ["SUN_THIEF_WEBHOOK"], 
					headers={'Content-Type':'application/x-www-form-urlencoded'}, 
					data={'content': content})
			
			print(resp.status_code)
			time.sleep(int(1))

	return len(new_posts)

def refresh_token():
	# get token from discord api
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

	print(resp.status_code)

	# set token
	os.environ["SUN_THIEF_TOKEN"] = resp.json()["token"]


def loop(): 
	start_time = time.time()
	print("=========Welcome to Sun Thief 1.0===========")

	while True:
		print("Starting new analysis...")
		new_posts = post()
		print("Analysis finished. %s new posts."%new_posts)
		time.sleep(60 - ((time.time() - start_time) % 60))

post()