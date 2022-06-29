from PyPDF2 import PdfFileReader as Reader
from pathlib import Path
import os
import sys
import concurrent.futures
import concurrent
from PIL import Image
from tqdm import tqdm
from exceptions import BrokenImageException

from PyPDF2 import PdfFileReader

fixpath = lambda path: str(Path(path.replace('"', '').strip()))
join = lambda dir, file: fixpath(os.path.join(dir, file))


def select_folder():
    """
    You can drag and drop a folder from Windows Explorer to the shell
    :return: whatever the user inputs, hopefully a directory
    """
    args = sys.argv[1:]
    if len(args) > 0:
        return fixpath(args[0])

    f = input("Type or drop folder here\n\t -> ")
    if len(f) == 0:
        return ''
    return fixpath(f)


def get_files(parent_folder):
    is_pdf = lambda f: f.lower().endswith('.pdf')
    is_tif = lambda f: f.lower().endswith('.tif')
    is_jpg = lambda f: f.lower().endswith('.jpg')

    full_list = []
    for folder, _, filenames in os.walk(parent_folder):
        sys.stdout.write("\033[K")
        print(folder, end='\r')

        files = list(map(lambda f: join(folder, f), filenames))
        full_list.extend(files)

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
    try:
        with open(pdf, 'rb') as f:
            reader = PdfFileReader(f, strict=False)
            return reader.numPages
    except Exception as ex:
        raise BrokenImageException(pdf, ex)


def count_tif(tif):
    """
    Counts the number of pages in a TIF.
    :param tif: The TIFF file.
    :return: The number of pages.
    """
    try:
        with Image.open(tif) as image:
            return image.n_frames
    except Exception as ex:
        raise BrokenImageException(tif, ex)


def count_list(counter, files):
    """
    Counts the number of pages in a file list, using the provided single page counter function
    :param counter: A function capable of counting the pages in an individual file of that type
    :param files: A list of files whose pages are to be counted, using the provided counter function
    :return: both the document count and page count for the folder
    """

    pages = 0
    docs = 0
    with concurrent.futures.ThreadPoolExecutor(8) as executor:
        futures = []
        pbar = tqdm(total=len(files))
        for f in files:
            future = executor.submit(counter, f)
            futures.append(future)

        for f in concurrent.futures.as_completed(futures):
            pages += f.result()
            docs += 1
            pbar.update(1)

        return docs, pages


def main():
    while (folder := select_folder()).strip() != '':

        if not os.path.isdir(folder):
            print('\nThat\'s not a real folder!\n')
            continue

        jpgs, pdfs, tifs = get_files(folder)
        print(
            f'\nFound {len(jpgs)} JPG documents, {len(pdfs)} PDF documents, {len(tifs)} TIF documents. Counting pages...')

        if len(jpgs) > 0:
            print('\nCounting JPGs')
            j_docs = len(jpgs)
        else:
            j_docs = 0

        if len(pdfs) > 0:
            print('\nCounting PDFs')
            p_docs, p_pages = count_list(count_pdf, pdfs)
        else:
            p_docs, p_pages = 0, 0

        if len(tifs) > 0:
            print('\nCounting TIFFs')
            t_docs, t_pages = count_list(count_tif, tifs)
        else:
            t_docs, t_pages = 0, 0

        print()
        print(f'\n\n{folder}: Totals:')
        print(f'\tJPG: {j_docs} documents, {j_docs} pages')
        print(f'\tPDF: {p_docs} documents, {p_pages} pages')
        print(f'\tTIF: {t_docs} documents, {t_pages} pages')
        print(f'\n\tTot: \
{j_docs + p_docs + t_docs} documents, \
{j_docs + p_pages + t_pages} pages\n')
        print('---------------------------------------------\n')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(str(e))
    finally:
        input("Press Enter to exit\n")
        pass
