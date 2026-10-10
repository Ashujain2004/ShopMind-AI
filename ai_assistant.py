import os
from database import products_df,sales_df,expenses_df
from ml_model import product_recommendations

def local_answer(message):
    msg=message.lower()
    p=products_df(); s=sales_df(); e=expenses_df()
    if "stock" in msg:
        return "Current stock: "+(", ".join(f'{r["name"]}: {r["stock"]}' for _,r in p.iterrows()) if not p.empty else "empty")
    if "low" in msg or "kam" in msg or "khatam" in msg:
        r=product_recommendations(p,s)
        return "Low/urgent stock: "+(", ".join(x["product"] for x in r) if r else "koi nahi")
    if "sale" in msg or "sales" in msg:
        return f"Recorded sales total ₹{s['total'].sum():,.0f} hai."
    if "profit" in msg or "munafa" in msg:
        revenue=s["total"].sum()
        cost=(s["quantity"]*s["purchase_price"]).sum()
        expense=e["amount"].sum()
        return f"Estimated gross profit ₹{revenue-cost-expense:,.0f} hai."
    return "Main stock, sales, profit aur reorder ke baare mein bata sakta hoon. Example: 'kaunsa stock kam hai?'"

def answer(message):
    key=os.getenv("OPENAI_API_KEY")
    if not key:
        return local_answer(message)
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        p=products_df().to_dict("records")
        s=sales_df().to_dict("records")
        e=expenses_df().to_dict("records")
        prompt=f"""You are ShopMind AI for an Indian small shop. Answer in simple Hinglish.
Never invent data. Use only this shop data.
Products={p}
Sales={s}
Expenses={e}
User={message}
Give a concise useful answer."""
        r=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-5.6-mini"),input=prompt)
        return r.output_text
    except Exception:
        return local_answer(message)
