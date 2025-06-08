import dash
from dash import html, dcc, Input, Output, State
from dash.dependencies import ALL
import yaml
import os
from datetime import datetime
import uuid


DUMMY_FILE = 'dummy_journal.yaml'
REAL_FILE = 'journal.yaml'

FILE = REAL_FILE if os.path.exists(REAL_FILE) else DUMMY_FILE

app = dash.Dash(__name__)
app.title = "📝 Investment Journal"

COLORS = {
    'Buy': 'lightgreen',
    'Sell': 'wheat',
    'Market Stories': 'skyblue',
    'Lessons Learned': 'chocolate',
    'Success Stories': 'gold'
}

FONT_FAMILY = 'sans-serif'


def load_entries():
    with open(FILE, 'r') as f:
        return yaml.safe_load(f).get('entries', [])

def save_entry(new_entry):
    if FILE == DUMMY_FILE:
        print("⚠️ Dummy file: New entries won't be saved.")
        return
    try:
        if not os.path.exists(FILE):
            data = {'entries': [new_entry]}
        else:
            with open(FILE, 'r') as f:
                data = yaml.safe_load(f) or {}
                data.setdefault('entries', []).append(new_entry)
        with open(FILE, 'w') as f:
            yaml.safe_dump(data, f, allow_unicode=True)
    except Exception as e:
        print(f"Error saving entry: {e}")

def delete_entry_by_id(entry_id):
    if FILE == DUMMY_FILE:
        print("⚠️ Dummy mode: deletion not performed.")
        return
    with open(FILE, 'r') as f:
        data = yaml.safe_load(f) or {}
        entries = data.get('entries', [])
        filtered = [e for e in entries if e.get('id') != entry_id]
        data['entries'] = filtered
    with open(FILE, 'w') as f:
        yaml.safe_dump(data, f, allow_unicode=True)

def create_card(entry):
    title = f"{entry.get('type')} - {entry.get('asset', entry.get('title', ''))}"
    date = entry.get('date')
    body = entry.get('note', '')
    tags = ', '.join(entry.get('tags', []))
    card_color = COLORS.get(entry.get('type'), 'silver')

    return html.Div([
        html.H4(f"{title}", style={"marginBottom": "5px"}),
        html.Div(f"📅 {date}", style={"fontSize": "0.9em", "color": "gray"}),
        dcc.Markdown(body, style={"marginTop": "10px"}),
        html.Div(f"🏷️ {tags}", style={"fontSize": "0.85em", "marginTop": "8px", "color": "#777"}),
        html.Button("🗑️ Delete", id={'type': 'delete-button', 'index': entry['id']}, style={
            'marginTop': '10px',
            'backgroundColor': '#ffdddd',
            'border': 'none',
            'padding': '6px 12px',
            'cursor': 'pointer'
        })
    ], style={
        'backgroundColor': card_color,
        'padding': '15px',
        'marginBottom': '15px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.05)',
        'fontFamily': FONT_FAMILY
    })

entry_types = ['Buy', 'Sell', 'Market Stories', 'Lessons Learned', 'Success Stories']

app.layout = html.Div(style={'fontFamily': FONT_FAMILY}, children=[
    html.H1("📝 Personal Investment Journal", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Filter by entry type:"),
        dcc.Dropdown(
            id='filter-type',
            options=[{'label': 'All', 'value': 'ALL'}] + [{'label': t, 'value': t} for t in entry_types],
            value='ALL',
            style={'width': '200px', 'marginRight': '20px'}
        ),
        html.Label("Date (YYYY-MM-DD):"),
        dcc.Input(id='filter-date', type='text', placeholder='e.g. 2024-06-01', style={'width': '180px', 'marginRight': '20px'}),
        html.Label("Tags:"),
        dcc.Input(id='filter-tags', type='text', placeholder='comma-separated', style={'width': '200px'})
    ], style={'padding': '20px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'}),

    html.Div(id='entries-container', style={'padding': '0px 20px'}),

    html.H2("➕ Add New Entry", style={'marginTop': '30px', 'textAlign': 'center'}),
    html.Div([
        dcc.Input(id='input-asset', type='text', placeholder='Asset or title', style={'width': '300px'}),
        dcc.Dropdown(id='input-type', options=[{'label': t, 'value': t} for t in entry_types], value='Buy', style={'width': '200px'}),
        dcc.Input(id='input-price', type='number', placeholder='Price', style={'width': '120px'}),
        dcc.Input(id='input-amount', type='number', placeholder='Amount', style={'width': '120px'}),
        dcc.Input(id='input-tags', type='text', placeholder='Tags (comma-separated)', style={'width': '300px'}),
    ], style={'margin': '10px 0', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'}),

    dcc.Textarea(id='input-note', placeholder='Your notes (Markdown supported)', style={'width': '100%', 'height': 120, 'marginBottom': '10px'}),
    html.Button('Save entry', id='save-button', n_clicks=0),
    html.Div(id='save-feedback', style={'marginTop': '10px'}),
])

@app.callback(
    Output('entries-container', 'children'),
    Input('filter-type', 'value'),
    Input('filter-date', 'value'),
    Input('filter-tags', 'value')
)
def update_entries(filter_type, filter_date, filter_tags):
    entries = load_entries()
    if filter_type != 'ALL':
        entries = [e for e in entries if e.get('type') == filter_type]
    if filter_date:
        entries = [e for e in entries if e.get('date') == filter_date]
    if filter_tags:
        tag_list = [t.strip().lower() for t in filter_tags.split(',')]
        entries = [e for e in entries if any(t in [x.lower() for x in e.get('tags', [])] for t in tag_list)]
    entries.sort(key=lambda e: e.get('date', ''), reverse=True)
    return [create_card(e) for e in entries]

@app.callback(
    Output('save-feedback', 'children'),
    Input('save-button', 'n_clicks'),
    State('input-type', 'value'),
    State('input-asset', 'value'),
    State('input-price', 'value'),
    State('input-amount', 'value'),
    State('input-note', 'value'),
    State('input-tags', 'value')
)
def save_new_entry(n_clicks, typ, asset, price, amount, note, tags):
    if n_clicks < 1:
        return ""
    new_entry = {
        'id': str(uuid.uuid4()),
        'date': datetime.today().strftime('%Y-%m-%d'),
        'type': typ,
        'note': note,
        'tags': [t.strip() for t in tags.split(',')] if tags else []
    }
    if typ in ['Buy', 'Sell']:
        new_entry['asset'] = asset
        new_entry['price'] = price
        new_entry['amount'] = amount
    else:
        new_entry['title'] = asset

    save_entry(new_entry)
    entries = load_entries()
    entries.sort(key=lambda e: e.get('date', ''), reverse=True)
    #return [create_card(e) for e in entries]
    return "✅ Entry saved! Please refresh to see it."

@app.callback(
    Output('entries-container', 'children', allow_duplicate=True),
    Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'delete-button', 'index': ALL}, 'id'),
    prevent_initial_call='initial_duplicate'
)
def handle_delete_entry(n_clicks_list, ids):
    triggered = dash.ctx.triggered_id

    if not triggered:
        return dash.no_update

    for idx, item in enumerate(ids): 
        if item['index'] == triggered['index']: 
            if n_clicks_list[idx] != None: 
                delete_entry_by_id(triggered['index'])
    
    entries = load_entries()
    entries.sort(key=lambda e: e.get('date', ''), reverse=True)
    return [create_card(e) for e in entries]

if __name__ == '__main__':
    app.run(debug=True)
