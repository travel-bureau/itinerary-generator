import re
from io import BytesIO
import random
from datetime import datetime
import emoji
import qrcode
from bs4 import BeautifulSoup
from markdown2 import markdown
from reportlab.graphics.barcode import code128
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, Spacer, KeepTogether, Image

from utils.unsplash_bot import fetch_image


# ======= QR Code =======
def generate_qr_code(data):
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def extract_toc_entries(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    toc = []
    line_no = 1

    for tag in soup.find_all(["h1", "h2", "h3"]):
        title = tag.get_text(strip=True)
        toc.append((line_no, title))
        line_no += 1

    return toc

def draw_random_watermarks(canvas, doc):
    canvas.saveState()
    canvas.setFillColorRGB(0.95, 0.95, 0.95)  # Light gray for subtle watermark
    canvas.setFont("Symbola", 50)

    emojis = ["✈", "🏝", "📸", "🌍", "🚗", "🗺", "🏨", "🍽",
              "🎒", "🚢", "🚂", "🚤", "🚃", "🚅", "🚁", "🛄"]

    for _ in range(random.randint(4, 6)):  # Draw 5 random objects
        emoji = random.choice(emojis)
        x = random.randint(50, int(doc.pagesize[0]) - 50)
        y = random.randint(100, int(doc.pagesize[1]) - 100)
        canvas.drawString(x, y, emoji)

    canvas.restoreState()

def draw_random_spaces(canvas, doc):
    canvas.saveState()
    canvas.setFillColorRGB(0.95, 0.95, 0.95)  # Light gray for subtle watermark
    canvas.setFont("Symbola", 50)

    emojis = [" ", "  ", "   ", "    ", "     ", "      ",
              "       ", "        ", "         "]
    for _ in range(random.randint(4, 6)):  # Draw 5 random objects
        emoji = random.choice(emojis)
        x = random.randint(50, int(doc.pagesize[0]) - 50)
        y = random.randint(100, int(doc.pagesize[1]) - 100)
        canvas.drawString(x, y, emoji)

    canvas.restoreState()

def draw_page_elements(canvas, doc):
    canvas.saveState()

    # --- Background color ---
    canvas.setFillColor(colors.HexColor("#FBFCF7"))
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], stroke=0, fill=1)

    # Watermarks
    draw_random_watermarks(canvas, doc)

    # Spaces
    draw_random_spaces(canvas, doc)

    # --- Header: Logo on left, Title on right ---
    canvas.setFont("Montserrat", 10)
    canvas.setFillColorRGB(0.2, 0.2, 0.2)

    # Logo image (top-left)
    logo_path = "logo/logo.png"
    logo_width = 120
    logo_height = 60
    logo_x = doc.leftMargin - 20
    logo_y = doc.height + doc.topMargin - 20

    canvas.drawImage(
        logo_path,
        logo_x,
        logo_y,
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True,
        mask='auto'
    )

    # Title (top-right)
    canvas.setFont("FacultyGlyphic", 15)
    canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin + 5, "Trip Itinerary")

    # --- Footer ---
    canvas.setFont("FiraSans", 8)
    canvas.setFillColorRGB(0.4, 0.4, 0.4)
    canvas.drawString(doc.leftMargin, 10, "www.travel-bureau.com | enjoy@travel-bureau.com")
    canvas.drawRightString(doc.width + doc.leftMargin, 10, f"Page {canvas.getPageNumber()}")

    # --- Diagonal Watermark ---
    canvas.saveState()
    canvas.setFont("FiraSans", 86)
    canvas.setFillColorRGB(0.95, 0.95, 0.95)

    # Move to center of page
    x = doc.leftMargin + doc.width / 2
    y = doc.bottomMargin + doc.height / 2
    canvas.translate(x, y)

    # Rotate canvas
    canvas.rotate(45)

    # Draw watermark at origin
    canvas.drawCentredString(0, 0, "TRAVEL BUREAU")
    canvas.restoreState()

    # --- Border (tight to page edges) ---
    canvas.setStrokeColorRGB(0.85, 0.85, 0.85)
    canvas.setLineWidth(0.5)
    canvas.rect(
        doc.leftMargin - 10,
        doc.bottomMargin - 10,
        doc.width + 20,
        doc.height + 20
    )

    canvas.restoreState()

def extract_day_titles(itinerary_text):
    day_titles = []

    # Match lines starting with "Day X:" (X = 1–99)
    day_pattern = re.compile(r"^Day\s+\d+:\s+.*", re.IGNORECASE)

    for line in itinerary_text.splitlines():
        line = line.strip()
        if day_pattern.match(line):
            day_titles.append(line)

    return day_titles

def render_traveler_info_block(raw_html, styles):
    emoji_map = {
        "Primary Traveller Name": "✎",
        "Travelers": "👤",
        "Travel Dates": "⏰"
    }

    soup = BeautifulSoup(raw_html, "html.parser")
    rows = []
    current_key = None

    for element in soup.contents:
        if isinstance(element, str):
            if current_key:
                value = element.strip(" :-\n")
                if value and current_key in emoji_map:
                    label = f"{emoji_map.get(current_key, '')} {current_key}".strip()
                    rows.append([
                        Paragraph(label, styles["EmojiText"]),
                        Paragraph(value, styles["EmojiText"])
                    ])
                current_key = None

        elif element.name == "b":
            current_key = element.get_text(strip=True).rstrip(":")

        else:
            if current_key:
                value = element.get_text(strip=True)
                if value and current_key in emoji_map:
                    label = f"{emoji_map.get(current_key, '')} {current_key}".strip()
                    rows.append([
                        Paragraph(label, styles["EmojiText"]),
                        Paragraph(value, styles["EmojiText"])
                    ])
                current_key = None

    if not rows:
        return Paragraph(soup.get_text(strip=True), styles["NormalText"])

    table = Table(rows, colWidths=[140, 280])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), styles["NormalText"].fontName),
        ("FONTSIZE", (0, 0), (-1, -1), styles["NormalText"].fontSize),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    return table

def render_cost_info_block(tour_costs, styles, max_width=420):
    if not tour_costs:
        return Paragraph("No cost information available.", styles["NormalText"])

    # Emoji-coded header
    rows = [[
        Paragraph("👤 Entity", styles["EmojiText"]),
        Paragraph("💰 Cost", styles["EmojiText"])
    ]]

    # Add each cost row
    for role, cost in tour_costs.items():
        rows.append([
            Paragraph(role, styles["EmojiText"]),
            Paragraph(cost, styles["EmojiText"])
        ])

    # Responsive column widths
    col_widths = [max_width * 0.45, max_width * 0.55]

    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), styles["NormalText"].fontName),
        ("FONTSIZE", (0, 0), (-1, -1), styles["NormalText"].fontSize),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ]))

    return table

def themed_heading(text, THEME_COLOR):
    return f'<font color="{THEME_COLOR}"><b>{text}</b></font>'

def sanitize_html_for_pdf(markdown_text):
    # Step 1: Convert Markdown to HTML
    html = markdown(markdown_text, extras=["fenced-code-blocks", "tables", "strike", "target-blank-links"])

    # Step 2: Replace unsupported tags
    html = html.replace("<strong>", "<b>").replace("</strong>", "</b>")
    html = html.replace("<em>", "<i>").replace("</em>", "</i>")

    # Step 3: Replace emojis with safe symbols
    emoji_map = {
        "📋": "✎", "🌟": "★", "📅": "⏰", "🧑": "👤", "👥": "👤 x2",
        "🔗": "⇱", "🌐": "⛶", "🗓": "⏰", "📧": "✉", "📞": "☎", "✅": "✓", "❌": "✗"
    }
    html = emoji.replace_emoji(html, replace=lambda e, pos: emoji_map.get(e, f"[{e}]"))

    # Step 4: Clean up spacing and unsupported tags
    soup = BeautifulSoup(html, "html.parser")

    # Remove unsupported tags like <span>, <div>
    for tag in soup.find_all(["span", "div"]):
        tag.unwrap()

    # Optional: remove empty tags
    for tag in soup.find_all():
        if not tag.get_text(strip=True):
            tag.decompose()

    return str(soup)

def fix_inline_spacing(html):
    # Add space before and after <b> and </b> if needed
    html = re.sub(r'(?<!\s)<b>', ' <b>', html)
    html = re.sub(r'</b>(?!\s)', '</b> ', html)

    # Same for <i>
    html = re.sub(r'(?<!\s)<i>', ' <i>', html)
    html = re.sub(r'</i>(?!\s)', '</i> ', html)

    return html

def tighten_bold_punctuation(html):
    # Move trailing punctuation into <b> tags
    return re.sub(r'<b>([^<]+?)</b>([.,!?])', r'<b>\1\2</b>', html)

def html_to_story(html_text, styles):
    soup = BeautifulSoup(html_text, "html.parser")
    story = []
    section_seen = set()

    def is_duplicate(text):
        return text.strip().lower() in section_seen

    def mark_seen(text):
        section_seen.add(text.strip().lower())

    def add_paragraph(text, style):
        text = fix_inline_spacing(text)
        if not text or is_duplicate(text):
            return False
        mark_seen(text)
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 10))
        return True

    def render_note_inline(text, styles):
        # Replace 'note:' with emoji-styled phrase inline
        styled_note = '<font name="Symbola"><b>📒: </b></font>'
        updated = re.sub(r"(?i)\bnote:", styled_note, text)
        story.append(Paragraph(updated, styles["NormalText"]))
        story.append(Spacer(1, 10))

    checklist_started = False

    # --- Step 3: Render day-wise details ---
    for elem in soup.find_all(["p", "ul", "ol", "blockquote"]):
        lines = elem.get_text().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip top fields
            if line.startswith("Travel Itinerary:") or any(
                    line.startswith(prefix) for prefix in [
                        "Primary Traveller Name:", "Travel Dates:", "Travelers:"
                    ]
            ):
                continue

            clean_line = line.lstrip("-").strip()

            # Day heading
            if re.match(r"^Day\s+\d+:", line):
                section_seen.clear()
                add_paragraph(f"<b>{line}</b>", styles["DayHeading"])

            # Time-wise split
            elif re.match(r"^(Morning|Afternoon|Evening|Night|Early Morning|Early Afternoon|Late Afternoon|All Day|"
                          r"Full Day|Morning till Evening|Late Evening|All day|Late Night):", clean_line, re.IGNORECASE):
                match = re.match(r"^-?\s*(Morning|Afternoon|Evening|Night|Early Morning|Early Afternoon|Late Afternoon|All Day|"
                                 r"Full Day|Morning till Evening|Late Evening|All day|Late Night):\s*(.*)", clean_line, re.IGNORECASE)
                if match:
                    time_label_raw = match.group(1).strip().title() + ":"
                    description = match.group(2).strip()

                    emoji_map = {
                        "Morning:": "🌄",
                        "Early Morning:": "🌄",
                        "Afternoon:": "🌞",
                        "Early Afternoon:": "🌅",
                        "Evening:": "🌆",
                        "Late Evening:": "🌃",
                        "Night:": "🌠",
                        "Late Afternoon:": "🫖",
                        "Late Night:": "🌌",
                        "All Day:": "📆",
                        "Full Day:": "📅",
                        "Morning Till Evening:": "🌕"
                    }
                    emoji = emoji_map.get(time_label_raw, "🕒")
                    time_text = f"<b>{emoji} {time_label_raw}</b>"

                    add_paragraph(time_text, styles["EmojiText"])
                    if description:
                        add_paragraph(description, styles["NormalText"])

            # Time-range label split
            elif re.match(
                    r"^(Morning|Afternoon|Evening|Night|All Day|Full day)"
                    r"(\s*(to|&|and)\s*(Morning|Afternoon|Evening|Night|All Day|Full day))?:\s*(.*)",
                    clean_line,
                    re.IGNORECASE
            ):
                match = re.match(
                    r"^(Morning|Afternoon|Evening|Night|All Day|Full day)"
                    r"(\s*(to|&|and)\s*(Morning|Afternoon|Evening|Night|All Day|Full day))?:\s*(.*)",
                    clean_line,
                    re.IGNORECASE
                )
                if match:
                    first_label = match.group(1).strip().title()
                    connector = match.group(3)
                    second_label = match.group(4).strip().title() if match.group(4) else None
                    description = match.group(5).strip()

                    if second_label:
                        time_range = f"{first_label} {connector} {second_label}"
                    else:
                        time_range = first_label

                    emoji = "🕒"
                    time_text = f"<b>{emoji} {time_range}:</b>"

                    add_paragraph(time_text, styles["EmojiText"])
                    if description:
                        add_paragraph(description, styles["NormalText"])

            # Accommodation split
            elif re.match(r"^(Accommodation):", clean_line, re.IGNORECASE):
                match = re.match(r"^-?\s*(Accommodation):\s*(.*)", clean_line, re.IGNORECASE)
                if match:
                    time_label_raw = match.group(1).strip().title() + ":"
                    description = match.group(2).strip()

                    emoji_map = {
                        "Accommodation:": "🏘"
                    }
                    emoji = emoji_map.get(time_label_raw, "🕒")
                    time_text = f"<b>{emoji} {time_label_raw}</b>"

                    add_paragraph(time_text, styles["EmojiText"])
                    if description:
                        add_paragraph(description, styles["NormalText"])

            # Day wise highlights summary
            elif re.match(r"^day[-\s]?wise.*:", clean_line, re.IGNORECASE):
                continue

            # Time wise split summary
            elif re.match(r"^time[-\s]?wise.*:", clean_line, re.IGNORECASE) or \
                    re.match(r"^time[-\s]?split.*:", clean_line, re.IGNORECASE):
                continue

            # Highlights
            elif clean_line.lower().startswith("highlight") or \
                    clean_line.lower().startswith("day highlight") or \
                    clean_line.lower().startswith("day-highlight"):
                highlight_text = line.split(":", 1)[1].strip()
                add_paragraph(f"<i>📸 Highlight:</i>", styles["EmojiText"])
                if highlight_text:
                    add_paragraph(highlight_text, styles["NormalText"])

            # Travel Tips
            elif clean_line.lower().startswith("travel tip") or \
                    clean_line.lower().startswith("tip"):
                tip_text = line.split(":", 1)[1].strip()
                add_paragraph(f"<i>💡 Travel Tips:</i>", styles["EmojiText"])
                if tip_text:
                    add_paragraph(tip_text, styles["NormalText"])

            # Local Experience
            elif clean_line.lower().startswith("local experience"):
                experience_text = line.split(":", 1)[1].strip()
                add_paragraph(f"<i>🎯 Local Experience:</i>", styles["EmojiText"])
                if experience_text:
                    add_paragraph(experience_text, styles["NormalText"])

            # Checklist heading
            elif clean_line.lower().startswith("packaging checklist"):
                section_seen.clear()
                story.append(PageBreak())
                add_paragraph(f"<b>Packaging Checklist</b>", styles["DayHeading"])
                checklist_started = True

            # Checklist items
            elif checklist_started and line.startswith("-"):
                item = line.lstrip("-").strip()
                add_paragraph(f"• {item}", styles["NormalText"])

            # Blockquote
            elif elem.name == "blockquote":
                add_paragraph(f"<i>{line}</i>", styles["SmallText"])

            # Check for notes
            elif "note:" in line.lower():
                item = line.lstrip("-").strip()
                render_note_inline(item, styles)

            # Fallback
            else:
                item = line.lstrip("-").strip()
                add_paragraph(item, styles["NormalText"])

        # Handle <ul> and <ol> separately
        if checklist_started and elem.name == "ul":
            for li in elem.find_all("li"):
                li_text = li.get_text(strip=True)
                add_paragraph(f"• {li_text}", styles["NormalText"])

        elif elem.name == "ol":
            for i, li in enumerate(elem.find_all("li"), start=1):
                li_text = li.get_text(strip=True)
                add_paragraph(f"{i}. {li_text}", styles["NormalText"])

    return story

def render_summary_section(story, styles, tour_costs, inclusions, exclusions, contact_info, qr_buffer, doc, link_style):
    story.append(PageBreak())
    story.append(Paragraph("Summary & Contact", styles["CenterHeading"]))
    story.append(Spacer(1, 16))

    # --- Tour Costs Table ---
    story.append(Spacer(1, 12))
    story.append(render_cost_info_block(tour_costs, styles, max_width=doc.width))
    story.append(Spacer(1, 12))

    # --- Inclusions & Exclusions ---
    def render_bullet_list(title, items, emoji):
        story.append(Paragraph(f"<b>{emoji} {title}</b><br />", styles["EmojiText"]))
        for item in items:
            story.append(Paragraph(f"• {item}", styles["NormalText"]))
        story.append(Spacer(1, 8))

    render_bullet_list("Inclusions", inclusions, "✓")
    render_bullet_list("Exclusions", exclusions, "✗")

    # --- Contact Info ---
    render_contact_table(story, contact_info, link_style)
    story.append(Spacer(1, 12))

    # --- QR Code ---
    qr_block = KeepTogether([
        Paragraph("🔗 Scan to visit website", styles["EmojiText"]),
        Spacer(1, 6),
        Image(qr_buffer, width=1.5*inch, height=1.5*inch)
    ])

    story.append(qr_block)

def get_barcode_metadata(doc):
    # --- Barcode metadata ---
    traveler = getattr(doc, "traveler_name", "Unknown")
    destination = getattr(doc, "destination", "Unknown")
    barcode_time = "ITIN-" + datetime.now().strftime("%Y%m%d%H%M%S")
    barcode_data = f"{traveler}_{destination}_{barcode_time}".replace(" ", "_")
    return barcode_data

def format_tel_link(phone_number):
    # Remove all non-digit characters except leading +
    digits = re.sub(r"[^\d]", "", phone_number)
    if phone_number.startswith("+"):
        return f"tel:+{digits}"
    return f"tel:{digits}"

def render_contact_table(story, contact_info, link_style):
    phone_link = format_tel_link(contact_info["phone"])
    contact_rows = [
        ["☎ Phone", Paragraph(f'<a href="{phone_link}">{contact_info["phone"]}</a>', link_style)],
        ["📧 Email", Paragraph(f'<a href="mailto:{contact_info["email"]}">{contact_info["email"]}</a>', link_style)],
        ["🌐 Website", Paragraph(f'<a href="https://{contact_info["website"]}">{contact_info["website"]}</a>', link_style)],
    ]

    contact_table = Table(contact_rows, colWidths=[100, 200])
    contact_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Symbola"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(contact_table)

def draw_summary_page(canvas, doc):
    # Draw shared header, logo, footer
    draw_page_elements(canvas, doc)

    # Draw summary-specific elements (e.g. motto)
    canvas.saveState()
    canvas.setFont("FiraSans-Italic", 6)
    canvas.setFillColorRGB(0.4, 0.4, 0.4)
    motto = "Travel Bureau guarantees absolutely smooth & hassle free holidays worldwide"
    canvas.drawRightString(doc.leftMargin + doc.width, doc.bottomMargin - 5, motto)

    # --- Barcode metadata ---
    barcode_metadata = get_barcode_metadata(doc)
    doc.barcode_metadata = barcode_metadata

    # --- Generate barcode with narrow width and tall height ---
    barcode = code128.Code128(barcode_metadata, barHeight=30, barWidth=0.6)

    # --- Rotate canvas to draw vertically at bottom-right ---
    canvas.translate(doc.leftMargin + doc.width + 10, doc.bottomMargin)
    canvas.rotate(90)
    barcode.drawOn(canvas, 0, 0)

    canvas.restoreState()

def add_coverpage(doc, story, image_flag=False):
    if image_flag:
        cover_image = fetch_image(doc.destination)

        # Optional: scale image to fit page width
        image_width = doc.width
        image_height = image_width * 0.6  # Adjust aspect ratio as needed

        story.append(Image(cover_image, width=image_width, height=image_height))
        story.append(Spacer(1, 24))  # Breathing room below image

        # Calculate vertical space to center the block
        block_height = 600  # Approximate height of your content block
        available_height = doc.height
        top_padding = (available_height - block_height) / 2
    else:
        # Calculate vertical space to center the block
        block_height = 200  # Approximate height of your content block
        available_height = doc.height
        top_padding = (available_height - block_height) / 2

    story.append(Spacer(1, top_padding))

    return story

def build_pdf_local(doc, story, pdf_path):
    # ---- Build PDF ----
    doc.build(story)
    print(f"PDF generated at: {pdf_path}")

    # Read PDF binary
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

def build_pdf_memory(doc, story):
    # ---- Build PDF in memory----
    # Create an in-memory buffer
    pdf_buffer = BytesIO()

    # Build the PDF into the buffer
    doc.build(story, filename=pdf_buffer)

    # Get the PDF bytes
    pdf_bytes = pdf_buffer.getvalue()

    # Optional: close the buffer
    pdf_buffer.close()

    return pdf_bytes