import time
import datetime

class Timer:
	'''
	A utility class for showing progress on batch jobs.
	'''

	start_time = time.time()
	total = 0

	def __init__(self, total):
		self.start(total)

	def start(self, total):
		'''
		Starts the timer. Progress begins at this time.
		The 'total' parameter is the total number of units to process. Progress is evaluated against this.
		'''
		self.total = total
		self.start_time = time.time()

	def get_progress(self, counter):
		'''
		Print a string representing progress, time remaining, etc.
		The 'counter' parameter is the number of units processed so far.
		'''

		now = time.time()
		elapsed = now - self.start_time
		progress = counter/self.total
		finish_time = self.start_time + elapsed / progress
		remaining = finish_time - now

		str_progress = str(round(100 * progress)) + '%'
		str_elapsed = str(datetime.timedelta(seconds=round(elapsed)))
		str_remaining = str(datetime.timedelta(seconds=round(remaining)))
		str_finish = str(datetime.timedelta(seconds=int(finish_time % 86400)))
		print(f'-> {counter}/{self.total} ({str_progress}) done. Runtime: {str_elapsed} since start. Expected to complete at {str_finish}, ({str_remaining} remaining)\r', end='\r')