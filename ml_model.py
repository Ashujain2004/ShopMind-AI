from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

MODEL_PATH=Path(__file__).parent/"models"/"sales_forecast.pkl"

def train_forecast(sales_df):
    if sales_df.empty:
        return None
    daily=sales_df.groupby("sale_date",as_index=False)["quantity"].sum()
    daily["date"]=pd.to_datetime(daily["sale_date"])
    daily=daily.sort_values("date")
    if len(daily)<4:
        return None
    daily["day_index"]=np.arange(len(daily))
    daily["dow"]=daily["date"].dt.dayofweek
    X=daily[["day_index","dow"]]
    y=daily["quantity"]
    model=RandomForestRegressor(n_estimators=150,random_state=42)
    model.fit(X,y)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model,MODEL_PATH)
    next_day=len(daily)
    dow=(daily["date"].max()+pd.Timedelta(days=1)).dayofweek
    pred=max(0,float(model.predict([[next_day,dow]])[0]))
    return pred

def product_recommendations(products,sales):
    out=[]
    if products.empty: return out
    for _,p in products.iterrows():
        s=sales[sales["product_id"]==p["id"]]
        if s.empty:
            avg=0
        else:
            avg=float(s["quantity"].sum()/max(1,s["sale_date"].nunique()))
        days=(p["stock"]/avg) if avg else 999
        reorder=max(0,int(round(avg*7-p["stock"])))
        if p["stock"]<=p["min_stock"] or days<3:
            out.append({"product":p["name"],"stock":int(p["stock"]),
                         "avg_daily":round(avg,2),"days_left":round(days,1),
                         "recommended_reorder":reorder})
    return out
