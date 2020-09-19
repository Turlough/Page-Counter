from PyPDF2 import PdfFileReader as Reader
from pathlib import Path
import os
from PIL import Image
from tqdm import tqdm

from PyPDF2 import PdfFileReader

fixpath = lambda path: str(Path(path.replace('"', '').strip()))
join = lambda dir, file: fixpath(os.path.join(dir, file))

last_message_length = 0


def select_folder():
    """
	You can drag and drop a folder from Windows Explorer to the shell
	:return: a path to a folder
	"""
    f = input("Type or drop drop folder here\n -> ")
    if len(f) == 0:
        return ''
    print(f)
    return fixpath(f)


def get_files(folder):
    is_pdf = lambda f: f.lower().endswith('.pdf')
    is_tif = lambda f: f.lower().endswith('.tif')
    is_jpg = lambda f: f.lower().endswith('.jpg')

    full_list = []
    for dirname, dirnames, filenames in os.walk(folder):
        global last_message_length
        print('' * last_message_length + '\r', end='')
        last_message_length = len(dirname)
        print(dirname)

        filepaths = list(map(lambda f: join(dirname, f), filenames))
        full_list.extend(filepaths)

    pdfs = [f for f in full_list if is_pdf(f)]
    tifs = [f for f in full_list if is_tif(f)]
    jpgs = [f for f in full_list if is_jpg(f)]

    return jpgs, pdfs, tifs


def count_pdf(pdf):
    """
	Counts the pages in a PDF.
	:param pdf: The pdf.
	:return: The number of pages.
	"""

    with open(pdf, 'rb') as f:
        reader = PdfFileReader(f, strict=False)
        return reader.numPages


def count_tif(tif):
    """
	Counts the number of pages in a TIF.
	:param tif: The TIFF file.
	:return: The number of pages.
	"""
    count = 0
    with Image.open(tif) as image:
        count = image.n_frames
    return count


def count_pdf_list(files, timer):
    pages = 0
    docs = 0
    for f in tqdm(files):
        pages += count_pdf(f)
        docs += 1

    return len(files), pages


def count_tif_list(files, timer):
    pages = 0
    docs = 0
    for f in tqdm(files):
        pages += count_tif(f)
        docs += 1

    return docs, pages


def main():
    while (folder := select_folder()).strip() != '':
        print('_______________')
        jpgs, pdfs, tifs = get_files(folder)
        print(f'Found {len(jpgs)} JPG documents, {len(pdfs)} PDF documents, {len(tifs)} TIF documents. Counting pages...')
        timer = len(jpgs) + len(pdfs) + len(tifs)
        print()
        print(f'\nFolder: {folder}')

        if(len(jpgs) > 0):
            print('\nCounting JPGs')
            j_docs = len(jpgs)
        else:
            j_docs = 0

        if (len(pdfs) > 0):
            print('\nCounting PDFs')
            p_docs, p_pages = count_pdf_list(pdfs, timer)
        else:
            p_docs, p_pages = 0, 0

        if (len(tifs) > 0):
            print('\nCounting TIFFs')
            t_docs, t_pages = count_tif_list(tifs, timer)
        else:
            t_docs, t_pages = 0, 0

        print()
        print(f'\n\n{folder}: Totals:')
        print(f'\tJPG: {j_docs} documents, {j_docs} pages')
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
