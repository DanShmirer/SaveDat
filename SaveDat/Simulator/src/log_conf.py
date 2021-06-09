from constants import *

log_format = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s  %(message)s')

def Create_logger(name, log_file, level=logging.INFO):


    f_handler = logging.FileHandler(log_file)
    f_handler.setFormatter(log_format)
    
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(f_handler)
    
    # Create handlers
    #c_handler = logging.StreamHandler()
    
    #c_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    #c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    
    #c_handler.setFormatter(c_format)
    
    
    # Add handlers to the logger
    #logger.addHandler(c_handler)
    
    #logger.info('This is a warning')
    #logger.info('This is an error')
    
    return logger