MOCK_BRAND_BRIEF = {
    "product_name": "Lavender Soy Candle",
    "category": "Home & Wellness",
    "target_audience": "Women 25-40, wellness-focused",
    "brand_vibe": "calm, minimal, premium",
    "brand_voice": "warm, soft-spoken, aspirational",
    "color_palette": ["#9B8EC4", "#F5F0EB", "#C9A96E"],
    "taglines": [
        "Find your calm",
        "One flame. Pure peace.",
        "Your evening ritual"
    ],
    "selling_points": [
        "100% soy wax",
        "Hand-poured in small batches",
        "40-hour burn time"
    ],
    "emotional_angle": "comfort and self-care"
}
MOCK_COPY = {
    "instagram": {
        "hook": "Your evening deserves this.",
        "body": "Pure lavender. Hand-poured soy wax. 40 hours of calm.",
        "cta": "Shop now — link in bio",
        "hashtags": ["#selfcare", "#candlelover", "#wellness"]
    },
    "facebook": {
        "primary_text": "Your evening ritual, reimagined.",
        "headline": "Lavender Soy Candle — Find Your Calm",
        "description": "Hand-poured. 100% soy wax. 40 hours of pure relaxation.",
        "cta": "Shop Now",
        "long_body": "We believe your evenings should feel like a deep breath."
    },
    "google": {
        "headlines": ["Lavender Soy Candle", "40-Hour Burn Time", "100% Soy Wax"],
        "descriptions": ["Hand-poured lavender candle for ultimate calm.", "Elevate your self-care routine."],
        "keywords": ["lavender candle", "soy candle", "wellness candle"]
    },
    "tiktok": {
        "hook": "POV: You finally found the perfect evening ritual.",
        "scenes": [
            {"time": "0-2s", "action": "Hook text on screen"},
            {"time": "2-5s", "action": "Close-up lighting the candle"},
            {"time": "5-10s", "action": "Slow zoom on flame"},
            {"time": "10-13s", "action": "Person relaxing"},
            {"time": "13-15s", "action": "Product shot with tagline"}
        ],
        "cta": "Link in bio",
        "suggested_audio": "Soft lo-fi"
    },
    "email": {
        "subject_lines": ["Your evening just got an upgrade", "This candle changes everything"],
        "preview_text": "Hand-poured lavender soy wax. Free shipping.",
        "body": "Hi there,\n\nWe made something for your evenings.\n\nShop now\n\nWarm regards,\nThe Brand Team"
    }
}

MOCK_PERSONAS = [
    {
        "name": "Wellness Emma",
        "age": 28,
        "job": "Yoga instructor",
        "income": "$45K-$60K",
        "platforms": ["Instagram", "Pinterest"],
        "active_times": "Evenings 7-10pm",
        "values": ["Natural ingredients", "Self-care"],
        "pain_points": ["Stressed from work", "Wants affordable self-care"],
        "buying_triggers": ["Beautiful aesthetics", "Natural claims"],
        "buying_blockers": ["Synthetic ingredients", "No reviews"],
        "best_ad_format": "Instagram Story + Carousel"
    },
    {
        "name": "Gift-Giver Rachel",
        "age": 35,
        "job": "Marketing manager",
        "income": "$70K-$90K",
        "platforms": ["Facebook", "Google"],
        "active_times": "Lunch breaks, weekday evenings",
        "values": ["Thoughtful gifts", "Quality"],
        "pain_points": ["Never knows what to gift"],
        "buying_triggers": ["Gift-ready packaging", "Free shipping"],
        "buying_blockers": ["Long shipping", "Over $50"],
        "best_ad_format": "Google Search + Facebook Retargeting"
    },
    {
        "name": "Home Decor Maya",
        "age": 31,
        "job": "Interior designer",
        "income": "$80K-$110K",
        "platforms": ["Instagram", "TikTok"],
        "active_times": "Morning 7-8am, late night 10pm",
        "values": ["Aesthetics", "Premium quality"],
        "pain_points": ["Wants Instagram-worthy space"],
        "buying_triggers": ["Minimalist design", "Artisan/handmade"],
        "buying_blockers": ["Generic branding", "Bad photos"],
        "best_ad_format": "TikTok Video + Instagram Carousel"
    }
]
MOCK_MEDIA_PLAN = {
    "budget_split": {
        "instagram": 40,
        "tiktok": 25,
        "google": 20,
        "email": 15
    },
    "daily_budget_recommendation": "$50-$100/day",
    "platform_strategy": [
        {"platform": "Instagram", "creatives": ["carousel", "story", "video"], "targeting": "Emma + Maya"},
        {"platform": "TikTok", "creatives": ["video"], "targeting": "Maya + younger audience"},
        {"platform": "Google", "creatives": ["search ads"], "targeting": "Rachel searching for gifts"},
        {"platform": "Email", "creatives": ["welcome sequence"], "targeting": "Existing customers"}
    ],
    "ab_tests": [
        {"test": "Instagram hook", "variant_a": "Your evening deserves this.", "variant_b": "Stop scrolling. Light this instead.", "metric": "CTR"},
        {"test": "Google headline", "variant_a": "Pure Calm", "variant_b": "40-Hour Burn", "metric": "Conversions"}
    ],
    "seven_day_calendar": [
        {"day": 1, "action": "Soft launch Instagram carousel", "platform": "Instagram"},
        {"day": 2, "action": "Launch TikTok video", "platform": "TikTok"},
        {"day": 3, "action": "Start Google search ads", "platform": "Google"},
        {"day": 4, "action": "Send email blast", "platform": "Email"},
        {"day": 5, "action": "Boost best Instagram post", "platform": "Instagram"},
        {"day": 6, "action": "Launch Facebook retargeting", "platform": "Facebook"},
        {"day": 7, "action": "Review metrics, scale winners", "platform": "All"}
    ]
}