"""
Configuration constants for Vetro integration
Centralizes layer definintions, keywords, and system fields
"""

# Only these layers will be fetched from the API.
ALLOWED_LAYERS = [
    "Pole",
    "Handhole",
    "Service Location",
    "Aerial Splice Closure",
    "Flower Pot Dead End",
    "Pigtail",
    "Lateral",
    "Backbone",
    "Duct",
    "Drop",
    "Combined",
    "Strand",
    "Cabinet (FDH)",
    "CO",
    "NAP",
    "Slack Loop",
]

# 2. To map filename words to Layer Names.
LAYER_KEYWORDS = {
    "flower": "Flower Pot Dead End",
    "pot": "Flower Pot Dead End",
    "service": "Service Location",
    "handhole": "Handhole",
    "splice": "Aerial Splice Closure",
    "closure": "Aerial Splice Closure",
    "pole": "Pole",
    "pigtail": "Pigtail",
    "lateral": "Lateral",
    "backbone": "Backbone",
    "co": "CO",
    "nap": "NAP",
    "slack": "Slack Loop",
    "loop": "Slack Loop",
    "duct": "Duct",
    "drop": "Drop",
    "strand": "Strand",
    "cabinet": "Cabinet (FDH)",
    "fdh": "Cabinet (FDH)",
}


# Columns to ignore during schema fetching.
SYSTEM_FIELDS = [
    "layer_id",
    "plan_id",
    "global_id",
    "created_at",
    "updated_at",
    "geometry",
    "shape",
    "objectid",
    "external_id",
    "import_id",
]
