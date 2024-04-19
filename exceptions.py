class BrokenImageException(Exception):
    def __init__(self, image, ex):
        message = f'\nError: Unable to process image {image}. Message: {str(ex)}'
        super().__init__(message)


class TruncatedTiffException(BrokenImageException):
    def __init__(self, image, ex):
        message = f'\nERROR: Unable to process image {image}. Message: {str(ex)}'
        super().__init__(message)
