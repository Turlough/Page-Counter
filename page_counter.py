from PyPDF2 import PdfFileReader as Reader
from pathlib import Path
import os
from PIL import Image
from timer import Timer

fixpath = lambda path: str(Path(path.replace('"','').strip()))
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
	print(f)
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
	return result


def count_tif(tif):

	count = 0
	with Image.open(tif) as image:
		count = image.n_frames
	return count


def count_pdf_list(files, timer):
	pages = 0
	docs = 0
	for f in files:
		pages += count_pdf(f)
		docs += 1
		timer.get_progress(docs)

	return len(files), pages


def count_tif_list(files, timer):
	pages = 0
	docs = 0
	for f in files:
		pages += count_tif(f)
		docs += 1
		timer.get_progress(docs)

	return docs, pages

def main():

	while True:
		print('_______________')
		folder = select_folder()
		pdfs, tifs = get_files(folder)
		print(f'Found {len(pdfs)} PDF documents, {len(tifs)} TIF documents. Counting pages...')
		timer = Timer(len(pdfs) + len(tifs))
		print()
		print(f'\nFolder: {folder}')
		print('\nCounting PDFs')
		p_docs, p_pages = count_pdf_list(pdfs, timer)
		print('\nCounting TIFFs')
		t_docs, t_pages = count_tif_list(tifs, timer)
		print()
		print(f'\n\n{folder}: Totals:')
		print(f'\tPDF: {p_docs} documents, {p_pages} pages')
		print(f'\tTIF: {t_docs} documents, {t_pages} pages')


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print(str(e))
	finally:
		input("Press Enter to exit\n")
		pass
