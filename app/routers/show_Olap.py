from fastapi import APIRouter, HTTPException;
from pydantic import BaseModel
from app.neo4j.neo4j_config import query

router = APIRouter()

class SelectionRequest(BaseModel):
    selected: list[str]

@router.post("/fact-combined")
async def query_fact_combined(request: SelectionRequest):
    selected = request.selected
    match_clauses = ["MATCH (f:FactTable)"]

    return_fields = []
    groupby_fields = []

    if any(x in selected for x in ["Year", "Month", "Day"]):
        match_clauses.append(
            "MATCH (f:FactTable)-[:ON_DAY]->(d)-[:BELONGS_TO]->(m:Month)-[:BELONGS_TO]->(y:Year)"
        )
        if "Year" in selected:
            return_fields.append("y.value AS Year")       
            groupby_fields.append("Year")
        if "Month" in selected:
            return_fields.append("m.value AS Month")
            groupby_fields.append("Month")  
        if "Day" in selected:
            return_fields.append("d.value AS Day")
            groupby_fields.append("Day")

    if any(x in selected for x in ["Country", "City", "Shop"]):
        match_clauses.append(
            "MATCH (f)-[:AT_SHOP]->(s)<-[:HAS_SHOP]-(ci:City)-[:LOCATED_IN]->(co:Country)"
        )
        if "Country" in selected:
            return_fields.append("co.name AS Country")
            groupby_fields.append("Country")
        if "City" in selected:
            return_fields.append("ci.name AS City")
            groupby_fields.append("City")
        if "Shop" in selected:
            return_fields.append("s.name AS Shop")
            groupby_fields.append("Shop")

    if any(x in selected for x in ["Category", "Pizza Name"]):
        match_clauses.append(
            "MATCH (f)-[:FOR_PRODUCT]->(p)-[:BELONGS_TO]->(cat:Category)"
        )
        if "Category" in selected:
            return_fields.append("cat.name AS Category")
            groupby_fields.append("Category")
        if "Pizza Name" in selected:
            return_fields.append("p.name AS Pizza")
            groupby_fields.append("Pizza")

    return_fields.append("SUM(f.total_quantity) AS TotalQuantity")
    return_fields.append("SUM(f.total_price) AS Revenue")

    cypher_query = "\n".join(match_clauses) + f"\nRETURN {', '.join(return_fields)}"
    if groupby_fields:
        cypher_query += f"\nORDER BY {', '.join(groupby_fields)}"

    result = query(cypher_query)
    data = [record.data() for record in result]


    return {
        "selected": selected,
        "cypher": cypher_query,
        "result": data
    }