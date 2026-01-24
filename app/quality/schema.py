SECTION_SCHEMAS = {
    "intake": {
        "required": ["problem_statement", "target_users", "business_goals"],
        "min_items": {
            "target_users": 1,
            "business_goals": 2,
        },
    },
    "scope": {
        "required": ["in_scope", "out_of_scope", "success_criteria"],
        "min_items": {
            "in_scope": 3,
            "success_criteria": 2,
        },
    },
    "requirements": {
        "required": ["functional_requirements", "non_functional_requirements"],
        "min_items": {
            "functional_requirements": 5,
        },
    },
    "architecture": {
        "required": ["architecture_overview", "components", "technology_stack"],
        "min_items": {
            "components": 4,
        },
    },
    "estimation": {
        "required": ["effort_breakdown", "timeline_weeks"],
        "min_items": {
            "effort_breakdown": 3,
        },
    },
    "risk": {
        "required": ["technical_risks", "business_risks", "mitigations"],
        "min_items": {
            "technical_risks": 2,
        },
    },
    "sow": {
        "required": ["deliverables", "milestones"],
        "min_items": {
            "deliverables": 3,
        },
    },
}
