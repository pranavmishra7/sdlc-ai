import json
import re


def safe_parse_json(text: str) -> dict:
    """
    Extract and parse JSON from LLM output safely.
    """
    raw = """{\n    \"problem_statement\": {\n        \"overview\": \"Investors face complexity in navigating various financial investment solutions, leading to confusion and missed opportunities.\",\n        \"current_challenges\": [\n            \"Difficulty in comparing different investment options\",\n            \"Limited access to unbiased financial information\",\n            \"Inadequate tools for tracking investment performance\",\n            \"Insufficient support for investors with complex financial situations\"\n        ],\n        \"business_impact\": [\n            \"Missed investment opportunities due to lack of clarity\",\n            \"Increased stress and anxiety among investors\",\n            \"Decreased investor satisfaction and loyalty\",\n            \"Opportunity cost due to inadequate investment guidance\"\n        ]\n    },\n    \"target_users\": {\n        \"primary_users\": [\n            \"Individual investors seeking to grow their wealth\",\n            \"Financial advisors looking for tools to enhance client services\",\n            \"Investment firms seeking to improve investor experience\"\n        ],\n        \"secondary_users\": [\n            \"Financial institutions and banks\",\n            \"Regulatory bodies and government agencies\"\n        ]\n    },\n    \"assumptions\": [\n        \"Investors have access to basic financial information\",\n        \"Investors are tech-savvy and familiar with digital tools\",\n        \"Financial advisors have the necessary expertise to interpret investment data\",\n        \"Investment firms prioritize investor satisfaction and loyalty\",\n        \"Regulatory bodies have established clear guidelines for investment products\"\n    ],\n    \"out_of_scope\": [\n        \"Creating a new investment product or service\",\n        \"Providing personalized investment advice\",\n        \"Conducting investment research or analysis\"\n    ]\n}"""
    print(raw)
    text = raw  # For demonstration purposes, replace with actual LLM output
    print("Raw LLM output:", text)
    if not text or not text.strip():
        raise ValueError("Empty LLM output")

    # Remove markdown fences if present
    text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    # Find first JSON object
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("LLM output does not contain valid JSON")

    try:
        print(json.loads(match.group()))
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by LLM: {e}")
