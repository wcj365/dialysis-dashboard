"""
Created on Sat Jul 13 09:34:46 2019

@author: jay
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

import pathlib
import pandas as pd
import plotly_express as px

# get relative data folder
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

dataset = "DialysisCareQualityData2.csv"
df = pd.read_csv(DATA_PATH.joinpath(dataset))

df=df.dropna()

df["FacilityInfo"] = df["Name"] + ", " + df["City"] + ", " + df["StateCode"]

df["Network"] = "No. " + df["Network"].astype(str)
df["UnemploymentRate"] = df["UnemploymentRate"].astype(float)  
df["PctgBlackACS"] = df["PctgBlackACS"].astype(float) 
df["PctgHispanicACS"] = df["PctgHispanicACS"].astype(float) 
df["PctgFamilyBelowFPL"] = df["PctgFamilyBelowFPL"].astype(float) 
df["PctgPoorEnglish"] = df["PctgPoorEnglish"].astype(float)            

df["StaffPatientRatio"] = df["TotalStaff"] / df["TotalPatients"]
df["StationPatientRatio"] = df["TotalStations"] / df["TotalPatients"]

srr_options= {
    'Staff Patient Ratio (Facility)': 'StaffPatientRatio',
    'Station Patient Ratio (Facility)': 'StationPatientRatio',
    '% Black (Facility)': 'PctgBlack',
    '% Hispanic (Facility)': 'PctgHispanic',
    '% Black (Community)': 'PctgBlackACS',
    '% Hispanic (Community)': 'PctgHispanicACS',
    '% Poor English (Community)': 'PctgPoorEnglish',
    'Unemployment Rate (Community)': 'UnemploymentRate',
    'Poverty Rate (Community)': 'PctgFamilyBelowFPL'
}


color_options = {
    'Census Region': 'Region',
    'Census Division': 'Division',
    'ESRD Network': 'Network',
    'Facility Profit Status': 'ProfitStatus',
    'Facility Hospital Affiliation': 'HospitalAffiliation',
    'State': 'StateCode'
}

external_css = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_css)

#app.config['suppress_callback_exceptions']=True


app.layout = html.Div([
    html.Div([
        html.H2(children="Dialysis Dashboard"),
        html.H5(children='Explore Socioeconomic Factors of Unplanned Hospital Readmission.'),
        ], 
        className="ten columns", 
        style = {'padding' : '10px' , 'backgroundColor' : 'tomato'}
    ),
            
    html.Div([
        html.Img(
            src=app.get_asset_url('KidneyCare.jpg'),
            className='two columns',
            style={
                'height': '15%',
                'width': '15%',
                'float': 'right',
                'position': 'relative',
               # 'margin-top': 1,
            }
        )
    ]),
        
    html.Br(),
    html.Br(),
    html.Br(),
    
    html.Div([
                           
       html.Div([
            html.Label("Figure Arrangement: ", style={'padding' : '10px',"display" : "inline-block", "padding-right" : "4px"}),
            dcc.Dropdown(
                id="choice_var",
                options=[
                    {'label': 'Vertical', 'value': 'stack'},
                    {'label': 'Horizontal', 'value': 'side'}
                ],
                value='stack',
                clearable=False
            )
         ], className="three columns"),
 
       html.Div([
            html.Label("Socioeconomic Risk Factors: ", style={'padding' : '10px',"display" : "inline-block", "padding-right" : "4px"}),
            dcc.Dropdown(
                id="x_var",
                options=[{'label':dict_key, 'value': dict_value} for dict_key, dict_value in srr_options.items()],
                value='StaffPatientRatio',
                clearable=False,
                style={"margin-top" : "4px"}
            )
        ], className="three columns"),
            
        html.Div([   
            html.Label("Facility Stratification: ", style={'padding' : '10px',"display" : "inline-block", "padding-right" : "4px"}),                        
            dcc.Dropdown(
                id="color_var",
                options=[{'label':dict_key, 'value':dict_value} for dict_key, dict_value in color_options.items()],
                clearable=False,
                value='Region'
            )
        ], className="three columns"), 
        
    ], className="row") ,
        
    html.Div([
        html.Div([
            dcc.Graph(id="scatter_graph", style={"width": "100%", "height": "100%", "display": "inline-block"}),
            ],
            id="scatter_div", 
            className="row"  
        ),

        html.Div([
            dcc.Graph(id="histogram_graph", style={"width": "100%", "height": "100%", "display": "inline-block"}),
           ] ,
            id="histo_div", 
           className="row"  
        ),
    
        html.Div([
            dcc.Graph(id="histogram2_graph", style={"width": "100%", "height": "100%", "display": "inline-block"}),
           ] ,
            id="histo2_div", 
            className="row"  
        )],

        className="row"  
    ),               
    
    html.Div([
        dash_table.DataTable(
            id="table",
            columns=[{"name":i,"id": i} for i in df.columns],
            data=df.to_dict("records"),
            page_current = 0,
            page_size = 10,
        )
    ]),

    html.H6("Endnote: This is developed using Python:"),
    html.H6("1. Pandas for data preprocessing;"),
    html.H6("2. Plotly Express for interactive Data visualization;"),
    html.H6("3. Dash for web-based dashboarding.")        
])


@app.callback([Output("scatter_div", "className"), Output("histo_div","className"), Output("histo2_div","className")],
              [Input('choice_var', 'value')] )
def change_layout(choice_selected):
    if choice_selected =="side":
        return "four columns", "four columns", "four columns"
    else:
        return "row", "row", "row"
   
@app.callback([Output("scatter_graph", "figure"), Output("histogram_graph","figure"), Output("histogram2_graph","figure")],
              [Input('x_var', 'value'),Input('color_var','value')] )
def make_figure(x_selected, color_selected):
 
    fig1 = px.scatter(
        df,
        x=x_selected,
        y="SRR",
        trendline="ols",
        hover_name="FacilityInfo",
#        height=1000,
        opacity=1,
        color=color_selected
    )
    
    fig2 = px.histogram(
        df,
#        orientation="h",
        x=color_selected,
        y="SRR",
        histfunc="avg",
        color=color_selected,
        hover_name="FacilityInfo"
 #       height=1000
    ).update_xaxes(categoryorder="mean ascending")

      
    fig3 = px.histogram(
        df,
#        orientation="h",
        x=color_selected,
        y=x_selected,
        histfunc="avg",
        color=color_selected,
        hover_name="FacilityInfo"
 #       height=1000
    ).update_xaxes(categoryorder="mean ascending")  

    return fig1, fig2, fig3
 
if __name__ == '__main__':
    app.run_server(debug=True)