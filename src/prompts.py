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
1. Break the query down into specific dimensions/categories (e.g., 'Core Product', 'Quantity', 'Brand', 'Voltage', 'Finish', 'Size').
2. For EACH query dimension, extract the specific value required by the query.
3. Find the SINGLE BEST corresponding value in the product information for that EXACT dimension.
4. Grade each dimension's alignment:
   - "match" if the product confirms the query's value for that dimension
   - "contradiction" if the product explicitly states a DIFFERENT VALUE for that dimension
   - "missing" if the product does not mention anything about that dimension at all

Product type mismatch rule: If the 'Core Product' dimension differs (e.g., query wants "screwdriver kit", product is "battery charger"), this is a CONTRADICTION, not "missing".

Important:
- Only compare a query dimension against the same dimension in the product. Do NOT compare 'Quantity' to 'Voltage' or 'Core Product' to 'Color'.
- If the product does not mention the dimension, set product_feature to null and status to "missing".

Example:
Query: "aa batteries 100 pack"
Product Title: "Energizer AA Batteries, 50 Count"

Correct alignment:
- dimension: "Core Product", query_feature: "batteries", product_feature: "Batteries", status: "match"
- dimension: "Battery Type", query_feature: "aa", product_feature: "AA", status: "match"
- dimension: "Quantity", query_feature: "100 pack", product_feature: "50 Count", status: "contradiction"

Do NOT make a final judgment. Just extract and align.
'''

PASS2_PROMPT = '''
You are an expert making final judgments on query-product relevance.

You will receive a query and a feature alignment from a previous analysis. Some features
were flagged as "contradiction". Your job is to re-evaluate each flagged contradiction
and determine if it is a GENUINE conflict or a false alarm.

False alarms (NOT genuine conflicts):
- Same value, different notation: "8.5 x 11" vs "8-1/2 x 11" are the SAME dimensions
- Same value, different wording: "100 pack" vs "100 count" vs "100-pack" are the SAME quantity
- Same finish, synonym: "glossy" vs "gloss finish" vs "high gloss" are the SAME finish
- Extra features: product having MORE than what query asks for is NOT a conflict
- Unrelated comparison: if a query feature was compared against a product feature of a completely different attribute type (e.g., quantity vs voltage, brand vs color), ignore it - it is a bad alignment, not a genuine conflict

Genuine conflicts (these ARE real):
- Different NUMBERS: 100 vs 50, 100 vs 60, 8v vs 12v
- Different TYPES: AA vs AAA, screwdriver vs battery charger
- Different FINISHES with opposite meanings: glossy vs matte, gloss vs matte
- Different BRANDS: dewalt vs enertwist


If after re-evaluation no genuine conflicts remain, set conflict_found to False.
If genuine conflicts exist, set conflict_found to True and reformulate the query to remove explicit conflict.
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