# -*- coding: utf-8 -*-

from glob import glob
import os
import sys
import threading
import time

sys.path.append(os.path.join(sys.path[0], '../../'))
import schedule
from instabot import Bot, utils

import config

bot = Bot(comments_file=config.COMMENTS_FILE,
          blacklist_file=config.BLACKLIST_FILE,
          whitelist_file=config.WHITELIST_FILE,
          friends_file=config.FRIENDS_FILE)
bot.login()
bot.logger.info("The InstaScheduler is Now Running. It is Safe to run it 24/7!")

random_user_file = utils.file(config.USERS_FILE)
random_hashtag_file = utils.file(config.HASHTAGS_FILE)
photo_captions_file = utils.file(config.PHOTO_CAPTIONS_FILE)
posted_pic_list = utils.file(config.POSTED_PICS_FILE).list
hashtags_file = utils.file(config.PICS_HASHTAGS_FILE)
collaborations_file = utils.file(config.COL_FILE)

pics = sorted([os.path.basename(x) for x in
               glob(config.PICS_PATH + "/*.jpg")])


def stats():
    bot.save_user_stats(bot.user_id)


def like_hashtags():
    bot.like_hashtag(random_hashtag_file.random(), amount=500 // 24)


def like_timeline():
    bot.like_timeline(amount=300 // 24)


def like_followers_from_random_user_file():
    bot.like_followers(random_user_file.random(), nlikes=3)


def follow_followers():
    bot.follow_followers(random_user_file.random(), nfollows=config.NUMBER_OF_FOLLOWERS_TO_FOLLOW)


def comment_medias():
    bot.comment_medias(bot.get_timeline_medias())


def unfollow_non_followers():
    bot.unfollow_non_followers(n_to_unfollows=config.NUMBER_OF_NON_FOLLOWERS_TO_UNFOLLOW)


def follow_users_from_hastag_file():
    bot.follow_users(bot.get_hashtag_users(random_hashtag_file.random()))


def comment_hashtag():
    hashtag = random_hashtag_file.random()
    bot.logger.info("Commenting on hashtag: " + hashtag)
    bot.comment_hashtag(hashtag)


def upload_pictures():  # Automatically post a pic in 'pics' folder
	count_available = 0
	count_total = 0
	available_images = []
	used_images = []
	for pic in pics:
		count_total = count_total + 1
		if pic not in posted_pic_list:
			count_available = count_available + 1
			available_images.append(pic)
		else:
			pass
	for pic in pics:	
		if pic in posted_pic_list:
			used_images.append(pic)
		else:
			pass
	print("_________________________________________________________________________\n")
	count_used = len(used_images)
	print("\nThe Following {} images were used and can be moved or deleted!\n".format(count_used))
	print("To delete the images you can you the command bellow:\ncd",config.PICS_PATH)
	print("rm",*used_images,"","\n")
	print("To move the images you can you the command bellow:\ncd",config.PICS_PATH)
	print("mv",*used_images," <path to destination>")
	print("_________________________________________________________________________\n")
	print("\nThere are {} out of {} images available in the inventory".format(count_available, count_total))
	print("\nThe following images were not yet used: \n")
	print(*available_images, sep='  ')
	print("_________________________________________________________________________\n")
	print("Starting Scheduler !!")
	try:
		for pic in pics:
			if pic in posted_pic_list:
				continue
			bot.logger.info("--------------------------------------------Will try upload picture script!--------------------------------------------")
			followme_message = config.FOLLOW_MESSAGE
			picture_by = config.PIC_BY
			caption = photo_captions_file.random()
			hashtags = hashtags_file.random()
			full_caption = "{}\n.\n{}\n.\n{}\n.\n{}".format(caption, picture_by, followme_message, hashtags)
			bot.logger.info("Uploading pic with caption: " + caption)
			bot.upload_photo(config.PICS_PATH + pic, caption=full_caption)
			if bot.api.last_response.status_code != 200:
				bot.logger.error("Something went wrong, read the following ->\n")
				bot.logger.error(bot.api.last_response)
				break

			if pic not in posted_pic_list:
				# After posting a pic, comment it with all the hashtags specified
				# In config.PICS_HASHTAGS
				posted_pic_list.append(pic)
				with open('pics.txt', 'a') as f:
					f.write(pic + "\n")
				collaborations = collaborations_file.random()
				count_available = count_available - 1
				bot.logger.info("Succesfully uploaded: " + pic)
				bot.logger.info("Commenting uploaded photo with " + collaborations)
				medias = bot.get_your_medias()
				last_photo = medias[0]  # Get the last photo posted
				bot.logger.info(last_photo)
				#bot.comment(last_photo, collaborations)
				bot.comment(last_photo)
				print("_________________________________________________________________________\n")
				print("There are {} available images in the inventory".format(count_available))
				print("_________________________________________________________________________\n")
				break
	except Exception as e:
		posted_pic_list.append(pic)
		with open('pics.txt', 'a') as f:
			f.write(pic + "\nThe image above failed to be posted!\n")
		bot.logger.error("Couldn't upload pic")
		bot.logger.error(str(e))


def put_non_followers_on_blacklist():  # put non followers on blacklist
    try:
        bot.logger.info("Creating non-followers list")
        followings = set(bot.following)
        followers = set(bot.followers)
        friends = bot.friends_file.set  # same whitelist (just user ids)
        non_followers = followings - followers - friends
        for user_id in non_followers:
            bot.blacklist_file.append(user_id, allow_duplicates=False)
        bot.logger.info("Done.")
    except Exception as e:
        bot.logger.error("Couldn't update blacklist")
        bot.logger.error(str(e))


def run_threaded(job_fn):
    job_thread = threading.Thread(target=job_fn)
    job_thread.start()


schedule.every(24).hours.do(run_threaded, upload_pictures)
schedule.every().sunday.at("17:05").do(run_threaded, upload_pictures)
schedule.every().monday.at("19:00").do(run_threaded, upload_pictures)
schedule.every().monday.at("22:00").do(run_threaded, upload_pictures)
schedule.every().tuesday.at("15:00").do(run_threaded, upload_pictures)
schedule.every().tuesday.at("22:00").do(run_threaded, upload_pictures)
schedule.every().wednesday.at("17:00").do(run_threaded, upload_pictures)
schedule.every().thursday.at("07:00").do(run_threaded, upload_pictures)
schedule.every().thursday.at("22:00").do(run_threaded, upload_pictures)
schedule.every().friday.at("01:00").do(run_threaded, upload_pictures)
schedule.every().friday.at("20:00").do(run_threaded, upload_pictures)
schedule.every().saturday.at("00:00").do(run_threaded, upload_pictures)
schedule.every().saturday.at("02:00").do(run_threaded, upload_pictures)
schedule.every(1).hour.do(run_threaded, stats)
schedule.every(12).to(16).hours.do(run_threaded, like_hashtags)
schedule.every(4).hours.do(run_threaded, like_timeline)
schedule.every(1).days.at("16:00").do(run_threaded, like_followers_from_random_user_file)
schedule.every(2).days.at("11:00").do(run_threaded, follow_followers)
schedule.every(16).hours.do(run_threaded, comment_medias)
schedule.every(10).to(25).hours.do(run_threaded, unfollow_non_followers)
schedule.every(12).hours.do(run_threaded, follow_users_from_hastag_file)
schedule.every(5).to(8).hours.do(run_threaded, comment_hashtag)
schedule.every(4).days.at("07:50").do(run_threaded, put_non_followers_on_blacklist)


#   Sunday: 5:00 p.m.
#   Monday: 7:00 p.m. & 10:00 p.m.
#   Tuesday: 3:00 a.m. & 10:00 p.m.
#   Wednesday: 5:00 p.m.
#   Thursday: 7:00 a.m. & 11:00 p.m.
#   Friday: 1:00 a.m. & 8:00 p.m.
#   Saturday: 12:00 a.m. & 2:00 a.m.
    
    
while True:
    schedule.run_pending()
    time.sleep(1)
