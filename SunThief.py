import time, sched, json, requests, json

def get_config():
	global config

	file = open("config.json", "r")
	config = json.loads(file.read())
	file.close()

def post():
	auth = {'Authorization': config["token"]}

	wcb = requests.get(f'{config["fromChannel"]}?limit=50', headers=auth).json()
	versus = requests.get(f'{config["toChannel"]}', headers=auth).json()

	wcb_posts = list(map(lambda x: f'**{x["author"]["username"]}**\n{x["content"]}', wcb))
	versus_posts = list(map(lambda x: x["content"], versus))
	new_posts = list(set(wcb_posts) - set(versus_posts))

	for x in wcb:
		if f'**{x["author"]["username"]}**\n{x["content"]}' in new_posts:
			content = f'**{x["author"]["username"]}**\n{x["content"]}'
			resp = requests.post(config["webhook"], headers={'Content-Type':'application/x-www-form-urlencoded'}, data={"content": content})
			
			# if unauthorized get a new token and post again
			if resp.status_code == 401:
				refresh_token()
				resp = requests.post(config["webhook"], headers={'Content-Type':'application/x-www-form-urlencoded'}, data={"content": content})
			
			print(resp.status_code)
			time.sleep(int(1))

	return len(new_posts)

def refresh_token():
	resp = requests.post(config["authUrl"], headers={'Host': 'discord.com', 'Content-Type':'application/json'}, json={"login": config["login"], "password": config["password"]})
	print(resp.status_code)
	config["token"] = resp.json()["token"]
	file = open("config.json", "w+")
	file.write(json.dumps(config))
	file.close()

def main():
	start_time = time.time()
	print("=========Welcome to Sun Thief 1.0===========")
	get_config()

	while True:
		print("Starting new analysis...")
		new_posts = post()
		print("Analysis finished. %s new posts."%new_posts)
		time.sleep(config["timer"] - ((time.time() - start_time) % config["timer"]))

main()