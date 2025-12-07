import os
from datetime import datetime, UTC

from pymongo import MongoClient


def initialize_mongodb():
    global db, collection, PDF_RERENDER_DIR
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    collection = db[os.getenv("MONGODB_COLLECTION_NAME")]
    PDF_RERENDER_DIR = "pdfs_from_db"
    os.makedirs(PDF_RERENDER_DIR, exist_ok=True)

def load_data_to_mongodb(barcode_data, traveler_name, destination, trip_title, trip_dates, pdf_bytes):
    # Prepare metadata
    record = {
        "barcode_id": barcode_data,
        "traveler_name": traveler_name,
        "destination": destination,
        "trip_title": trip_title,
        "trip_dates": trip_dates,
        "created_at": datetime.now(UTC),
        "pdf_data": pdf_bytes  # Stored as binary
    }

    # Insert into MongoDB
    return collection.insert_one(record)

def fetch_pdf_from_mongodb(barcode_id):
    record = collection.find_one({"barcode_id": barcode_id})

    if not record:
        raise ValueError(f"No PDF found for barcode_id: {barcode_id}")

    # Extract metadata
    destination = record.get("destination", "Itinerary").replace(" ", "_")
    trip_dates = record.get("trip_dates", "")
    start_date, end_date = trip_dates.split("-") if "-" in trip_dates else ("Unknown", "Unknown")
    start_date = start_date.strip().replace(" ", "")
    end_date = end_date.strip().replace(" ", "")

    # Build filename
    pdf_file_name = f"{destination}_{start_date}_{end_date}_reprint.pdf"
    pdf_path = os.path.join(PDF_RERENDER_DIR, pdf_file_name)

    pdf_bytes = record["pdf_data"]

    # Write to file
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"PDF re-rendered at: {pdf_path}")

def delete_all_documents():
    collections = db.list_collection_names()
    for name in collections:
        result = db[name].delete_many({})
        print(f"🧹 Cleared {result.deleted_count} documents from '{name}'")

    print("✅ All collections emptied.")