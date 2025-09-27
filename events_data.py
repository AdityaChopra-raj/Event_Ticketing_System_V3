# --- Event Data Configuration ---

# Using local images in 'images' folder
# Make sure you have the images in the folder:
# images/navratri.jpeg, images/diwali.jpeg, images/freshers.jpeg, images/ravan.jpeg

BASE_IMAGE_PATH = "images/"

events = {
    "Navratri Dance Night": {
        "description": "Celebrate the nine nights of Navratri with Garba and Dandiya Raas! Featuring live music, traditional attire, and a massive dance floor.",
        "location": "University Main Ground / Community Hall A",
        "time": "Saturday, October 12, 2024, 7:00 PM onwards",
        "image": os.path.join(BASE_IMAGE_PATH, "navratri.jpeg"),
        "capacity": 200
    },
    "Diwali Fest & Dance": {
        "description": "The festival of lights celebration! Includes cultural performances, traditional sweet stalls, fireworks display, and a special DJ night for open dancing.",
        "location": "Campus Central Lawn",
        "time": "Friday, November 1, 2024, 6:00 PM",
        "image": os.path.join(BASE_IMAGE_PATH, "diwali.jpeg"),
        "capacity": 250
    },
    "Freshers Party": {
        "description": "Welcome the new batch! A night of music, introductions, talent showcases, and dinner to kick off the academic year. Theme: Neon Glow.",
        "location": "Auditorium Grand Ballroom",
        "time": "Friday, September 27, 2024, 8:00 PM",
        "image": os.path.join(BASE_IMAGE_PATH, "freshers.jpeg"),
        "capacity": 150
    },
    "Ravan Dehan Ceremony": {
        "description": "Witness the burning of the effigy of Ravana on Dussehra, symbolizing the victory of good over evil. Community fair and food vendors available.",
        "location": "Adjacent Football Field",
        "time": "Tuesday, October 15, 2024, 7:30 PM",
        "image": os.path.join(BASE_IMAGE_PATH, "ravan.jpeg"),
        "capacity": 300
    }
}

# For easier import in app.py and verify_ticket.py
events_data = events
