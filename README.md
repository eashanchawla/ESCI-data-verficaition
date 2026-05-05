## ESCI Verification

**TODO:**
- [X] Initial commit
- [X] Code cleanup
- [X] Prompt changes
- [X] Add function doc strings
- [ ] Handling missing data (product id: 0547238967 appears in multiple locales -- and has differet vals we see one in jp with null values) 
- [ ] Handling cases where nothing matches? And the product to query match is bad to begin with but still marked E?
- [ ] Performance evaluation per query
- [X] Same prompt with different model
- [X] Second prompt with re-ordered schema 
- [ ] Second critique prompt
- [ ] Final documentation / Presentation cleanup (IN PROGRESS)
- [X] Evaluation code to create report for comparision between human labels and LLM generated labels 
- [ ] Pass through ruff or black for linting
- [ ] use standard logger package from python to do logging (Overkill for this)
- [ ] Train Test split? (Overkill for this)
- [ ] Build in confidence voting for evaluation -- how do you resolve reformulated query (by separating it out to a different prompt) (Overkill for this)

Ideas: 
1. Async model calls with retries and exponential backoff to avoid rate limit 
2. Single LLM prompt on Gemini vs Multiple Prompts on a weaker model vs Human Labels? 
3. Label with the dataset and then 
4. Reranker with Lambda Rank? 
   