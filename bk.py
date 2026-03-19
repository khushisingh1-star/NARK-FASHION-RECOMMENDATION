from flask import Flask, request, jsonify, render_template
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='../templates')

# --- Color Palettes ---
COLOR_PALETTES = {
    "Casual": {
        "T-Shirt and Jeans": ["Blue", "Gray", "White", "Black", "OliveGreen", "SkyBlue", "DenimBlue"],
        "Polo and Chinos": ["Khaki", "Navy", "LightBlue", "Burgundy", "Teal", "Beige", "Rust"],
        "Hoodie and Joggers": ["Gray", "Black", "Navy", "Maroon", "Charcoal", "ForestGreen", "SlateGray"],
        "Flannel and Jeans": ["Red", "Black", "Navy", "Green", "Brown", "Mustard", "Cream"],
        "Denim Jacket and T-Shirt": ["Blue", "White", "Black", "Gray", "Olive"],
    },
    "Formal": {
        "Suit and Tie": {
            "Men": [["Black", "White", "Black"], ["Navy", "White", "Navy"], ["Gray", "LightBlue", "Gray"],
                    ["Charcoal", "White", "Silver"], ["MidnightBlue", "White", "RoyalBlue"]],
            "Women": [["Black", "Ivory", "Black"], ["Navy", "White", "Navy"], ["Gray", "LightPink", "Gray"],
                    ["Burgundy", "Cream", "Gold"], ["Teal", "Silver", "Black"]],
        },
        "Blazer and Dress Pants/Skirt": {
            "Men": [["Navy", "White", "Gray"], ["Gray", "LightBlue", "Black"], ["Brown", "LightYellow", "Brown"],
                    ["Olive", "Cream", "Khaki"], ["Charcoal", "SkyBlue", "Black"]],
            "Women": [["Black", "Ivory", "Black"], ["Burgundy", "Black", "Burgundy"],
                    ["ForestGreen", "Beige", "DarkBrown"],
                    ["Navy", "White", "Silver"], ["Plum", "Gray", "Black"]],
        },
        "Elegant Gown": ["Black", "Navy", "Red", "SeaGreen", "RoyalBlue", "Gold", "Silver", "Emerald", "Amethyst",
                        "Rose"],
        "Cocktail Dress": ["Black", "Red", "Navy", "Emerald", "Sapphire", "Magenta", "Peach"],
    },
    "Streetwear": {
        "Oversized Hoodie and Cargo Pants": ["Black", "OliveGreen", "Gray", "Beige", "Camo", "NeonGreen", "Rust"],
        "Graphic Tee and Ripped Jeans": ["Black", "White", "Red", "Yellow", "Purple", "Cyan", "Magenta"],
        "Bomber Jacket and Joggers": ["Black", "Navy", "Olive", "Burgundy", "Charcoal", "Orange", "Teal"],
        "Tracksuit": ["Red", "Blue", "Black", "Gray", "Yellow", "Green", "White"],
    },
    "Chic": {
        "Blazer and High-Waisted Pants/Skirt": ["Black", "White", "Beige", "Camel", "Pink", "PowderBlue", "Mint"],
        "Midi Dress with Boots": ["Floral Prints", "SaddleBrown", "Burgundy", "OliveGreen", "Mustard", "Teal", "Rust"],
        "Sweater and Skinny Jeans": ["Cream", "Gray", "Navy", "Burgundy", "ForestGreen", "Mauve", "Terracotta"],
        "Jumpsuit": ["Black", "Navy", "Olive", "Red", "Teal", "Purple", "White"],
    },
    "Bohemian": {
        "Flowy Dress": ["Floral Prints", "Earth Tones", "Cream", "Rust", "Olive", "Turquoise", "Mustard"],
        "Crochet Top and Maxi Skirt": ["White", "Beige", "Brown", "Orange", "Yellow", "Green", "Blue"],
        "Denim and Lace": ["Blue", "White", "Cream", "Beige", "Brown"],
    },
    "Vintage": {
        "A-Line Dress": ["Burgundy", "Navy", "ForestGreen", "Mustard", "Brown", "Black", "Cream"],
        "High-Waisted Trousers and Blouse": ["Navy", "Gray", "Brown", "Olive", "Burgundy", "Cream", "Black"],
        "Swing Dress": ["Red", "Black", "Navy", "Green", "Purple", "Teal", "White"],
    }
}

# --- Shoe Styles ---
SHOE_STYLES = {
    "Casual": ["Sneakers (Athletic)", "Sneakers (Canvas)", "Loafers", "Sandals", "Boots (Casual)", "Espadrilles",
               "Boat Shoes"],
    "Formal": {
        "Men": ["Oxfords", "Derby shoes", "Monk straps", "Brogues", "Opera Pumps"],
        "Women": ["Heels (Pumps)", "Heels (Stilettos)", "Flats", "Ankle boots (Dressy)", "Pointed-toe heels",
                  "Slingbacks"],
    },
    "Streetwear": ["High-top sneakers", "Platform sneakers", "Combat boots", "Chelsea boots", "Skate shoes"],
    "Chic": ["Ankle boots (Stylish)", "Pointed-toe heels", "Ballet flats", "Mules", "Kitten heels"],
    "Bohemian": ["Sandals (Strappy)", "Ankle boots (Suede)", "Espadrilles", "Clogs"],
    "Vintage": ["Oxfords (Vintage)", "Heels (Retro)", "Loafers (Vintage)", "Boots (Vintage)"],
}

# --- Accessory Suggestions ---
ACCESSORY_SUGGESTIONS = {
    "Casual": [
        ("Casual Watch", "Any"), ("Leather Bracelet", "Any"), "Cap", "Sunglasses", "Backpack",
        ("Canvas Tote Bag", "Any"), ("Baseball Cap", "Any"), ("Friendship Bracelet", "Any")
    ],
    "Formal": {
        "Men": [
            ("Dress Watch", "Silver"), ("Silk Tie", "Any"), ("Cufflinks", "Gold/Silver"), ("Pocket Square", "Any"),
            ("Leather Belt", "Any"), ("Tie Clip", "Gold/Silver"), ("Formal Scarf", "Any")
        ],
        "Women": [
            ("Pearl Necklace", "Pearl"), ("Diamond Earrings", "Gold/Silver"), "Clutch", "Scarf (Silk)", "Elegant watch",
            ("Statement Necklace", "Gold/Silver"), ("Elegant Handbag", "Any"), ("Hair Clip (Jeweled)", "Any")
        ],
    },
    "Streetwear": [
        ("Chain Necklace", "Silver"), "Beanie", "Baseball cap", "Crossbody bag", "Bucket hat",
        ("Snapback Cap", "Any"), ("Oversized Scarf", "Any"), ("Fingerless Gloves", "Any")
    ],
    "Chic": [
        ("Gold Statement Necklace", "Gold"), ("Silver Delicate Bracelet", "Silver"), "Stylish handbag",
        "Belt (defining waist)",
        ("Hoop Earrings", "Gold/Silver"), ("Silk Scarf", "Any"), ("Structured Clutch", "Any")
    ],
    "Bohemian": [
        ("Layered Necklaces", "Mixed"), ("Beaded Bracelets", "Any"), "Floppy hat", "Shoulder bag (Fringe)",
        ("Feather Earrings", "Any"), ("Headband (Floral)", "Any"), ("Woven Belt", "Any")
    ],
    "Vintage": [
        ("Brooch", "Gold/Silver"), ("Pearl Necklace", "Pearl"), "Gloves (Lace/Leather)", "Hat (Vintage)",
        ("Cameo Pendant", "Any"), ("Retro Sunglasses", "Any"), ("Vintage Handbag", "Any")
    ],
}

# --- Color name to hex mapping ---
COLOR_MAP = {
    "Black": "#000000",
    "White": "#FFFFFF",
    "Blue": "#0000FF",
    "Gray": "#808080",
    "OliveGreen": "#6B8E23",
    "SkyBlue": "#87CEEB",
    "DenimBlue": "#1560BD",
    "Khaki": "#C3B091",
    "Navy": "#000080",
    "LightBlue": "#ADD8E6",
    "Burgundy": "#800020",
    "Teal": "#008080",
    "Beige": "#F5F5DC",
    "Rust": "#B7410E",
    "Maroon": "#800000",
    "Charcoal": "#36454F",
    "ForestGreen": "#228B22",
    "SlateGray": "#708090",
    "Red": "#FF0000",
    "Green": "#008000",
    "Brown": "#A52A2A",
    "Mustard": "#FFDB58",
    "Cream": "#FFFDD0",
    "Olive": "#808000",
    "SeaGreen": "#2E8B57",
    "RoyalBlue": "#4169E1",
    "Gold": "#FFD700",
    "Silver": "#C0C0C0",
    "Emerald": "#50C878",
    "Amethyst": "#9966CC",
    "Rose": "#FF007F",
    "Sapphire": "#0F52BA",
    "Magenta": "#FF00FF",
    "Peach": "#FFE5B4",
    "Camo": "#78866B",
    "NeonGreen": "#39FF14",
    "Orange": "#FFA500",
    "Purple": "#800080",
    "Cyan": "#00FFFF",
    "Yellow": "#FFFF00",
    "Pink": "#FFC0CB",
    "PowderBlue": "#B0E0E6",
    "Mint": "#3EB489",
    "SaddleBrown": "#8B4513",
    "Mauve": "#E0B0FF",
    "Terracotta": "#E2725B",
    "Turquoise": "#40E0D0",
    "Plum": "#8E4585",
    "Ivory": "#FFFFF0",
    "LightPink": "#FFB6C1",
    "MidnightBlue": "#191970",
    "Coral": "#FF7F50",
    "Lavender": "#E6E6FA",
    "Salmon": "#FA8072",
    "Tan": "#D2B48C",
    "Dark": "#1A1A1A",
    "Very Dark": "#0A0A0A",
    "Very Light": "#F5F5F5",
    "Light": "#E6E6E6",
    "Medium": "#A8A8A8",
    "Floral Prints": "#FF69B4",
    "Earth Tones": "#A0522D"
}

def generate_detailed_outfit(user_info, preferences, occasion):
    style = preferences["style"]
    possible_base_outfits = list(COLOR_PALETTES.get(style, {"Basic": ["Top and Bottom"]}).keys())
    base_outfit = random.choice(possible_base_outfits)

    outfit_colors = []
    possible_colors = COLOR_PALETTES.get(style, {}).get(base_outfit)
    
    if possible_colors:
        if isinstance(possible_colors, dict):
            possible_colors = possible_colors.get(user_info["gender"],
                                               possible_colors.get("Women", possible_colors.get("Men", [])))
            if possible_colors:
                outfit_colors.extend(random.choice(possible_colors))
            else:
                outfit_colors.append(random.choice(preferences["colors"]) if preferences["colors"] else "gray")
        elif isinstance(possible_colors, list):
            num_colors = random.choice([1, 2, 3])
            available_colors = list(set(possible_colors + preferences["colors"]))
            outfit_colors.extend(random.sample(available_colors, min(num_colors, len(available_colors))))
        else:
            outfit_colors.append(random.choice(preferences["colors"]) if preferences["colors"] else "gray")

    shoe_style = ""
    possible_shoes = SHOE_STYLES.get(style)
    if possible_shoes:
        if isinstance(possible_shoes, dict):
            shoe_style = random.choice(
                possible_shoes.get(user_info["gender"],
                                   possible_shoes.get("Women", possible_shoes.get("Men", [preferences["shoes"]]))))
        else:
            shoe_style = random.choice(possible_shoes + [preferences["shoes"]])
    else:
        shoe_style = preferences["shoes"]

    shoe_color = random.choice(preferences["colors"]) if preferences["colors"] else "Black"

    accessories = []
    possible_accessories = ACCESSORY_SUGGESTIONS.get(style)
    num_accessories = random.choice([2, 3])
    chosen_accessories = []

    if possible_accessories:
        available_accessories = []
        if isinstance(possible_accessories, dict):
            available_options = possible_accessories.get(user_info["gender"],
                                                        possible_accessories.get("Women",
                                                                                possible_accessories.get("Men",
                                                                                                        preferences[
                                                                                                            "accessories"])))
            for acc in available_options:
                if isinstance(acc, tuple):
                    available_accessories.append(acc)
                else:
                    available_accessories.append(acc)
        else:
            for acc in possible_accessories + preferences["accessories"]:
                if isinstance(acc, tuple):
                    available_accessories.append(acc)
                else:
                    available_accessories.append(acc)

        preferred_metal = preferences.get("jewelry-metal", "Any").lower()
        filtered_jewelry = [item for item in available_accessories if
                            isinstance(item, tuple) and (preferred_metal == "any" or item[1].lower() == preferred_metal)]
        non_jewelry_accessories = [item for item in available_accessories if not isinstance(item, tuple)]

        num_jewelry_needed = min(num_accessories, len(filtered_jewelry))
        chosen_accessories.extend(random.sample(filtered_jewelry, num_jewelry_needed))

        remaining_needed = num_accessories - len(chosen_accessories)
        num_non_jewelry = min(remaining_needed, len(non_jewelry_accessories))
        chosen_accessories.extend(random.sample(non_jewelry_accessories, num_non_jewelry))
    else:
        if preferences["accessories"]:
            chosen_accessories.extend(
                random.sample(preferences["accessories"], min(num_accessories, len(preferences["accessories"]))))

    for acc in chosen_accessories:
        if isinstance(acc, tuple):
            accessories.append(f"{acc[0]} ({acc[1]})")
        else:
            accessories.append(acc)

    outfit_details = {
        "Outfit Style": base_outfit,
        "Outfit Colors": list(set(outfit_colors)),
        "Shoe Style": shoe_style,
        "Shoe Color": shoe_color,
        "Accessories": list(set(accessories)),
        "Occasion": occasion,
    }
    return outfit_details

def generate_gemini_prompt(recommendation, user_info):
    prompt = f"Generate an image of a {user_info['gender'].lower()} wearing a {recommendation['Outfit Style'].lower()} in "
    prompt += ", ".join([f"{color.lower()}" for color in recommendation['Outfit Colors']])
    prompt += f", with {recommendation['Shoe Style'].lower()} in {recommendation['Shoe Color'].lower()}, "

    if recommendation['Accessories']:
        prompt += "and the following accessories: "
        prompt += ", ".join([f"{acc.lower()}" for acc in recommendation['Accessories']])
    else:
        prompt += "with no accessories."
    prompt += f". The outfit is suitable for a {recommendation['Occasion'].lower()} occasion. "
    prompt += f"The {user_info['gender'].lower()} has {user_info['skinTone'].lower()} skin with "
    prompt += f"{user_info['skinUndertone'].lower()} undertones, and a {user_info['bodyShape'].lower()} body shape, "
    prompt += f"is {user_info['height'].lower()} tall and weighs {user_info['weight'].lower()}."
    return prompt

def generate_search_query(recommendation):
    search_parts = []
    colors = recommendation["Outfit Colors"]
    outfit_style = recommendation["Outfit Style"]
    
    if "T-Shirt" in outfit_style or "Tee" in outfit_style:
        search_parts.append(f"{colors[0]} t-shirt")
    if "Jeans" in outfit_style:
        search_parts.append(f"{colors[1]} jeans" if len(colors) > 1 else f"{colors[0]} jeans")
    if "Polo" in outfit_style:
        search_parts.append(f"{colors[0]} polo shirt")
    if "Chinos" in outfit_style:
        search_parts.append(f"{colors[1]} chinos" if len(colors) > 1 else f"{colors[0]} chinos")
    if "Hoodie" in outfit_style:
        search_parts.append(f"{colors[0]} hoodie")
    if "Joggers" in outfit_style:
        search_parts.append(f"{colors[1]} joggers" if len(colors) > 1 else f"{colors[0]} joggers")
    if "Flannel" in outfit_style:
        search_parts.append(f"{colors[0]} flannel shirt")
    if "Denim Jacket" in outfit_style:
        search_parts.append(f"{colors[0]} denim jacket")
    if "Suit" in outfit_style:
        search_parts.append(f"{colors[0]} suit")
    if "Blazer" in outfit_style:
        search_parts.append(f"{colors[0]} blazer")
    if "Gown" in outfit_style:
        search_parts.append(f"{colors[0]} gown")
    if "Cocktail Dress" in outfit_style:
        search_parts.append(f"{colors[0]} cocktail dress")
    if "Oversized Hoodie" in outfit_style:
        search_parts.append(f"{colors[0]} oversized hoodie")
    if "Cargo Pants" in outfit_style:
        search_parts.append(f"{colors[1]} cargo pants" if len(colors) > 1 else f"{colors[0]} cargo pants")
    if "Bomber Jacket" in outfit_style:
        search_parts.append(f"{colors[0]} bomber jacket")
    if "Tracksuit" in outfit_style:
        search_parts.append(f"{colors[0]} tracksuit")
    if "High-Waisted Pants" in outfit_style or "High-Waisted Skirt" in outfit_style:
        search_parts.append(f"{colors[1]} high-waisted pants" if len(colors) > 1 else f"{colors[0]} high-waisted pants")
    if "Midi Dress" in outfit_style:
        search_parts.append(f"{colors[0]} midi dress")
    if "Sweater" in outfit_style:
        search_parts.append(f"{colors[0]} sweater")
    if "Skinny Jeans" in outfit_style:
        search_parts.append(f"{colors[1]} skinny jeans" if len(colors) > 1 else f"{colors[0]} skinny jeans")
    if "Jumpsuit" in outfit_style:
        search_parts.append(f"{colors[0]} jumpsuit")
    if "Flowy Dress" in outfit_style:
        search_parts.append(f"{colors[0]} flowy dress")
    if "Crochet Top" in outfit_style:
        search_parts.append(f"{colors[0]} crochet top")
    if "Maxi Skirt" in outfit_style:
        search_parts.append(f"{colors[1]} maxi skirt" if len(colors) > 1 else f"{colors[0]} maxi skirt")
    if "Denim and Lace" in outfit_style:
        search_parts.append(f"{colors[0]} denim top with lace")
    if "A-Line Dress" in outfit_style:
        search_parts.append(f"{colors[0]} a-line dress")
    if "High-Waisted Trousers" in outfit_style:
        search_parts.append(f"{colors[1]} high-waisted trousers" if len(colors) > 1 else f"{colors[0]} high-waisted trousers")
    if "Blouse" in outfit_style:
        search_parts.append(f"{colors[1]} blouse" if len(colors) > 1 else f"{colors[0]} blouse")
    if "Swing Dress" in outfit_style:
        search_parts.append(f"{colors[0]} swing dress")
    
    if recommendation["Shoe Style"]:
        search_parts.append(recommendation["Shoe Style"])
    
    if recommendation["Accessories"] and len(recommendation["Accessories"]) > 0:
        search_parts.extend([acc.split('(')[0].strip() for acc in recommendation["Accessories"]])
    
    return " ".join(search_parts)

def get_color_value(colorName):
    return COLOR_MAP.get(colorName, "#CCCCCC")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    try:
        data = request.json
        
        # Process user info
        user_info = {
            "gender": data["gender"],
            "height": data["height"],
            "weight": data["weight"],
            "bodyShape": data["body-shape"],
            "skinTone": data["skin-tone"],
            "skinUndertone": data["skin-undertone"]
        }
        
        # Process fashion preferences
        fashion_prefs = {
            "style": data["style"],
            "colors": [c.strip() for c in data["colors"].split(",")],
            "shoes": data["shoes"],
            "accessories": [a.strip() for a in data["accessories"].split(",")],
            "jewelry-metal": data["jewelry-metal"]
        }
        
        # Get occasion
        occasion = data["occasion"]
        
        # Generate recommendation
        recommendation = generate_detailed_outfit(user_info, fashion_prefs, occasion)
        gemini_prompt = generate_gemini_prompt(recommendation, user_info)
        search_query = generate_search_query(recommendation)
        
        # Prepare response
        response = {
            "recommendation": recommendation,
            "gemini_prompt": gemini_prompt,
            "search_query": search_query
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)