class BrokenImageException(Exception):
    def __init__(self, image, ex):
        message = f'Unable to process image {image}. Message: {str(ex)}'
        super().__init__(message)