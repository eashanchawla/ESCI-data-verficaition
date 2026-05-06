## ESCI Verification

## Verifying ESCI "Exact" Labels with Local LLMs 
### Iterative prompt engineering on Gemma:4b through Ollama

The ESCI dataset labels query-product pairs as 'E' when the product satisfies all query specifications. However, some labels are incorrect i.e.
**Product information explicitly contradicts a query requirement, despite being labeled as an exact match**
 
**Target Queries:**
1. `"aa batteries 100 pack"`
2. `"kodak photo paper 8.5 x 11 glossy"`
3. `"dewalt 8v max cordless screwdriver kit, gyroscopic"`

**Key Rules:**
- **Missing info != conflict**
- **Extra info != conflict**
- **Explicit contradiction == conflict**

**Approach**: 
I use a local LLM via Ollama with structured Pydantic output schemas to automatically detect these conflicts, iterating through 3 prompt versions systematically
fixing failures.


**TODO:**
- [X] Initial commit
- [X] Code cleanup
- [X] Prompt changes
- [X] Add function doc strings
- [ ] Handling missing data (product id: 0547238967 appears in multiple locales -- and has differet vals we see one in jp with null values) 
- [ ] Performance evaluation per query
- [X] Same prompt with different model
- [X] Second prompt with re-ordered schema 
- [X] Second critique prompt
- [X] Final documentation / Presentation cleanup (IN PROGRESS)
- [X] Evaluation code to create report for comparision between human labels and LLM generated labels 
- [ ] Pass through ruff or black for linting
- [ ] use standard logger package from python to do logging (Overkill for this)
- [ ] Train Test split? (Overkill for this)
- [ ] Build in confidence voting for evaluation -- how do you resolve reformulated query (by separating it out to a different prompt) (Overkill for this)

Ideas: 
1. Async model calls with retries and exponential backoff to avoid rate limit 
2. Single LLM prompt on Gemini vs Multiple Prompts on a weaker model vs Human Labels? 