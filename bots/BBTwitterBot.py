import tweepy
import logging
from config import create_api
from lxml import html
import requests
import time


def main():
	logging.basicConfig(level = logging.INFO)
	logger = logging.getLogger()

	api = create_api()

	week = 1
	comp_table = 5

	HOH_tweeted = RmTw_tweeted = IniNoms_tweeted = Veto_tweeted = FinNoms_tweeted = Evt_tweeted = False

	HOH_col_pos, RmTw_col_pos, IniNoms_col_pos_1, IniNoms_col_pos_2 = 1, 3, 4, 6 #1, 3, 5, 7
	Veto_col_pos, VtUs_col_pos, FinNoms_col_pos_1, FinNoms_col_pos_2 = 8, 10, 12, 14 #7, 11, 13, 15
	Evt_col_pos, Vote_col_pos = 16, 17 #17, 18
	#This is a little complicated because some of the column numbers change 
	#depending on if the veto ceremony has already happened.  This is because 
	#after the veto, a picture is added to the table shifting the column positions.
	#The column positions here are the position at the time that that event happens

	hashtags = ' #BB22 #spoiler #BigBrother'

	#Find the current week.
	page = requests.get('https://bigbrother.fandom.com/wiki/Big_Brother_22_(US)')
	tree = html.fromstring(page.content)
	names = tree.xpath('//table[' + str(comp_table) + ']/tr[' + str(week+2) + ']/td/text()')

	while(names[HOH_col_pos].split('\n')[0] != 'TBD'):
		week += 1
		names = tree.xpath('//table[' + str(comp_table) + ']/tr[' + str(week+2) + ']/td/text()')
	week -= 1
	logger.info('It is week ' + str(week))
	names = tree.xpath('//table[' + str(comp_table) + ']/tr[' + str(week+2) + ']/td/text()')

	#Find what part of the week
	if(names[HOH_col_pos].split('\n')[0] != 'TBD'):
		HOH_tweeted = True
		logger.info('HOH comp is done')
	if(names[RmTw_col_pos].split('\n')[0] != 'TBD'):
		RmTw_tweeted = True
		logger.info('Safety Suite comp is done')
	if(names[IniNoms_col_pos_1].split('\n')[0] + ' and ' + names[IniNoms_col_pos_2].split('\n')[0] != 'TBD and TBD'):
		IniNoms_tweeted = True
		logger.info('Noms are done')
	if(names[Veto_col_pos].split('\n')[0] != 'TBD'):
		Veto_tweeted = True
		logger.info('Veto comp is done')
	noms = names[FinNoms_col_pos_1].split('\n')[0] + ' and ' + names[FinNoms_col_pos_2].split('\n')[0]
	if(noms != 'TBD and TBD' and noms != '   and   '):
		FinNoms_tweeted = True
		logger.info('Veto ceremony is done')


	while(week<14):
		page = requests.get('https://bigbrother.fandom.com/wiki/Big_Brother_22_(US)')
		tree = html.fromstring(page.content)
		names = tree.xpath('//table[' + str(comp_table) + ']/tr[' + str(week+2) + ']/td/text()')
		HOH = names[HOH_col_pos].split('\n')[0]
		if((HOH != 'TBD') and HOH_tweeted == False):
			Tweet = HOH + ' has won the HOH competition' + hashtags
			logger.info('Tweeting: ' + Tweet)
			api.update_status(Tweet)
			HOH_tweeted = True

		RmTw = names[RmTw_col_pos].split('\n')[0]
		if((RmTw != 'TBD') and RmTw_tweeted == False):
			Tweet = RmTw + ' has won the Safety Suite competition' + hashtags
			logger.info('Tweeting: ' + Tweet)
			api.update_status(Tweet)
			RmTw_tweeted = True

		IniNoms = names[IniNoms_col_pos_1].split('\n')[0] + ' and ' + names[IniNoms_col_pos_2].split('\n')[0]
		if((IniNoms != 'TBD and TBD') and IniNoms_tweeted == False):
			Tweet = HOH + ' has nominated ' + IniNoms + ' for eviction' + hashtags
			logger.info('Tweeting: ' + Tweet)
			api.update_status(Tweet)
			IniNoms_tweeted = True

		Veto = names[Veto_col_pos].split('\n')[0]
		if((Veto != 'TBD') and Veto_tweeted == False):
			Tweet = Veto + ' has won the Veto competition' + hashtags
			logger.info('Tweeting: ' + Tweet)
			api.update_status(Tweet)
			Veto_tweeted = True

		VtUs = names[VtUs_col_pos].split('\n')[0]
		FinNoms = names[FinNoms_col_pos_1].split('\n')[0] + ' and ' + names[FinNoms_col_pos_2].split('\n')[0]
		if((FinNoms != 'TBD and TBD') and (FinNoms != '   and   ') and FinNoms_tweeted == False):
		#FinNoms could be either of these two things depending on whether the veto ceremony has happened.
			if(FinNoms != IniNoms):
				Tweet = Veto + ' has used the Power of Veto. The final nominees are ' + FinNoms + hashtags
				logger.info('Tweeting: ' + Tweet)
				api.update_status(Tweet)
				FinNoms_tweeted = True
			else:
				Tweet = Veto + ' has not used the Power of Veto. The final nominees are ' + FinNoms + hashtags
				logger.info('Tweeting: ' + Tweet)
				api.update_status(Tweet)
				FinNoms_tweeted = True

		Evt = names[Evt_col_pos].split('\n')[0]
		Vote = names[Vote_col_pos].split('\n')[0]
		if((Vote != '\xa0?-?') and (Evt != '\xa0?-?') and Evt_tweeted == False):
		#The Vote and Evt column position change depending on if the veto ceremony has happened.
			Tweet = Evt + ' has been evicted by a vote of' + Vote + hashtags
			logger.info('Tweeting: ' + Tweet)
			api.update_status(Tweet)
			Evt_tweeted = True

		if(Evt_tweeted):
			week += 1
			HOH_tweeted = RmTw_tweeted = IniNoms_tweeted = Veto_tweeted = FinNoms_tweeted = Evt_tweeted = False

		time.sleep(60)

if __name__ == "__main__":
	main()