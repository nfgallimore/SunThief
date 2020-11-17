import time, sched, json, requests

def sun_thief():
	auth = {'Authorization': 'insert_token_here'}

	wcb = requests.get('https://discord.com/api/v8/channels/770027870876860466/messages?limit=10', headers=auth).json()
	versus = requests.get('https://discord.com/api/v8/channels/778139603966230548/messages', headers=auth).json()

	wcbPosts = list(map(lambda post: f'**{post["author"]["username"]}**\n{post["content"]}', wcb))
	versusPosts = list(map(lambda post: post["content"], versus))
	newPosts = list(set(wcbPosts) - set(versusPosts))

	for post in wcb:
		if f'**{post["author"]["username"]}**\n{post["content"]}' in newPosts:
			content = f'**{post["author"]["username"]}**\n{post["content"]}'
			resp = requests.post('https://discordapp.com/api/webhooks/778139913022734356/bMil0rT6KRy_8KAm3_YTpQIpgzKjNFV4ouYLC9H72sQSG5hHb_ZfiVKQkOipLfgBGPSx', headers={'Content-Type':'application/x-www-form-urlencoded'}, data={"content": content})
			print(resp)
			time.sleep(int(1))

	return len(newPosts)

starttime = time.time()

print("=========Welcome to Sun Thief 1.0===========")

while True:
	print("Starting new analysis...")
	newPosts = sun_thief()
	print("Analysis finished. %s new posts."%newPosts)
	time.sleep(60.0 - ((time.time() - starttime) % 60.0))