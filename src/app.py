# Import required libraries
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, State
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import iplot
from dash import no_update
import jupyter_dash
from jupyter_dash import JupyterDash

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
mpl.style.use('ggplot')

import sort_dataframeby_monthorweek as sd

# Create a dash application
app = jupyter_dash.JupyterDash(__name__)

# Server
server = app.server

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the cleaned hotel data into pandas dataframe
df_hotel = pd.read_csv("hotel_bookings_cleaned.csv")

"""Compute graph data for creating hotel bookings report 

Function that takes hotel data as input and create dataframes based on the grouping condition
to be used for plottling charts and graphs.

Argument:
     
    df_hotel: Filtered dataframe
    
Returns:
   Dataframes to create graph. 
"""

def compute_data_choice_1(df_hotel):
    
    # df with only not cancelled (nc) bookings
    df_hotel_nc = df_hotel[df_hotel['is_canceled']==0]
    
    # Mean monthly price per hotel type (over the year)
    df_hotel_nc_mean_price = df_hotel_nc.groupby('arrival_date_month')['adr'].mean().reset_index()
    df_hotel_nc_mean_price.columns = ['Month','Monthly Price']
    df_hotel_nc_mean_price_ord = sd.Sort_Dataframeby_Month(df_hotel_nc_mean_price, 'Month')
    
    # Nr of bookings per month per hotel type
    df_monthly_bookings = df_hotel['arrival_date_month'].value_counts().to_frame().reset_index()
    df_monthly_bookings.columns = ['Month','Nr of Bookings']
    df_monthly_bookings_ord = sd.Sort_Dataframeby_Month(df_monthly_bookings, 'Month')
    
    # Nr bookings per nights of stay per hotel type
    df_hotel_nc['Total_nights'] = df_hotel_nc['stays_in_weekend_nights'] + df_hotel_nc['stays_in_week_nights']
    df_stays = df_hotel_nc.groupby('Total_nights').agg('count').reset_index()
    df_stays = df_stays.iloc[:,0:2]
    df_stays.columns = ['Total nights', 'Nr of stays']
    
    # Nr of bookings per market segment
    df_market = df_hotel_nc['market_segment'].value_counts().to_frame().reset_index()
    df_market.columns = ['Market segment', 'Nr of bookings']

    # Nr reservations / cancellations per hotel type
    df_canc_res = df_hotel.groupby('is_canceled').agg('count').reset_index()
    df_canc_res = df_canc_res.iloc[:,0:2]
    df_canc_res.columns = ['Reservation Cancellation', 'Count']
    
    return df_hotel_nc_mean_price_ord, df_monthly_bookings_ord, df_stays, df_market, df_canc_res

def compute_data_choice_2(df_hotel):
    
    # df with only not cancelled (nc) bookings
    df_hotel_nc = df_hotel[df_hotel['is_canceled']==0]
    
    # Nr of guests per month per hotel type
    df_hotel_nc['Tot_guests_per_booking'] = df_hotel_nc[['adults', 'children', 'babies']].sum(axis=1)
    df_guests_month = df_hotel_nc.groupby('arrival_date_month')['Tot_guests_per_booking'].sum().to_frame().reset_index()
    df_guests_month.columns = ['Month', 'Total guests']
    df_guests_month = sd.Sort_Dataframeby_Month(df_guests_month, 'Month')
    
    # Nr of bookings per nr of special request per cancelled/not cancelled
    df_cancel_req = df_hotel.groupby('total_of_special_requests')['is_canceled'].value_counts().to_frame()
    df_cancel_req.columns = ['Nr of bookings']
    df_cancel_req = df_cancel_req.reset_index()
    df_cancel_req.columns = ['Special requests', 'Cancelled (1)/Not cancelled (0)', 'Nr of bookings']
    df_cancel_req['Cancelled (1)/Not cancelled (0)'] = df_cancel_req['Cancelled (1)/Not cancelled (0)'].astype(str)
    
    # Nr of bookings per nr of special requests per reserved room type
    df_room_req = df_hotel.groupby('total_of_special_requests')['reserved_room_type'].value_counts().to_frame()
    df_room_req.columns = ['Nr of bookings']
    df_room_req = df_room_req.reset_index()
    df_room_req.columns = ['Special requests', 'Room type', 'Nr of bookings']
    
    # Preferred meal types per room types
    df_meal_room = df_hotel_nc.groupby('meal')['reserved_room_type'].value_counts().to_frame()
    df_meal_room.columns = ['Nr of preferences']
    df_meal_room.index.name = 'meal_type'
    df_meal_room = df_meal_room.reset_index()
    df_meal_room.columns = ['Meal', 'Room type', 'Nr of preferences']
    
    # Origin countries of guests
    df_map = df_hotel_nc['country'].value_counts().reset_index()
    df_map.columns = ['Country', 'Guests']
    
    return df_guests_month, df_cancel_req, df_room_req, df_meal_room, df_map

# Application layout
app.layout = html.Div(children=[ 
                                # Add title to the dashboard
                                html.H1('Hotel analysis',
                                    style={'textAlign':'center', 'font-size':30,
                                            'backgroundColor':'#01386a','color':'snow',
                                            'font-family': 'Tahoma, sans-serif'}),
    
                                # Tabs creation
                                # Create an outer division 
                                html.Div([
                                    # Add an inner division
                                    html.Div([
                                        # Create an division for adding dropdown helper text for report type
                                        dcc.Tabs(id="input-type", value='OPT1',
                                                 children=[
                                            dcc.Tab(label='Hotel Bookings analysis', value='OPT1',
                                                   style={'font-size': '20px', 
                                                          'backgroundColor':'#01386a',
                                                          'color':'snow',
                                                          'font-family':'Tahoma, sans-serif'}),
                                            dcc.Tab(label='Hotel Guests analysis', value='OPT2',
                                                   style={'font-size': '20px', 
                                                          'backgroundColor':'#01386a',
                                                          'color':'snow',
                                                          'font-family':'Tahoma, sans-serif'})
                                                     
                                        ], style={'font-size': '20px', 
                                                  'backgroundColor':'#01386a',
                                                  'color':'snow',
                                                  'font-family':'Tahoma, sans-serif'},
                                            colors={"border": "snow",
                                                    "primary": "#a2cffe",
                                                    "background": "#01386a"}),
                                    ]),
                                    
                                   # Add next division 
                                   html.Div([
                                       # Create an division for adding dropdown helper text for choosing hotel type
                                        html.Div(
                                            [
                                            html.H2('Hotel type', style={'display':'inline', 'margin-right': '10em',
                                                                         'backgroundColor':'#01386a',
                                                                         'color':'snow',
                                                                         'font-family':'Tahoma, sans-serif'})
                                            ]
                                        ),
                                        dcc.Dropdown(id='input-hotel', 
                                                     # Update dropdown values using list comphrehension
                                                     options=[{'label': 'Resort Hotel', 'value': 'Resort Hotel'},
                                                             {'label': 'City Hotel', 'value': 'City Hotel'}],
                                                     placeholder="Select a Hotel type",
                                                     style={'width':'80%', 'padding':'3px', 'font-size': '20px', 
                                                            'text-align-last' : 'center',
                                                            'backgroundColor':'#01386a', 'color':'snow',
                                                            'font-family':'Tahoma, sans-serif'}
                                                     #multi=True
                                                    ),
                                            # Place them next to each other using the division style
                                            ], style={'display': 'flex','backgroundColor':'#01386a',
                                                      'color':'snow',
                                                      'font-family':'Tahoma, sans-serif'}),  
                                          ]),
                                
                                # Add Computed graphs
                                # Added an empty division and provided an id that will be updated
                                # during callback
                                html.Div([ ], id='plot1'),
    
                                html.Div([
                                        html.Div([ ], id='plot2'),
                                        html.Div([ ], id='plot3')
                                ], style={'display': 'flex','margin-left': 50, 'margin-right':50}),
                                
                                # Add a division with two empty divisions inside
                                html.Div([
                                        html.Div([ ], id='plot4', style = {'float': 'left'}),
                                        html.Div([ ], id='plot5', style = {'float': 'right'})
                                ], style={'display': 'flex','margin-left': 50, 'margin-right':50}),
                               
                                ])


# Callback function definition
@app.callback( [Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children'),
                Output(component_id='plot3', component_property='children'),
                Output(component_id='plot4', component_property='children'),
                Output(component_id='plot5', component_property='children')],
               [Input(component_id='input-type', component_property='value'),
                Input(component_id='input-hotel', component_property='value')],
               # Holding output state till user enters all the form information.
               # In this case, it will be chart type
               [State("plot1", 'children'), State("plot2", "children"),
                State("plot3", "children"), State("plot4", "children"),
                State("plot5", "children")
               ])

# Add computation to callback function and return graph
def get_graph(chart, hotel_type, children1, children2, children3, children4, children5): # 
    # Select data
    df = df_hotel[df_hotel['hotel']==hotel_type]
       
    if chart == 'OPT1': # Hotel Bookings analysis

        # Compute required information for creating graph from the data
        df_hotel_nc_mean_price_ord, df_monthly_bookings_ord, df_stays, df_market, df_canc_res = compute_data_choice_1(df)

        # Lineplot of avergae monthly room price per hotel type
        line_price = px.line(df_hotel_nc_mean_price_ord,
                             x='Month',
                             y='Monthly Price',
                             title= f"Monthly mean room-price in {hotel_type}")
        line_price.update_layout({'plot_bgcolor': '#01386a',
                                  'paper_bgcolor': '#01386a'},
                                 font_color="snow",
                                 title_font_size = 23,
                                 xaxis=dict(showgrid=False),
                                 yaxis=dict(showgrid=False))
        line_price.update_traces(line_color='#a2cffe')
              
        # Lineplot Nr of bookings per month per hotel type
        line_booking = px.line(df_monthly_bookings_ord,
                            x='Month',
                            y='Nr of Bookings',
                            title= f"Monthly bookings in {hotel_type}")
        line_booking.update_layout({'plot_bgcolor': '#01386a',
                                    'paper_bgcolor': '#01386a'},
                                    font_color="snow",
                                    title_font_size = 23,
                                    xaxis=dict(showgrid=False),
                                    yaxis=dict(showgrid=False))
        line_booking.update_traces(line_color='#a2cffe')
        
        # Barplot Nr of bookings per nr of nights of stay per hotel type
        bar_stays = px.bar(df_stays,
                           x = 'Total nights',
                           y = 'Nr of stays',
                           text = 'Nr of stays',
                           barmode = 'group',
                           height = 400,
                           title = f"Bookings per nights of stay in {hotel_type}")
        bar_stays.update_layout({'plot_bgcolor': '#01386a',
                                  'paper_bgcolor': '#01386a'},
                                  font_color="snow",
                                  title_font_size = 23,
                                  xaxis=dict(showgrid=False),
                                  yaxis=dict(showgrid=False))
        bar_stays.update_traces(marker_color='#a2cffe')
        
        # Pie chart nr of bookings per market segment ['Market segment', 'Nr of bookings']
        pie_market = px.pie(df_market,
                            values = 'Nr of bookings',
                            names = 'Market segment',
                            title = f'Bookings per market segment in {hotel_type}')
        pie_market.update_layout({'plot_bgcolor': '#01386a',
                                  'paper_bgcolor': '#01386a'},
                                  font_color="snow",
                                  title_font_size = 23)
        
        # Barplot nr of cancellations / reservations per hotel type
        bar_canc_res = px.bar(df_canc_res,
                              x='Reservation Cancellation',
                              y='Count',
                              barmode='group',
                              height=400,
                              title=f'Cancellations (1) and reservations (0) in {hotel_type}')
        bar_canc_res.update_layout({'plot_bgcolor': '#01386a',
                                    'paper_bgcolor': '#01386a'},
                                    font_color="snow",
                                    title_font_size = 23,
                                    xaxis=dict(showgrid=False),
                                    yaxis=dict(showgrid=False))
        bar_canc_res.update_traces(marker_color='#a2cffe')


        # Return dcc.Graph component to the empty division
        return [dcc.Graph(figure = line_price), 
                dcc.Graph(figure = line_booking),
                dcc.Graph(figure = bar_stays),
                dcc.Graph(figure = pie_market),
                dcc.Graph(figure = bar_canc_res)
               ]
    
    elif chart == 'OPT2': 
        # HOTEL GUESTS ANALYSIS
        df_guests_month, df_cancel_req, df_room_req, df_meal_room, df_map = compute_data_choice_2(df)
        
        # Lineplot nr of guests per month per hotel type
        line_guests_month = px.line(df_guests_month,
                                    x='Month',
                                    y= 'Total guests',
                                    title=f'Monthly guests in {hotel_type}')
        line_guests_month.update_layout({'plot_bgcolor': '#01386a',
                                        'paper_bgcolor': '#01386a'},
                                         font_color="snow",
                                         title_font_size = 23,
                                         xaxis=dict(showgrid=False),
                                         yaxis=dict(showgrid=False))
        line_guests_month.update_traces(line_color='#a2cffe')
                                
        # Barplot nr of bookings by nr of special requests per cancelled/not cancelled
        bar_cancel_req = px.bar(df_cancel_req,
                                x = 'Special requests',
                                y = 'Nr of bookings',
                                barmode='group',
                                color = 'Cancelled (1)/Not cancelled (0)',
                                color_discrete_map={ # replaces default color mapping by value
                                "0": "#3c73a8", "1": "#a2cffe"
                                },
                                height = 400,
                                title = f"Special requests per cancelled (1)/not cancelled (0) in {hotel_type}")
        bar_cancel_req.update_layout({'plot_bgcolor': '#01386a',
                                      'paper_bgcolor': '#01386a'},
                                      font_color="snow",
                                      title_font_size = 23,
                                      xaxis=dict(showgrid=False),
                                      yaxis=dict(showgrid=False))
        
        # Barplot nr of bookings by nr of special requests per room type
        bar_room_req = px.bar(df_room_req,
                              x = 'Special requests',
                              y = 'Nr of bookings',
                              color = 'Room type',
                              height = 400,
                              title = f"Special requests per room type in {hotel_type}")
        bar_room_req.update_layout({'plot_bgcolor': '#01386a',
                                    'paper_bgcolor': '#01386a'},
                                    font_color="snow",
                                    title_font_size = 23,
                                    xaxis=dict(showgrid=False),
                                    yaxis=dict(showgrid=False))
        
        # Barplot preferred meals type per room type per hotel type
        bar_meal_room = px.bar(df_meal_room,
                               x = 'Meal',
                               y = 'Nr of preferences',
                               color = 'Room type',
                               height = 400,
                               title = f'Preferred meal type per room type in {hotel_type}')
        bar_meal_room.update_layout({'plot_bgcolor': '#01386a',
                                     'paper_bgcolor': '#01386a'},
                                     font_color="snow",
                                     title_font_size = 23,
                                     xaxis=dict(showgrid=False),
                                     yaxis=dict(showgrid=False))
        
        # Origin countries  of bookings
        map_origin = px.choropleth(df_map,
                                   locations = df_map['Country'],
                                   color = df_map['Guests'],
                                   hover_name = df_map['Country'],
                                   title = f"Origin countries of hotel guests in {hotel_type}")
        map_origin.update_layout({'plot_bgcolor': '#01386a',
                                  'paper_bgcolor': '#01386a'},
                                  font_color="snow",
                                  title_font_size = 23,
                                  xaxis=dict(showgrid=False),
                                  yaxis=dict(showgrid=False))
        
        return[dcc.Graph(figure = line_guests_month), 
               dcc.Graph(figure = bar_cancel_req), 
               dcc.Graph(figure = bar_room_req), 
               dcc.Graph(figure = bar_meal_room), 
               dcc.Graph(figure = map_origin)]


# Run the app
if __name__ == '__main__':
    app.run_server() #mode='inline'