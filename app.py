import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from database import init_db,products_df,sales_df,expenses_df,add_product,add_sale,add_expense
from ml_model import train_forecast,product_recommendations
from ai_assistant import answer

st.set_page_config(page_title="ShopMind AI",page_icon="🧠",layout="wide")
init_db()
st.title("ShopMind AI")
st.caption("Python + AI/ML shop management assistant")

p=products_df(); s=sales_df(); e=expenses_df()
revenue=float(s["total"].sum()) if not s.empty else 0
cost=float((s["quantity"]*s["purchase_price"]).sum()) if not s.empty else 0
expenses=float(e["amount"].sum()) if not e.empty else 0
profit=revenue-cost-expenses

c1,c2,c3,c4=st.columns(4)
c1.metric("Total Sales",f"₹{revenue:,.0f}")
c2.metric("Estimated Profit",f"₹{profit:,.0f}")
c3.metric("Products",len(p))
c4.metric("Low Stock",len(product_recommendations(p,s)))

tab1,tab2,tab3,tab4=st.tabs(["Dashboard","Inventory","Add Sale","AI Assistant"])

with tab1:
    st.subheader("Sales Trend")
    if not s.empty:
        daily=s.groupby("sale_date",as_index=True)["total"].sum()
        st.line_chart(daily)
    pred=train_forecast(s)
    if pred is not None:
        st.info(f"ML forecast: next day's total item quantity ≈ {pred:.0f} units")
    st.subheader("Reorder Recommendations")
    rec=product_recommendations(p,s)
    st.dataframe(pd.DataFrame(rec) if rec else pd.DataFrame({"Message":["No urgent reorder"]}),use_container_width=True)

with tab2:
    st.dataframe(p,use_container_width=True)
    with st.expander("Add New Product"):
        with st.form("product"):
            n=st.text_input("Product name"); cat=st.text_input("Category")
            buy=st.number_input("Purchase price",min_value=0.0)
            sell=st.number_input("Selling price",min_value=0.0)
            stock=st.number_input("Opening stock",min_value=0,step=1)
            minimum=st.number_input("Minimum stock",min_value=0,step=1,value=5)
            supplier=st.text_input("Supplier")
            if st.form_submit_button("Save"):
                try:
                    add_product(n,cat,buy,sell,stock,minimum,supplier); st.success("Product added"); st.rerun()
                except Exception as ex: st.error(str(ex))

with tab3:
    options={f'{r["name"]} (stock {r["stock"]})':r["id"] for _,r in p.iterrows()}
    if options:
        with st.form("sale"):
            selected=st.selectbox("Product",list(options))
            qty=st.number_input("Quantity",min_value=1,step=1)
            price=st.number_input("Selling price (0 = product price)",min_value=0.0)
            if st.form_submit_button("Record Sale"):
                try:
                    pid=options[selected]; add_sale(pid,qty,None if price==0 else price)
                    st.success("Sale recorded and stock updated"); st.rerun()
                except Exception as ex: st.error(str(ex))
    else: st.warning("Add a product first.")

with tab4:
    st.subheader("Ask ShopMind")
    st.caption("Try: 'Maggi ka stock kitna hai?' / 'kaunsa stock kam hai?' / 'profit kitna hai?'")
    msg=st.chat_input("Shop ke baare mein poochho...")
    if msg:
        st.chat_message("user").write(msg)
        st.chat_message("assistant").write(answer(msg))

