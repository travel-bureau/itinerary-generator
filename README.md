# 🧭 Itinerary-to-PDF Generator

This script transforms structured itinerary input into a beautifully formatted PDF using ChatGPT and ReportLab. It intelligently caches responses to optimize performance and token usage.

---

## 📌 Description

This Python script accepts an itinerary in a specific structured format and performs the following steps:

1. **ChatGPT Integration**  
   The itinerary is sent to ChatGPT to generate a rich, descriptive travel narrative.

2. **PDF Generation with ReportLab**  
   The ChatGPT response is parsed and rendered into a styled PDF using the ReportLab library.

3. **MongoDB Storage**  
   The generated PDF is stored as a binary blob in MongoDB for persistent access and retrieval.

4. **Redis Caching**  
   To avoid redundant API calls and token usage, the script checks Redis for a cached ChatGPT response. If the same itinerary is submitted again, the cached response is reused to regenerate the PDF without invoking ChatGPT.

---

## ⚙️ Features

- 🔁 **Idempotent**: Duplicate itineraries reuse cached responses
- 🧠 **AI-powered**: Uses ChatGPT for natural language generation
- 🖨️ **PDF Output**: Clean, printable PDFs via ReportLab
- 💾 **MongoDB**: Stores PDFs as binary documents
- ⚡ **Redis**: Fast caching layer to reduce API calls and latency

---
# 🧪 Example Input

```json
{
  "trips": [
    {
      "id": 1,
      "trip_title": "Dubai - 6 Days Trip",
      "trip_dates": "03 Feb 2026 - 08 Feb 2026",
      "traveler_name": "Ashok",
      "pax": "6 Adults + 3 Children (7y, 3y & 1 infant)",
      "tour_costs": {
        "Adult": "Rs.48,500",
        "Child": "Rs.35,000",
        "Infant": "Rs.16,000"
      },
      "inclusions": [
        "5N stays at Hotel",
        "Daily Breakfast",
        "All entry tickets mentioned in itinerary",
        "Private Cabs for transfers",
        "Sightseeing as per itinerary",
        "All hotel taxes",
        "Visa Charges",
        "Tourist Dirham"
      ],
      "exclusions": [
        "Flight fare",
        "Meals other than mentioned",
        "Personal expenses",
        "Optional Activities"
      ],
      "destination": "Dubai",
      "itinerary_text": "Dubai - 6 Days Trip\n\nName: Ashok \nPax: 6 Adults + 3 Child (7, 3 year & 1 infant)\nDate: 03 Feb 2026 - 08 Feb 2026\n\nDay 1: Arrival at Sharjah Airport to Deira/ Bur Dubai Hotel + Half Day Dubai city tour + Dhow cruise marina with Dinner - Pvt.\nDay 2: Miracle Garden + Burj Khalifa 124th & 125th floor non-prime Hr. + Dubai Aquarium and Underwater Zoo - Pvt.\nDay 3: Ski Dubai - Snow plus + Standard Desert safari with BBQ dinner - Pvt.\nDay 4: Visit Global Village - Pvt.\nDay 5: Visit Dubai Frame + Dolphinarium and Seal Show. Departure from Deira/ Bur Dubai Hotel to DXB Airport"
    }
  ]
}
```

# 🚀 Coming Soon
🔒 PDF access tokens for secure downloads

📤 GCP integration for cloud-based PDF serving

📊 Admin dashboard for itinerary analytics

# 🧰 Requirements
Python 3.11+

openai, reportlab, pymongo, redis, python-dotenv
