import os, sys
import functools
import subprocess
import threading
import random
import requests
import re
import string

from pytube import YouTube
from tkinter import *

stop = threading.Event()


def clear():
	e1.delete(0,END)
	e2.delete(0,END)
	tkvar.set('720p')
	v1.set("")
	v2.set("")


# on change dropdown value
def change_dropdown(*args):
	resolution = tkvar.get()
	return resolution


def foldertitle(url):
	try:
		res = requests.get(url)
	except:
		v2.set("Check your internet connection...")
		return False

	plain_text = res.text

	if 'list=' in url:
		eq = url.rfind('=') + 1
		cPL = url[eq:]
	else:
		v2.set("")
		v2.set("Incorrect attempt...")
		return False

	return cPL


def link_snatcher(url):
	our_links = []
	try:
		res = requests.get(url)
	except:
		v2.set("")
		v2.set("Check your internet connection.....")
		return False

	plain_text = res.text

	if 'list=' in url:
		eq = url.rfind('=') + 1
		cPL = url[eq:]
	else:
		v2.set("")
		v2.set("Incorrect Playlist.Please try again.")
		return False

	tmp_mat = re.compile(r'watch\?v=\S+?list=' + cPL)
	mat = re.findall(tmp_mat, plain_text)

	for m in mat:
		new_m = m.replace('&amp;', '&')
		work_m = 'https://youtube.com/' + new_m
		if work_m not in our_links:
			our_links.append(work_m)

	return our_links


def background(func):
	@functools.wraps(func)
	def wrapper():
		t = threading.Thread(target=func)
		t.start()
	return wrapper


def cancel():
	stop.set()
	sys.exit(1)


@background
def size_calculator():
	try:
		playlist_url =  e1.get()
		if e2.get() == '':
			video_number_to_start_download = 1
		else:
			video_number_to_start_download = int(e2.get())
		resolution = tkvar.get()
	except Exception as e:
		v1.set("")
		v1.set(e)

	our_links = link_snatcher(playlist_url)[video_number_to_start_download-1:]
	len_our_links = len(our_links)
	count = 0
	skipped_count = 0
	playlist_size = 0.0

	for link in our_links:
		try:
			yt = YouTube(link)
		except:
			v1.set("")
			v1.set("Connection problem.Unable to fetch video info.....")
			v2.set("")
			v2.set('File size until now - {} GB'.format(str(round(playlist_size / 1024, 2))))
			count += 1
			skipped_count += 1
			continue

		if resolution in choices:
			vid = yt.streams.filter(file_extension='mp4', res=resolution).first()
			v1.set("")
			v1.set('Total Videos - {}.\tCalculating. . . '.format(len_our_links))
			v2.set("")
			try:
				if resolution == '360p' or resolution == '720p':
					playlist_size += round(vid.filesize / (1024 * 1024), 2)
					v2.set('File size for video number {} = {} MB'.format(count + 1,
																		  str(round(vid.filesize / (1024 * 1024), 2))))
				else:
					playlist_size += round(vid.filesize_approx / (1024 * 1024), 2)
					v2.set('File size for video number {} = {} MB (approx.)'.format(
						count+1, str(round(vid.filesize_approx / (1024 * 1024), 2))))
				count += 1
			except Exception as e:
				count += 1
				skipped_count += 1
				continue
		else:
			v1.set("")
			v2.set("")
			v2.set('Something went wrong.Please rerun the program.')
	if skipped_count > 0:
		computed_video_count = len_our_links - skipped_count
		average_video_size = playlist_size / computed_video_count
		playlist_size = average_video_size * len_our_links
	v1.set("CALCULATION COMPLETED!")
	v2.set("")
	v2.set('File size  - {} GB (approx.) \t\t Skipped Video Count - {}'.format(str(round(playlist_size / 1024, 2)),
																			skipped_count))


@background
def downloader():
	try:
		playlist_url =  e1.get()
		if e2.get() == '':
			video_number_to_start_download = 1
		else:
			video_number_to_start_download = int(e2.get())
		resolution = tkvar.get()
		os.chdir(BASE_DIR)
		new_folder_name = foldertitle(playlist_url)
	except Exception as e:
		v1.set("")
		v1.set(e)

	try:
		os.mkdir(new_folder_name)
	except:
		v2.set("")
		v2.set("Folder already exists.Delete or copy previous folders to different location.")

	os.chdir(new_folder_name)
	SAVEPATH = os.getcwd()
	x=[]
	for root, dirs, files in os.walk(".", topdown=False):
		for name in files:
			pathh = os.path.join(root, name)
			if os.path.getsize(pathh) < 1:
				os.remove(pathh)
			else:
				x.append(str(name))

	v2.set("")
	v2.set("Connecting.......")

	our_links = link_snatcher(playlist_url)[video_number_to_start_download-1:]
	len_our_links = len(our_links)
	count = 0

	for link in our_links:
		try:
			yt = YouTube(link)
			title = (yt.title)
			cleaned_title = title.replace('/', ' ')
			thumbnail_url = yt.thumbnail_url
			r = requests.get(thumbnail_url, allow_redirects=True)
			try:
				os.mkdir('thumbnails')
			except:
				v2.set("")
				v2.set("Folder already exists.Delete or copy previous folders to different location.")
			thumbnail_dir = os.path.abspath('.') + '/thumbnails/'
			open(os.path.join(thumbnail_dir, (cleaned_title +'.jpg')), 'wb').write(r.content)
			main_title = cleaned_title
			main_title = main_title + '.mp4'
			main_title = main_title.replace('|', '')
		except:
			v2.set("")
			v2.set("Connection problem.Unable to fetch video info.....")
			break

		if main_title not in x:
			try:
				if resolution == '360p' or resolution == '720p':
					vid = yt.streams.filter(progressive=True, file_extension='mp4', res=resolution).first()
					v1.set("")
					v1.set('Downloading. . . ' + vid.default_filename)
					v2.set("")
					v2.set('File size  - ' + str(round(vid.filesize / (1024 * 1024), 2)) + ' MB.')
					vid.download(SAVEPATH)
					count+=1
				else:
					v1.set("")
					v2.set("")
					v2.set("Download Option available only for '360p' and '720p' resolutions for now.")
			except Exception as e:
				v1.set("")
				v2.set("")
				v2.set('Something went wrong. Please rerun the program.')
		else:
			v1.set("")
			v2.set("")
			v2.set(f'Skipping "{main_title}" video.')

	v1.set("DOWNLOAD COMPLETED!")
	v2.set("")
	v2.set("Playlist Successfully Downloaded..Enjoy!!")


BASE_DIR = os.getcwd()

master = Tk()
# screen_width = master.winfo_screenwidth()
# screen_height = master.winfo_screenheight()
master.geometry("1050x580")
master.title("Youtube Playlist Downloader")
master.resizable(False, False)

Label(master, text="Youtube Playlist URL", font=('', '15')).grid(row=0, pady=20)
Label(master, text="Video Number To Start", font=('', '15')).grid(row=1, pady=20)
# Create a Tkinter variable
tkvar = StringVar(master)

# Dictionary with options
choices = ('720p', '144p', '240p', '360p', '480p', '1080p')
tkvar.set('720p') # set the default option

popupMenu = OptionMenu(master, tkvar, *choices)
Label(master, text="Choose a resolution", font=('', '15')).grid(row = 2, column = 0, pady=20)
popupMenu.grid(row = 2, column =1, pady=20, ipady=10, sticky="ew")
# link function to change dropdown
tkvar.trace('w', change_dropdown)

v1 = StringVar()
v2 = StringVar()
Label(master, textvariable=v1, font=('', '11')).grid(row=5, column=1, ipady=2)
Label(master, textvariable=v2, font=('', '11')).grid(row=6, column=1, ipady=2)

e1 = Entry(master, width=100)
e2 = Entry(master, width=100)
e1.grid(row=0, column=1, pady=20, ipady=10)
e2.grid(row=1, column=1, pady=20, ipady=10)

Button(master, text='Calculate Size', font=('', '11'),background='light blue',width='80', command=size_calculator).grid(row=7, column=1, sticky=W, pady=4, ipady=10)
Button(master, text='Download', font=('', '11'),background='light blue',width='80', command=downloader).grid(row=8, column=1, sticky=W, pady=4, ipady=10)
Button(master, text='Reset',font=('', '11'),background='light blue', width='80', command=clear).grid(row=9, column=1, sticky=W, pady=4, ipady=10)
Button(master, text='Cancel & Exit', font=('', '11'),background='light blue',width='80', command=cancel).grid(row=10, column=1, sticky=W, pady=4, ipady=10)

mainloop()






