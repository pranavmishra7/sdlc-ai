QUALITY_CONTRACTS = {
    "intake": {
        "required_keys": ["problem", "target_users", "assumptions"],
        "min_score": 70,
    },
    "scope": {
        "required_keys": ["in_scope", "out_of_scope", "constraints"],
        "min_score": 70,
    },
    "requirements": {
        "required_keys": ["functional", "non_functional"],
        "min_score": 75,
    },
    "architecture": {
        "required_keys": [
            "architecture_overview",
            "major_components",
            "data_flow",
            "technology_choices",
        ],
        "min_score": 80,
    },
    "estimation": {
        "required_keys": [
            "effort_breakdown",
            "estimated_timeline",
            "assumptions",
            "risks",
        ],
        "min_score": 75,
    },
    "risk": {
        "required_keys": ["technical", "business", "operational"],
        "min_score": 70,
    },
    "sow": {
        "required_keys": ["deliverables", "milestones", "commercials"],
        "min_score": 80,
    },
}
