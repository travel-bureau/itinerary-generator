import asyncio
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, PageBreak, NextPageTemplate
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
import re

from utils.chatgpt_bot import initialize_chatgpt, enhance_itinerary_with_chatgpt
from utils.mongodb_bot import initialize_mongodb, load_data_to_mongodb
from utils.redis_bot import initialize_redis
from utils.reportlab_bot import generate_qr_code, draw_page_elements, \
    sanitize_html_for_pdf, tighten_bold_punctuation, html_to_story, \
    add_coverpage, render_summary_section, draw_summary_page, build_pdf_local, build_pdf_memory
from utils.styles import register_styles
from utils.unsplash_bot import initialize_unsplash

load_dotenv()

initialize_redis()
initialize_mongodb()
initialize_unsplash()
initialize_chatgpt()

emoji_style, link_style, heading_style, sub_heading_style, day_style, normal_style, small_style, THEME_COLOR, EMOJI_COLOR = register_styles()

# ======= Configuration =======
CACHE_DIR = "cache"
IMAGE_CACHE_DIR = os.path.join(CACHE_DIR, "images")
CHATGPT_CACHE_FILE = os.path.join(CACHE_DIR, "chatgpt_cache.json")
PDF_OUTPUT_DIR = "generated_pdfs"
PDF_RERENDER_DIR = "pdfs_from_db"
PLACEHOLDER_IMAGE = BytesIO(requests.get("https://images.unsplash.com/photo-1559311648-d46f5d8593d6?q=80&w=3500&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D").content)

# Create necessary directories
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# ======= PDF Generation =======
def create_itinerary_pdf(itinerary_text, trip_title, trip_dates, traveler_name, pax_details, tour_costs, inclusions, exclusions, contact_info, destination=None, source="local", cache_flag=True):
    detailed_itinerary = enhance_itinerary_with_chatgpt(itinerary_text, cache_flag=cache_flag)

    # Generate PDF file name
    if destination:
        safe_dest = destination.replace(' ', '_')
        start_date, end_date = trip_dates.split('-')
        start_date = start_date.strip().replace(' ', '')
        end_date = end_date.strip().replace(' ', '')
        pdf_file_name = f"{safe_dest}_{start_date}_{end_date}.pdf"
    else:
        pdf_file_name = f"Itinerary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(PDF_OUTPUT_DIR, pdf_file_name)

    doc = BaseDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id='normal',
        showBoundary=0  # Set to 1 if you want visible frame borders
    )
    template = PageTemplate(id='main', frames=[frame], onPage=draw_page_elements)
    doc.addPageTemplates([template])

    # Define a frame for the summary page
    summary_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='summary')

    # Register the summary page template with your custom draw function
    summary_template = PageTemplate(id='SummaryPage', frames=[summary_frame], onPage=draw_summary_page)

    # Add it to the document
    doc.addPageTemplates([summary_template])

    styles = getSampleStyleSheet()
    styles.add(emoji_style)
    styles.add(heading_style)
    styles.add(sub_heading_style)
    styles.add(day_style)
    styles.add(normal_style)
    styles.add(small_style)
    story = []

    # Add metadata for barcode
    doc.traveler_name = traveler_name
    doc.destination = destination

    # ---- Cover Page ----
    story = add_coverpage(doc, story, image_flag=False)

    story.append(Paragraph(f"<b>{trip_title}</b>", styles["CenterHeading"]))
    story.append(Paragraph(f"Dates: {trip_dates}", styles["CenterHeading"]))
    story.append(Paragraph(f"Traveler: {traveler_name}", styles["CenterHeading"]))
    story.append(Paragraph(f"Pax: {pax_details}", styles["CenterHeading"]))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Powered by Travel Bureau", styles["CenterHeading"]))
    story.append(PageBreak())

    # ---- Itinerary Pages ----
    safe_html = sanitize_html_for_pdf(detailed_itinerary)
    safe_html = tighten_bold_punctuation(safe_html)
    story.extend(html_to_story(safe_html, styles))

    # ---- Summary Page ----
    story.append(NextPageTemplate("SummaryPage"))
    qr_buffer = generate_qr_code(contact_info['website'])
    render_summary_section(story, styles, tour_costs, inclusions, exclusions, contact_info, qr_buffer, doc, link_style)

    if source == "local":
        build_pdf_local(doc, story, pdf_path)

    pdf_bytes = build_pdf_memory(doc, story)

    barcode_metadata = getattr(doc, "barcode_metadata", None)
    mongo_res = load_data_to_mongodb(barcode_metadata, traveler_name, destination, trip_title, trip_dates, pdf_bytes)
    print(f"PDF data for {traveler_name} with destination {destination} loaded to mongodb for future reference!")
    return mongo_res

async def run_bot(request=None, source="local"):
    return await main(request, source)

def trigger(request):
    return asyncio.run(run_bot(request, source="gcp"))

# ======= Example Usage =======
async def main(request=None, source="local", cache_flag=True):
    print(source)
    itinerary_data = {}
    request_data = {}
    mongo_id = None
    if not request:
        with open("data/itineraries.json", "r", encoding="utf-8") as f:
            itinerary_data = json.load(f)
    else:
        # TODO: Process request and prepare itinerary_data
        try:
            request_data = request.get_json(silent=True)
            itinerary_data = request_data

        except Exception as e:
            print(f"⚠️ Error: {e}")
            return "❌ Failed to process request!", 500

    if itinerary_data:
        with open("data/contact.json", "r", encoding="utf-8") as f:
            contact_info = json.load(f)

        for trip in itinerary_data["trips"]:
            trip_id = trip["id"]
            trip_title = trip["trip_title"]
            trip_dates = trip["trip_dates"]
            traveler_name = trip["traveler_name"]
            pax_details = trip["pax"]
            tour_costs = trip["tour_costs"]
            inclusions = trip["inclusions"]
            exclusions = trip["exclusions"]
            destination = trip["destination"]
            itinerary_text = trip["itinerary_text"]
            # ✅ use .get() with default True
            cache_flag = trip.get("useCache", True)

            print(f"""
🧳 Trip Summary
────────────────────────────────────────────
📌 Trip ID       : {trip_id}
📍 Title         : {trip_title}
📅 Dates         : {trip_dates}
👤 Traveler      : {traveler_name}
👥 Pax Details   : {pax_details}
🌍 Destination   : {destination}

💰 Tour Costs
{chr(10).join([f"  - {entity}: {cost}" for entity, cost in tour_costs.items()])}

✅ Inclusions
{chr(10).join([f"  - {item}" for item in inclusions])}

❌ Exclusions
{chr(10).join([f"  - {item}" for item in exclusions])}

📝 Itinerary
────────────────────────────────────────────
{itinerary_text}

🧾 Use Cache     : {cache_flag}
""")

            # Generate PDF
            res = create_itinerary_pdf(
                itinerary_text,
                trip_title,
                trip_dates,
                traveler_name,
                pax_details,
                tour_costs,
                inclusions,
                exclusions,
                contact_info,
                destination,
                source=source,
                cache_flag=cache_flag
            )

            mongo_id = re.search(r"ObjectId\('([a-f0-9]{24})'\)", str(res)).group(1)
            print(mongo_id)
    return mongo_id


if __name__ == "__main__":
    asyncio.run(run_bot())
