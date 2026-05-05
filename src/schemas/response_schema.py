'''
Purpose: schema for responses from the LLM
'''

from pydantic import BaseModel, Field
from typing import List

class MyResponse(BaseModel):
    query_features: List[str] = Field(description="List of features explicitly mentioned in the query - brand, specifications, other attributes")
    product_features: List[str] = Field(description="List of features explicitly mentioned in the product title / description / brand - brand, specifications, other attributes. if product title and other product infromation has conflicting info, give product title preference. For example title says 100 pack but bullet points say 50 pack, only extract 50 pack as feature")
    conflict_found: bool = Field(description="True only if a product attribute explicitly does not match a query attribute")
    reasoning: str = Field(description="Explain why there is or is not a conflict")
    acceptable: bool = Field(description="True if the product is an exact match for the query. False otherwise")
    reformulated_query: str | None = Field(description="If conflict_found is True, write a search query replacing the exact contradiction words with product attributes. Otherwise, output null. Only change contradictory parts of query string.")

class MyResponseReordered(BaseModel):
    query_features: List[str] = Field(description="List of features explicitly mentioned in the query - brand, specifications, other attributes")
    product_features: List[str] = Field(description="List of features explicitly mentioned in the product title / description / brand - brand, specifications, other attributes. if product title and other product infromation has conflicting info, give product title preference. For example title says 100 pack but bullet points say 50 pack, only extract 50 pack as feature")
    reasoning: str = Field(description="Explain why there is or is not a conflict")
    conflict_found: bool = Field(description="True only if a product attribute explicitly does not match a query attribute")
    acceptable: bool = Field(description="True if the product is an exact match for the query. False otherwise")
    reformulated_query: str | None = Field(description="If conflict_found is True, write a search query replacing the exact contradiction words with product attributes. Otherwise, output null. Only change contradictory parts of query string.")