four_way_junction = {
    "junction_id": "J1",
    "junction_type": "FOUR_WAY_INTERSECTION",
    "street_names": [
        "North_Main",
        "South_Main",
        "East_Road",
        "West_Road",
    ],
    "conflict_map": {
        "North_Main": ["East_Road", "West_Road"],
        "South_Main": ["East_Road", "West_Road"],
        "East_Road":  ["North_Main", "South_Main"],
        "West_Road":  ["North_Main", "South_Main"],
    },
    "green_capacity": 4,
    "allow_parallel_green": True,   
    "min_green_interval": 3,        
}
u_turn_junction = {
    "junction_id": "J2",
    "junction_type": "U_TURN_POINT",
    "street_names": [
        "Main_Forward",
        "UTurn_Main",
        "Side_Exit",
    ],
    "conflict_map": {
        "Main_Forward": ["UTurn_Main"],
        "UTurn_Main":   ["Main_Forward", "Side_Exit"],
        "Side_Exit":    ["UTurn_Main"],
    },
    "green_capacity": 3,
    "allow_parallel_green": True,   
    "min_green_interval": 0,
}
merge_junction = {
    "junction_id": "J3",
    "junction_type": "ROAD_MERGE",
    "street_names": [
        "Main_Road",
        "Merge_Road",
    ],
    "conflict_map": {
        "Main_Road":  ["Merge_Road"],
        "Merge_Road": ["Main_Road"],
    },
    "green_capacity": 3,
    "allow_parallel_green": False,  
    "min_green_interval": 0,
}
three_way_junction = {
    "junction_id": "J4",
    "junction_type": "THREE_WAY_INTERSECTION",
    "street_names": [
        "North_Main_T",
        "South_Main_T",
        "Side_Road_T",
    ],
    "conflict_map": {
        "North_Main_T": ["Side_Road_T"],
        "South_Main_T": ["Side_Road_T"],
        "Side_Road_T":  ["North_Main_T", "South_Main_T"],
    },
    "green_capacity": 4,
    "allow_parallel_green": True,   
    "min_green_interval": 0,
}
ALL_JUNCTION_CONFIGS = [
    four_way_junction,
    u_turn_junction,
    merge_junction,
    three_way_junction,
]
def get_junction_config(junction_id: str) -> dict | None:
    for config in ALL_JUNCTION_CONFIGS:
        if config["junction_id"] == junction_id:
            return config
    return None
def get_all_street_names() -> list[str]:
    streets = []
    for config in ALL_JUNCTION_CONFIGS:
        streets.extend(config["street_names"])
    return streets
