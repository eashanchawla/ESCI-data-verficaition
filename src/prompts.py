'''
Houses all prompts used
'''

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
4. Minimal Edit: If a conflict exists, rewrite the query to match the product perfectly. ONLY change the specific words that contradict. Do not delete words if you can replace them with the accurate attribute. Keep all non-conflicing words exactly the same. 

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


PASS1_PROMPT = '''
You are an expert extracting and comparing features between search queries and product listings.

For the given query and product information:
1. Extract all distinct features/specifications from the query.
2. Extract all features/specifications from the product information.
3. For each query feature, find the corresponding product feature and grade it:
   - "match" if the product confirms the query feature
   - "contradiction" if the product explicitly states a different value for the same attribute
   - "missing" if the product does not mention anything about that feature

Do NOT make a final judgment. Just extract and align.
'''

PASS2_PROMPT = '''
You are an expert making final judgments on query-product relevance.

You will receive a query and a feature alignment from a previous analysis. Some features 
were flagged as "contradiction". Your job is to re-evaluate each flagged contradiction 
and determine if it is a GENUINE conflict or a false alarm.

Common false alarms to watch for:
- Same quantity, different wording: "100 pack" vs "100 count" vs "100-pack" are NOT conflicts
- Same dimensions, different notation: "8.5 x 11" vs "8-1/2 x 11" vs "8.5" x 11"" are NOT conflicts
- Same finish, different wording: "glossy" vs "gloss finish" vs "high gloss" are NOT conflicts
- Extra info in product: product having MORE than what query asks for is NOT a conflict

A genuine conflict is when the actual VALUE differs: 100 vs 50, AA vs AAA, glossy vs matte, 
dewalt vs enertwist.

If after re-evaluation no genuine conflicts remain, set conflict_found to False.
If genuine conflicts exist, set conflict_found to True and reformulate the query.
'''




EVALUATION_PROMPT_V2 = '''
You are an expert auditing labeled data with user search queries and returned product matches. 
Your goal is to tell us if product and query information matches or not. 
1. You must only flag a conflict if the product explicitly states a different value for the same attribute type the query specified. Following attributes can create conflicts:
    - Quantity / count: a conflict exists only when the NUMBERS differ (eg query: 100 pack, product: 32 pack = conflict). 
    - Size / dimensions (eg query: 8.5x11, product: 4x6 = conflict)
    - Finish / material (eg query: glossy, product: matte = conflict)
    - Battery or product type (eg query: AA, product: AAA = conflict)
    - Brand name (eg query: dewalt, product: enertwist = conflict)
    - Inclusions or exclusions (eg query: without pillow shams, product: includes pillow shams = conflict)
2. Missing information: If the query specifies a feature, and the product text does not mention anything related to that at all, assume it is a match (no contradiction). Do not flag missing info as a conflict. 
3. Extra info: If the product includes extra items or features beyond what the query asks for (eg extra batteries, extra accessories, carry case), it is still a match. A product can exceed specifications without creating a conflict.
4. Intra-product contradictions: If the product title states one value but the bullet points state a different value for the same attribute, extract BOTH values as separate product features and flag as a conflict since the product info cannot reliably confirm the query specification.
5. Minimal edit: If a conflict exists, rewrite the query to match the product perfectly. ONLY change the specific words that contradict. Keep all non-conflicting words exactly the same.
6. Step by step analysis: You must provide an explanation in the 'feature_alignment' field. For each query feature, find the corresponding product feature and grade it as match, contradiction, or missing.
7. Self consistency: After completing feature_alignment, review it to write the final 'reasoning' field. If any feature_alignment entry has status 'contradiction', conflict_found MUST be True.

Examples:
-- Contradiction example
Query: "dewalt 8v max cordless screwdriver kit, gyroscopic"
Product Title: "DEWALT 12V Max Screwdriver, tool only"
Analysis: The query asks for an 8v kit. The product explicitly states 12v and "tool only" instead of "kit". No contradiction on "gyroscopic" so we leave it in the reformulated query.
Conflict Found: True
Reformulated Query: "dewalt 12v max cordless screwdriver tool only, gyroscopic"
-- Missing Info Example (NOT a contradiction)
Query: "kodak photo paper 8.5 x 11 glossy"
Product Title: "Photo Paper 6.5 mil, Glossy, 8-1/2 x 11, 100 sheets/pack"
Product Brand: "nan"
Product Bullet Points: "nan"
Analysis: The query specifies brand "kodak". Product info does not mention any brand, but there is no explicit contradiction. We assume it is a match.
Conflict Found: False
Reformulated Query: null
'''