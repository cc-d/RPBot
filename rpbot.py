import json
import time
import praw
import logging
import sys
import calendar
import re

def main():
	logger = logging.getLogger('rpbot')
	handler = logging.FileHandler('rpbot.log')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)

	with open('config.json', 'r+') as c:
		config = json.loads(c.read())

	with open('subreddits.txt', 'r+') as s:
		subreddits = '+'.join(s.read().splitlines())

	with open('submitted.txt', 'r+') as s:
		submitted = s.read().splitlines()[-100:]

	try:
		r = praw.Reddit(config['bot']['user-agent'])
		r.login(config['bot']['username'], config['bot']['password'])
		logger.info('Logged into reddit.')
	except Exception as e:
		logger.error(str(e))

	while True:
		try:
			all_subreddits = r.get_subreddit(subreddits)
			submissions = all_subreddits.get_new(limit=30)
			for submission in submissions:
				try:
					if submission.id not in submitted and submission.url not in config['blacklist']['urls'] and \
						not any(word in submission.title for word in config['blacklist']['words']) and \
						(submission.created_utc - calendar.timegm(time.gmtime())) <= -180:
			
							ctime = time.time()
							if ctime - submission.author.created_utc <= 18000:
								logger.error('Submission is too young. Waiting for subreddit moderators to review.')
								break
				
							print 'Creating submission. Do not kill me!'
				
							stitle = re.sub(config['regex'][0], '', submission.title, flags=re.IGNORECASE)
							for cregex in config['regex'][1:]:
								stitle = re.sub(cregex, '', stitle, flags=re.IGNORECASE)
				
							flair = str(submission.subreddit).lower().replace('porn','')
							flair = flair[0].upper() + flair[1:]
							author = 'http://reddit.com/' + str(submission.permalink).split('/')[6]
	
							fan_submission = r.submit(flair + 'Fans', stitle, url=submission.url)
							fan_submission.approve()	
							if submission.over_18:
								local_submission.mark_as_nsfw()
							
							fan_comment = fan_submission.add_comment('[Link To Original Submission]('
																		+  author
																		+ ') \r\n\r\n______\r\n\r\n^^^I ^^^Am ^^^A ^^^Bot. ^^^Please ^^^Message ^^^/u/cc-d ^^^if ^^^you ^^^have ^^^any ^^^feedback ^^^or ^^^suggestions.')

							local_submission = r.submit(config['bot']['subreddit'], '[' + flair + '] ' + stitle, url=submission.url)
							r.set_flair(config['bot']['subreddit'], local_submission, flair_text=flair)
							local_submission.approve()
							if submission.over_18:
								local_submission.mark_as_nsfw()	
			
							local_comment = local_submission.add_comment('[' + flair + 'Fans](' + str(fan_submission.permalink) + ')'
																		+ ' | [Link To Original Submission](' + author 
																		+ ') \r\n\r\n______\r\n\r\n^^^I ^^^Am ^^^A ^^^Bot. ^^^Please ^^^Message ^^^/u/cc-d ^^^if ^^^you ^^^have ^^^any ^^^feedback ^^^or ^^^suggestions.')
							local_comment.approve()
							submitted.append(submission.id)
			
							with open('submitted.txt', 'w') as s:
								s.write('\n'.join(submitted))
			
							logger.info('Successfully submitted submission ' + str(local_submission.permalink))
			
							print 'It is to ok to kill me now.'
							time.sleep(5)
	
				except praw.errors.AlreadySubmitted as e:
						logger.error(str(e) + ' (already submitted)')
						if submission.id not in submitted:
							submitted.append(submission.id)
							with open('submitted.txt', 'w') as s:
								s.write('\n'.join(submitted))
							time.sleep(2)
		
				except Exception as e:
					logger.error(str(e))
					time.sleep(2)

			time.sleep(5)

		except Exception as e:
			logger.error(str(e))
			time.sleep(10)

if __name__ == '__main__':
	main()

