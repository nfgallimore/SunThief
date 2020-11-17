import time, sched, json, requests, os

def post():
	auth = {'Authorization': os.environ["SUN_THIEF_TOKEN"]}

	wcb = requests.get(f'{os.environ["SUN_THIEF_FROM_CHANNEL"]}?limit=10', headers=auth).json()
	versus = requests.get(f'{os.environ["SUN_THIEF_TO_CHANNEL"]}', headers=auth).json()

	# format posts to similar way and check if we've already posted it
	wcb_posts = list(map(lambda x: format_post(x), wcb))
	versus_posts = list(map(lambda x: x["content"], versus))
	new_posts = list(set(wcb_posts) - set(versus_posts))

	for p in wcb[::-1]:

		formatted_post = format_post(p)

		if formatted_post in new_posts:
			# post content to webhook
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


def debug(): 
	start_time = time.time()
	print("=========Welcome to Sun Thief 1.0===========")

	while True:
		print("Starting new analysis...")
		new_posts = post()
		print("Analysis finished. %s new posts."%new_posts)
		time.sleep(60 - ((time.time() - start_time) % 60))

def main():
	post()

def format_post(post):
	content = f'**{post["author"]["username"]}**\n{post["content"]}'
	if (post["attachments"] != ""):
		for a in post["attachments"]:
			content += a["url"]
	return content

main()