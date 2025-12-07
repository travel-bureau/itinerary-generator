from dotenv import load_dotenv

from utils.mongodb_bot import delete_all_documents, initialize_mongodb

load_dotenv()
initialize_mongodb()
delete_all_documents()