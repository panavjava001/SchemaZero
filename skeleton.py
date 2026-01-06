import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field

# loading env vars locally
# from dotenv import load_dotenv
# load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# defining the output structure we want
class InvoiceData(BaseModel):
    invoice_id: str
    vendor_name: str
    total_amount: float
    currency: str = Field(description="ISO code like USD or AUD")
    items: list[str]

#use o1 to look at the document and plan the schema
#rn just simulating the reasoning part because o1 api is slow
def plan_schema(doc_text):
    print("Architect: reading document...")
    
    # prompt = "Analyze this file and give me a json schema..."
    # response = client.chat.completions.create(model="o1-preview", messages=[...])
    
    # mimicking what o1 would return after thinking
    return {
        "target_table": "invoices_2025",
        "required_fields": ["id", "vendor", "total"],
        "notes": "Looks like a standard tax invoice"
    }

#use 4o to actually grab the data using the plan
def extract_data(schema_plan, text_chunk):
    print(f"Worker: extracting data for {schema_plan['target_table']}...")
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Extract info based on this structure."},
                {"role": "user", "content": text_chunk}
            ],
            response_format=InvoiceData,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"Extraction failed: {e}")
        return None

#testing the flow
if __name__ == "__main__":
    # dummy file content
    test_file = "Invoice #INV-992 from Amazon AWS. Total: $45.00 USD"
    
    print("running schema zero prototype...")
    
    plan = plan_schema(test_file)
    result = extract_data(plan, test_file)
    
    if result:
        print("\n--- Result ---")
        print(f"Vendor: {result.vendor_name}")
        print(f"Total: {result.total_amount} {result.currency}")
        # print(result.model_dump_json())
