from langchain_core.tools import Tool, StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
from tools_utils import (
    get_data_from_sql,
    chart_building
)


class SQLQueryInput(BaseModel):
    sql_query: str = Field(description="SQL query to execute")


class PlotInput(BaseModel):
    csv_file_path: str = Field(description="Path to the CSV file containing the data for the plot")
    plot_type: str = Field(description="Plot type. Choose value: line, bar, scatter, hist, boxplot, pie")
    x_axis: str = Field(description="Name of data column for X-axis")
    y_axis: Optional[str] = Field(description="Name of data column for y-axis. May be None")


with open("utils/prompts/sql_tool_prompt.txt", "r", encoding="utf-8") as f:
    sql_description = f.read()
with open("utils/prompts/plot_tool_prompt.txt", "r", encoding="utf-8") as f:
    plot_description = f.read()

sql_tool = Tool(
    name="get_data_from_sql",
    func=get_data_from_sql,
    description=sql_description,
    args_schema=SQLQueryInput,
)

plot_tool = StructuredTool.from_function(
    name="chart_building",
    func=chart_building,
    description=plot_description,
    args_schema=PlotInput,
)

tools = [sql_tool, plot_tool]
