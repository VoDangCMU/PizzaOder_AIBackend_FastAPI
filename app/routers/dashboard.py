from fastapi import APIRouter
from app.neo4j.neo4j_config import query
from fastapi import APIRouter
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
from datetime import datetime
router = APIRouter()

@router.get("/revenue-by-month")
def get_monthly_revenue():
    cypher_query = """
    MATCH (f:FactTable)-[:ON_DAY]->(d:Day)
    RETURN d.year AS year, d.month AS month, SUM(f.total_price) AS total_revenue
    ORDER BY year, month
    """
    result = query(cypher_query)
    return result

def describe_cluster(row):
    desc = []
    if row["avg_total_price"] > 300:
        desc.append("Chi tiêu cao")
    elif row["avg_total_price"] < 100:
        desc.append("Chi tiêu thấp")

    if row["avg_categories"] >= 2:
        desc.append("Thử nhiều loại pizza")
    else:
        desc.append("Trung thành 1-2 loại")

    if row["avg_unique_pizzas"] >= 3:
        desc.append("Mua nhiều loại pizza mỗi lần")
    else:
        desc.append("Chỉ chọn vài món quen thuộc")

    return ", ".join(desc)

@router.get("/sales-overview")
def sales_overview():
    cypher_query = """
    MATCH (o:Order)-[:CONTAINS]->(p:Pizza),
          (o)-[:ORDERED_ON]->(d:Day),
          (o)-[:DELIVERED_TO]->(ci:City),
          (p)-[:BELONGS_TO]->(cat:Category)
    RETURN 
        SUM(o.total_price) AS total_sales,
        SUM(o.quantity) AS total_quantity,
        COUNT(DISTINCT p.name) AS num_items,
        COUNT(DISTINCT cat.name) AS category_count,
        p.name AS pizza_name
    """
    
    result = query(cypher_query)
    
    if not result:
        return {"message": "Không có dữ liệu từ cơ sở dữ liệu."}

    data = []
    for r in result:
        try:
            if None in r.values():
                continue
            data.append({
                "total_sales": r["total_sales"],
                "total_quantity": r["total_quantity"],
                "num_items": r["num_items"],
                "category_count": r["category_count"],
                "pizza_name": r["pizza_name"]
            })
        except Exception as e:
            continue

    df = pd.DataFrame(data)
    df = df.dropna()  

    if df.shape[0] < 1:
        return {"message": "Không đủ dữ liệu để tính tổng quan doanh thu."}

    total_sales = df["total_sales"].sum()
    total_quantity = df["total_quantity"].sum()
    num_items = df["num_items"].sum()
    category_count = df["category_count"].sum()

    top_selling_pizza = df.groupby("pizza_name").agg(
        total_sales=('total_sales', 'sum'),
        total_quantity=('total_quantity', 'sum')
    ).reset_index()

    top_selling_pizza = top_selling_pizza.sort_values(by="total_quantity", ascending=False)

    top_selling_pizza = top_selling_pizza.applymap(lambda x: x.item() if isinstance(x, np.generic) else x)

    return {
        "total_sales": int(total_sales), 
        "total_quantity": int(total_quantity), 
        "num_items": int(num_items),  
        "category_count": int(category_count), 
        "top_selling_pizza": top_selling_pizza.to_dict(orient="records")
    }

# @router.get("/cluster-orders")
# def cluster_orders():
#     cypher_query = """
#     MATCH (o:Order)-[:CONTAINS]->(p:Pizza),
#           (o)-[:ORDERED_ON]->(d:Day),
#           (o)-[:DELIVERED_TO]->(ci:City),
#           (p)-[:BELONGS_TO]->(cat:Category)
#     RETURN 
#         o.order_id AS order_id,
#         SUM(o.total_price) AS total_price,
#         SUM(o.quantity) AS quantity,
#         COUNT(DISTINCT p.name) AS num_items,
#         COUNT(DISTINCT cat.name) AS category_count,
#         d.value AS day, d.month AS month, d.year AS year,
#         ci.name AS city
#     """
#     result = query(cypher_query)

#     data = []
#     for r in result:
#         try:
#             if None in r.values():
#                 continue
#             data.append({
#                 "order_id": r["order_id"],
#                 "total_price": r["total_price"],
#                 "quantity": r["quantity"],
#                 "num_items": r["num_items"],
#                 "category_count": r["category_count"],
#                 "day": r["day"],
#                 "month": r["month"],
#                 "year": r["year"],
#                 "city": r["city"]
#             })
#         except:
#             continue

#     df = pd.DataFrame(data)
#     df = df.dropna()

#     if df.shape[0] < 3:
#         return {"message": "Không đủ dữ liệu để phân cụm."}

#     df["city_encoded"] = pd.factorize(df["city"])[0]

#     features = [
#         "total_price", "quantity", "num_items", "category_count",
#         "day", "month", "year", "city_encoded"
#     ]
#     X = df[features]

#     kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
#     df["cluster"] = kmeans.fit_predict(X)

#     def describe_cluster(row):
#         desc = []
#         if row["avg_total_price"] > 300:
#             desc.append("--------Chi tiêu cao")
#         elif row["avg_total_price"] < 100:
#             desc.append("--------Chi tiêu thấp")
#         else:
#             desc.append("--------Chi tiêu trung bình")

#         if row["avg_categories"] >= 2:
#             desc.append("Thử nhiều loại pizza")
#         else:
#             desc.append("Trung thành 1-2 loại")

#         if row["avg_unique_pizzas"] >= 3:
#             desc.append("Mỗi đơn mua nhiều loại pizza")
#         else:
#             desc.append("Chỉ vài món cố định")

#         return ", ".join(desc)

#     summary = df.groupby("cluster")[features].agg(["mean", "count"]).reset_index()

#     summary_dict = []
#     for _, row in summary.iterrows():
#         cluster_id = row["cluster"]
#         count = int(row[("total_price", "count")])
#         avg_price = round(row[("total_price", "mean")], 2)
#         avg_quantity = round(row[("quantity", "mean")], 2)
#         avg_items = round(row[("num_items", "mean")], 2)
#         avg_categories = round(row[("category_count", "mean")], 2)

#         description = describe_cluster({
#             "avg_total_price": avg_price,
#             "avg_quantity": avg_quantity,
#             "avg_unique_pizzas": avg_items,
#             "avg_categories": avg_categories
#         })

#         summary_dict.append({
#             "cluster": int(cluster_id),
#             "cluster_size": count,
#             "avg_total_price": avg_price,
#             "avg_quantity": avg_quantity,
#             "avg_unique_pizzas": avg_items,
#             "avg_categories": avg_categories,
#             "insight": description
#         })

#     return {
#         "cluster_summary": summary_dict,
#         "orders": df.to_dict(orient="records")
#     }

@router.get("/cluster-orders")
def cluster_orders():
    cypher_query = """
    MATCH (o:Order)-[:CONTAINS]->(p:Pizza),
          (o)-[:ORDERED_ON]->(d:Day),
          (o)-[:DELIVERED_TO]->(ci:City),
          (p)-[:BELONGS_TO]->(cat:Category)
    RETURN 
        COUNT(o.order_id) AS order_count,
        SUM(o.total_price) AS total_price,
        SUM(o.quantity) AS quantity,
        COUNT(DISTINCT p.name) AS num_items,
        COUNT(DISTINCT cat.name) AS category_count,
        d.value AS day, d.month AS month, d.year AS year,
        ci.name AS city
    """
    result = query(cypher_query)

    data = []
    for r in result:
        try:
            if None in r.values():
                continue
            data.append({
                "order_count": r["order_count"],
                "total_price": r["total_price"],
                "quantity": r["quantity"],
                "num_items": r["num_items"],
                "category_count": r["category_count"],
                "day": r["day"],
                "month": r["month"],
                "year": r["year"],
                "city": r["city"]
            })
        except:
            continue

    df = pd.DataFrame(data)
    df = df.dropna()

    if df.shape[0] < 3:
        return {"message": "Không đủ dữ liệu để phân cụm."}

    df["city_encoded"] = pd.factorize(df["city"])[0]

    features = [
        "total_price", "quantity", "num_items", "category_count",
        "day", "month", "year", "city_encoded"
    ]
    X = df[features]

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X)

    def describe_cluster(row):
        desc = []
        if row["avg_total_price"] > 300:
            desc.append("--------Chi tiêu cao")
        elif row["avg_total_price"] < 100:
            desc.append("--------Chi tiêu thấp")
        else:
            desc.append("--------Chi tiêu trung bình")

        if row["avg_categories"] >= 2:
            desc.append("Thử nhiều loại pizza")
        else:
            desc.append("Trung thành 1-2 loại")

        if row["avg_unique_pizzas"] >= 3:
            desc.append("Mỗi đơn mua nhiều loại pizza")
        else:
            desc.append("Chỉ vài món cố định")

        return ", ".join(desc)

    summary = df.groupby("cluster")[features].agg(["mean", "count"]).reset_index()

    summary_dict = []
    for _, row in summary.iterrows():
        cluster_id = row["cluster"]
        count = int(row[("total_price", "count")])
        avg_price = round(row[("total_price", "mean")], 2)
        avg_quantity = round(row[("quantity", "mean")], 2)
        avg_items = round(row[("num_items", "mean")], 2)
        avg_categories = round(row[("category_count", "mean")], 2)

        description = describe_cluster({
            "avg_total_price": avg_price,
            "avg_quantity": avg_quantity,
            "avg_unique_pizzas": avg_items,
            "avg_categories": avg_categories
        })

        summary_dict.append({
            "cluster": int(cluster_id),
            "cluster_size": count,
            "avg_total_price": avg_price,
            "avg_quantity": avg_quantity,
            "avg_unique_pizzas": avg_items,
            "avg_categories": avg_categories,
            "insight": description
        })

    return {
        "cluster_summary": summary_dict,
        "orders_count": df.groupby("cluster")["order_count"].sum().to_dict()
    }


# @router.get("/cluster-orders")
# def cluster_orders():
#     cypher_query = """
#     MATCH (o:Order)-[:CONTAINS]->(p:Pizza),
#           (o)-[:ORDERED_ON]->(d:Day),
#           (o)-[:DELIVERED_TO]->(ci:City),
#           (p)-[:BELONGS_TO]->(cat:Category)
#     RETURN 
#         COUNT(o.order_id) AS order_count,
#         SUM(o.total_price) AS total_price,
#         SUM(o.quantity) AS quantity,
#         COUNT(DISTINCT p.name) AS num_items,
#         COUNT(DISTINCT cat.name) AS category_count,
#         d.value AS day, d.month AS month, d.year AS year,
#         ci.name AS city,
#         p.name AS pizza_name
#     """
    
#     try:
#         result = query(cypher_query)
#         if not result:
#             return {"message": "Không có dữ liệu trả về từ cơ sở dữ liệu."}
#     except Exception as e:
#         return {"message": f"Lỗi khi truy vấn cơ sở dữ liệu: {str(e)}"}

#     data = []
#     for r in result:
#         try:
#             if None in r.values():
#                 continue
#             data.append({
#                 "order_count": r["order_count"],
#                 "total_price": r["total_price"],
#                 "quantity": r["quantity"],
#                 "num_items": r["num_items"],
#                 "category_count": r["category_count"],
#                 "day": r["day"],
#                 "month": r["month"],
#                 "year": r["year"],
#                 "city": r["city"],
#                 "pizza_name": r["pizza_name"]
#             })
#         except Exception as e:
#             continue

#     df = pd.DataFrame(data)
#     df = df.dropna()  # Loại bỏ các dòng có giá trị NaN

#     if df.shape[0] < 3:
#         return {"message": "Không đủ dữ liệu để phân cụm."}

#     # Đảm bảo 'city' được mã hóa đúng cách
#     df["city_encoded"] = pd.factorize(df["city"])[0]

#     features = [
#         "total_price", "quantity", "num_items", "category_count",
#         "day", "month", "year", "city_encoded"
#     ]
#     X = df[features]

#     # Áp dụng phân cụm KMeans
#     kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
#     df["cluster"] = kmeans.fit_predict(X)

#     def describe_cluster(row):
#         desc = []
#         if row["avg_total_price"] > 300:
#             desc.append("--------Chi tiêu cao")
#         elif row["avg_total_price"] < 100:
#             desc.append("--------Chi tiêu thấp")
#         else:
#             desc.append("--------Chi tiêu trung bình")

#         if row["avg_categories"] >= 2:
#             desc.append("Thử nhiều loại pizza")
#         else:
#             desc.append("Trung thành 1-2 loại")

#         if row["avg_unique_pizzas"] >= 3:
#             desc.append("Mỗi đơn mua nhiều loại pizza")
#         else:
#             desc.append("Chỉ vài món cố định")

#         return ", ".join(desc)

#     summary = df.groupby("cluster")[features].agg(["mean", "count"]).reset_index()

#     summary_dict = []
#     for _, row in summary.iterrows():
#         cluster_id = row["cluster"]
#         count = int(row[("total_price", "count")])
#         avg_price = round(row[("total_price", "mean")], 2)
#         avg_quantity = round(row[("quantity", "mean")], 2)
#         avg_items = round(row[("num_items", "mean")], 2)
#         avg_categories = round(row[("category_count", "mean")], 2)

#         description = describe_cluster({
#             "avg_total_price": avg_price,
#             "avg_quantity": avg_quantity,
#             "avg_unique_pizzas": avg_items,
#             "avg_categories": avg_categories
#         })

#         # Reset index to avoid issues with comparison
#         df = df.reset_index(drop=True)

#         # Ensure that 'cluster' column is of type integer
#         df["cluster"] = df["cluster"].astype(int)

#         # Now filter the DataFrame based on the cluster_id
#         cluster_data = df[df["cluster"] == cluster_id]

#         # Tính toán top pizza bán chạy nhất
#         most_ordered_pizza = cluster_data.groupby("pizza_name")["order_count"].sum().idxmax()

#         # Tính toán ngày/tháng bán chạy nhất
#         popular_day = cluster_data["day"].mode()[0]
#         popular_month = cluster_data["month"].mode()[0]
#         popular_year = cluster_data["year"].mode()[0]

#         summary_dict.append({
#             "cluster": int(cluster_id),
#             "cluster_size": count,
#             "avg_total_price": avg_price,
#             "avg_quantity": avg_quantity,
#             "avg_unique_pizzas": avg_items,
#             "avg_categories": avg_categories,
#             "insight": description,
#             "most_ordered_pizza": most_ordered_pizza,
#             "popular_day": int(popular_day),
#             "popular_month": int(popular_month),
#             "popular_year": int(popular_year)
#         })

#     return {
#         "cluster_summary": summary_dict,
#         "orders_count": df.groupby("cluster")["order_count"].sum().to_dict()
#     }
