EVALUATION_PROMPT = '''
You are an expert auditing labeled data with user search queries and returned product matches. 
Your goal is to tell us if product and query information matches or not. 

1. You must only flag a conflict if the product explicitly states a different value for the same attribute type the query specified. Following attributes can create conflicts:
    - Quantity / count (eg query: 100 pack, product: 32 pack = conflict)
    - Size / dimensions (eg query: 8.5x11, product: 4x6 = conflict)
    - finish / material (eg query: glossy, product: matte = conflict)
    - other attributes including brand name, inclusions or exclusions 
2. Missing information: If the query specifies a brand or feature, and the product text does not mention anything related to that at all, assume it is a match (no contradiction). Do not flag missing info as a conflict. 
3. Extra Info: If the product includes extra items / features beyond the query, it IS a match. Do not flag as a contradiction.
5. Minimal Edit: If a conflict exists, rewrite the query to match the product perfectly. ONLY change the specific words that contradict. Do not delete words if you can replace them with the accurate attribute. Keep all non-conflicing words exactly the same. 

Examples:
-- Contradiction example
Query: "dewalt 8v max cordless screwdriver kit, gyroscopic"
Product Title: "DEWALT 12V Max Screwdriver, tool only"
Analysis: The query asks for an 8v kit. The product explicitly contradicts this by being a 12v tool only version. No contradiction on "gyroscopic" so we leave it in the reformulated query.
Conflict Found: True
Reformulated Query: "dewalt 12v max cordless screwdriver tool only, gyroscopic"

-- Missing Info Example
Query: "kodak photo paper 8.5 X 11 glossy"
Product Title: "Photo Paper 6.5 mil, Glossy, 8-1/2 X11, 100 sheets/pack"
Product Brand: "nan"
Product Bullet Points: "nan"
Analysis: The query specifies brand "kodak". Product info is missing brand name, but there is no explicit contradiction, we assume it is a match"
Conflict Found: False
Reformulated Query: null
'''

EVALUATION_PROMPT_V2 = ''''''