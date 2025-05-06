from tk_db_tool import message
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
message.set_message_handler(logger)
