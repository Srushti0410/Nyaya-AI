"""
Example usage of the input_processor module.

This demonstrates how the input processor enriches user queries
with structured context and issue type detection.
"""

from app.services.input_processor import enrich_query, extract_case_context

# Example 1: Tenancy Dispute
print("=" * 60)
print("Example 1: Tenancy Dispute")
print("=" * 60)

query1 = "what should I do"
history1 = ["My landlord locked my room and threw my belongings out"]

enriched1 = enrich_query(query1, history1)
print("\nRaw Input:")
print(f"Query: '{query1}'")
print(f"History: {history1}")
print("\nEnriched Output:")
print(enriched1)

context1 = extract_case_context(query1, history1)
print("\nExtracted Context:")
print(f"Issue Type: {context1['issue_type']}")
print(f"Has History: {context1['has_history']}")

# Example 2: Employment Issue
print("\n" + "=" * 60)
print("Example 2: Employment Issue")
print("=" * 60)

query2 = "Can I take legal action?"
history2 = ["My boss fired me without notice or severance"]

enriched2 = enrich_query(query2, history2)
print("\nRaw Input:")
print(f"Query: '{query2}'")
print(f"History: {history2}")
print("\nEnriched Output:")
print(enriched2)

context2 = extract_case_context(query2, history2)
print("\nExtracted Context:")
print(f"Issue Type: {context2['issue_type']}")

# Example 3: No History (query alone)
print("\n" + "=" * 60)
print("Example 3: No History")
print("=" * 60)

query3 = "What are my rights under Article 32?"
enriched3 = enrich_query(query3, None)
print("\nRaw Input:")
print(f"Query: '{query3}'")
print(f"History: None")
print("\nEnriched Output:")
print(enriched3)

# Example 4: Cybercrime
print("\n" + "=" * 60)
print("Example 4: Cybercrime")
print("=" * 60)

query4 = "How do I report this?"
history4 = ["I received a phishing email asking for my bank OTP"]

enriched4 = enrich_query(query4, history4)
print("\nRaw Input:")
print(f"Query: '{query4}'")
print(f"History: {history4}")
print("\nEnriched Output:")
print(enriched4)

context4 = extract_case_context(query4, history4)
print("\nExtracted Context:")
print(f"Issue Type: {context4['issue_type']}")
