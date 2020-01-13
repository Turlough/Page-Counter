from PyPDF2 import PdfFileReader as Reader
from pathlib import Path
import os
from PIL import Image

fixpath = lambda path: str(Path(path.strip()))
join = lambda dir, file: fixpath(os.path.join(dir, file))
change_ext = lambda file, new_ext: file[0:-4] + new_ext



def select_folder():
	'''
	You can drag and drop a folder from Windows Explorer to the shell
	'''

	f = input("Type or drop drop folder here\n -> ")
	if len(f) == 0:
		input("No folder selected. Press enter again to quit")
		exit()
	return fixpath(f)


def get_files(folder):

	is_pdf = lambda f: f.lower().endswith('.pdf')
	is_tif = lambda f: f.lower().endswith('.tif')

	full_list = []
	for dirname, dirnames, filenames in os.walk(folder):
		filepaths = list(map(lambda f: os.path.join(dirname, f), filenames))
		full_list.extend(filepaths)

	pdfs = [f for f in full_list if is_pdf(f)]
	tifs = [f for f in full_list if is_tif(f)]

	return pdfs, tifs


def count_pdf(pdf):
	'''
	Gets the pagecount of the pdf
	'''
	result = 0
	with open(pdf,"rb") as f:
		p = Reader(f)
		result = p.getNumPages()
	print(f'{result}\t {os.path.basename(pdf)}')
	return result


def count_tif(tif):

	count = 0
	with Image.open(tif) as image:
		count = image.n_frames
	print(f'{count}\t {os.path.basename(tif)}')
	return count


def count_pdf_list(files):
	pages = 0
	for f in files:
		pages += count_pdf(f)

	return len(files), pages


def count_tif_list(files):
	pages = 0
	for f in files:
		pages += count_tif(f)

	return len(files), pages

def main():

	while True:
		print('_______________')
		folder = select_folder()
		pdfs, tifs = get_files(folder)
		print(f'Found {len(pdfs)} PDF documents, {len(tifs)} TIF documents. Counting pages...')
		
		print()
		print(f'\nFolder: {folder}')
		# PDF count
		docs, pages = count_pdf_list(pdfs)
		print(f'\tPDF: {docs} documents, {pages} pages')
		# TIF count
		docs, pages = count_tif_list(tifs)
		print(f'\tTIF: {docs} documents, {pages} pages')


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print(str(e))
	finally:
		input("Press Enter to exit\n")
		pass
