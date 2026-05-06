'''
Purpose: schema for responses from the LLM
'''

from pydantic import BaseModel, Field
from typing import List

class MyResponse(BaseModel):
    '''V1 schema'''
    query_features: List[str] = Field(description="List of features explicitly mentioned in the query - brand, specifications, other attributes")
    product_features: List[str] = Field(description="List of features explicitly mentioned in the product title / description / brand - brand, specifications, other attributes. if product title and other product infromation has conflicting info, give product title preference. For example title says 100 pack but bullet points say 50 pack, only extract 50 pack as feature")
    conflict_found: bool = Field(description="True only if a product attribute explicitly does not match a query attribute")
    reasoning: str = Field(description="Explain why there is or is not a conflict")
    # acceptable: bool = Field(description="True if the product is an exact match for the query. False otherwise")
    reformulated_query: str | None = Field(description="If conflict_found is True, write a search query replacing the exact contradiction words with product attributes, else output null.")

class FeatureAlignment(BaseModel):
    query_feature: str = Field(description="A single feature from the query")
    product_feature: str | None = Field(description="The corresponding value found in the product info, or null if not mentioned")
    status: str = Field(description="One of: 'match', 'contradiction', 'missing'.")
    explaination: str = Field(description="Brief explanation of why this status was chosen. Must be in English.")

class Pass1Response(BaseModel):
    '''Just extract and align features. No final judgement'''
    query_features: List[str] = Field(description="List of features explicitly mentioned in the query - brand, specifications, other attributes")
    product_features: List[str] = Field(description="List of features explicitly mentioned in the product title / description / brand / bullet points - brand, specifications, other attributes.")
    feature_alignment: List[FeatureAlignment] = Field(description="For each query feature, find the matching product attribute and grade it")

class Pass2Response(BaseModel):
    '''Just extract and align features. No final judgement'''
    reasoning: str = Field(description="Re-evaluate each contradiction. Are they genuine conflicts or just different wording for the same value? Explain in English.")
    conflict_found: bool = Field(description="True only if a geniune conflict exists after re-evaluation")
    reformulated_query: str | None = Field(description="If conflict_found is True, rewrite query replacing only contradicted words. Otherwise None")

class MyResponseV2(BaseModel):
    '''V1 schema reordered so the model does reasoning before making a decision'''
    query_features: List[str] = Field(description="List of features explicitly mentioned in the query - brand, specifications, other attributes")
    product_features: List[str] = Field(description="List of features explicitly mentioned in the product title / description / brand / bullet points - brand, specifications, other attributes.")
    feature_alignment: List[FeatureAlignment] = Field(description="For each query feature, find the matching product attribute and grade it")
    reasoning: str = Field(description="Summary of the alignment analysis. Must be in English.")
    conflict_found: bool = Field(description="True if any feature_alignment has status='contradiction'. Must be consistent with feature alignment")
    reformulated_query: str | None = Field(description="If conflict_found is True, rewrite query replacing only contradicted words. Otherwise None")
