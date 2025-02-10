
import os
import sys
import concurrent.futures
import concurrent
from tqdm import tqdm
from exceptions import BrokenImageException, TruncatedTiffException
from pypdf import PdfReader
from tifffile import TiffFile
import warnings
import logging
from tabulate import tabulate


def select_folder() -> str | None:
    """
    You can drag and drop a folders from Windows Explorer to the shell
    :return: The selected folder
    """
    f = input("Type or drop a single folder here\n\t -> ").replace('"', '').strip()
    if not os.path.isdir(f):
        return None
    return f


def get_files(parent_folder: str) ->(list[str], list[str], list[str]):
    """
    Find all JPG, PDF and TIFF files in the folder, and return a separate listing for each.
    Files can be nested in subfolders; all will be included in result.
    :param parent_folder: The folder containing the files
    :return: Three lists: JPGs, TIFFs and PDFs
    """
    full_list = []
    for folder, _, filenames in os.walk(parent_folder):
        files = list(map(lambda f: os.path.join(folder, f), filenames))
        full_list.extend(files)

    pdfs = [f for f in full_list if f.lower().endswith('.pdf')]
    jpgs = [f for f in full_list if f.lower().endswith('.jpg')]
    tifs = [f for f in full_list if f.lower().endswith('.tif')]

    return jpgs, pdfs, tifs


def count_pdf(pdf: str) -> int:
    """
    Counts the pages in a PDF.
    :param pdf: The pdf.
    :return: The number of pages.
    """
    try:
        with open(pdf, 'rb') as f:
            reader = PdfReader(f, strict=False)
            return reader.get_num_pages()
    except Exception as ex:
        raise BrokenImageException(pdf, ex)


def count_tif(tif: str) -> int:
    """
    Counts the number of pages in a TIF.
    :param tif: The TIFF file.
    :return: The number of pages.
    """

    # Convert specific warnings to exceptions
    warnings.filterwarnings('error')
    try:
        with TiffFile(tif) as image:
            return len(image.pages)
    except UserWarning as uw:
        # Handle the warning as an exception
        raise TruncatedTiffException(tif, str(uw))
    except Exception as ex:
        raise BrokenImageException(tif, ex)


def count_list(counter, files: list[str]) -> (int, int):
    """
    Counts the number of pages in a file list, using the provided single page counter function
    :param counter: A function capable of counting the pages in an individual file of that type
    :param files: A list of files whose pages are to be counted, using the provided counter function
    :return: both the document count and page count for the folders
    """

    pages = 0
    docs = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        pbar = tqdm(total=len(files))
        try:
            futures = {executor.submit(counter, f): f for f in files}
            for docs, future in enumerate(concurrent.futures.as_completed(futures)):
                pages += future.result()
                pbar.update(1)

            return docs, pages
        except BrokenImageException as ex:
            executor.shutdown(cancel_futures=True)
            raise ex


def process_folder(folder: str) -> None:
    """
    Count the JPG, PDF and TIFF files and pages in the folder. Page count PDF and multipage TIFFs.
    Tabulate document and page counts for each of the three types, as well as the totals.
    :param folder: The folder containing the files
    """
    jpgs, pdfs, tifs = get_files(folder)
    print(f'\nFound {len(jpgs)} JPG documents, {len(pdfs)} PDF documents, {len(tifs)} TIF documents. Counting pages...')

    if jpgs:
        print('\nCounting JPGs')
        j_docs = len(jpgs)
    else:
        j_docs = 0

    if pdfs:
        print('\nCounting PDFs')
        p_docs, p_pages = count_list(count_pdf, pdfs)
    else:
        p_docs, p_pages = 0, 0

    if tifs:
        print('\nCounting TIFFs')
        t_docs, t_pages = count_list(count_tif, tifs)
    else:
        t_docs, t_pages = 0, 0

    print()

    print(f'Totals for: "{folder}"')
    headings = ['Type', "Docs", "Pages"]
    j = ['JPG', j_docs, j_docs]
    p = ['PDF', p_docs, p_pages]
    t = ['TIF', t_docs, t_pages]
    tot = ['Total', j_docs + p_docs + t_docs, j_docs + p_pages + t_pages]
    # Adding ANSI escape code for bold text to the totals (works in terminal)
    tot = [f"\033[1m{x}\033[0m" for x in tot]
    headings = [f"\033[1m{x}\033[0m" for x in headings]
    print(tabulate([j, p, t, '', tot], headers=headings, tablefmt='simple_outline'))


def main():
    # Accept drag-and-drop folder as launch args
    args = sys.argv[1:]
    if args:
        process_folder(args[0])

    # Offer to repeat on another folder
    while  folder := select_folder():
        process_folder(folder)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(e)
    finally:
        input("Press Enter to exit\n")
        pass
