all = ["Errors"]

from dataclasses import dataclass

@dataclass
class Errors:
    INVALID_COMMAND: str = "Invalid command. Please check the usage and try again."
    LOW_PERMISSIONS: str = "Sorry, you do not have the necessary permissions to use this command."
    ERROR: str = "An error occurred while processing your request. Please try again later."
    INVALID_INPUT: str = "Invalid input. Please check your input and try again."
    FEATURE_LOCKED: str = "Sorry, this feature is currently unavailable. Please try again later."
    INVALID_PARAMS: str = "Invalid parameters provided. Please check the usage and try again.",
    FUNCTION_LOCKED: str = "Sorry, the function is not available, please check you are using the right version of the bot",
    COOLDOWN: str = "You have reached the maximum number of requests for this function.",
    BUG: str = "An unexpected error occurred. Our team has been notified and will fix the problem as soon as possible.",
    LOW_PERMISSIONS: str = "You are not authorized to perform this action.",
    USER_NOT_FOUND: str = "Error: User not found.",
    CHANNEL_NOT_FOUND: str = "Error: Channel not found.",
    SERVER_NOT_FOUND: str = "Error: Server not found.",
    DISCONNECTED_DATABASE: str = "Error: Unable to connect to the database.",
    FAILED_TO_SAVE_DATA: str = "Error: Failed to save data.",
    FAILED_TO_RETRIEVE_DATA: str = "Error: Failed to retrieve data.",
    INVALID_FILE_FORMAT: str = "Error: Invalid file format.",
    INVALID_FILE_SIZE: str = "Error: File size exceeded the maximum limit."