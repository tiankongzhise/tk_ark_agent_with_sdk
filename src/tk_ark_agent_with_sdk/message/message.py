from tk_db_tool import message
import logging


logger = logging.getLogger(__name__)
message.set_message_handler(logger)
