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
    'Lessons Learned': '#ff6666',
    'Success Stories': '#fff166',
    'Strategy' : '#da66ff'
}

FONT_FAMILY = 'Segoe UI, sans-serif'
FONT_COLOR = 'Black'


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

def delete_entry_from_file(entry_id):
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

def safe_str(val):
    return str(val) if isinstance(val, (int, float, str)) and val is not None else ""

def create_card(entry):
    title = f"{entry.get('type')} - {entry.get('title', '')}"
    
    price = entry.get('price', None)       
    amount = entry.get('amount', None)
    costs = price * amount if price is not None and amount is not None else None
    
    sub_title = f"{safe_str(costs)}€ ({safe_str(amount)} x {safe_str(price)}€)" if costs else "-"
    
    date = entry.get('date')
    body = entry.get('note', '')
    tags = ', '.join(entry.get('tags', []))
    card_color = COLORS.get(entry.get('type'), '#e9ecef')

    return html.Div([
        # Header-Zeile mit Titel und Button nebeneinander
        html.Div([
            html.H3(f"{title}", style={'margin': '0'}),
            html.Div([
                html.Button("✏️", id={'type': 'edit-button', 'index': entry['id']}, style={
                'backgroundColor': 'transparent',
                'border': 'none',
                'padding': '4px 10px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'fontSize': '1em'
                }),
                html.Button("❌", id={'type': 'delete-button', 'index': entry['id']}, style={
                'backgroundColor': 'transparent',
                'border': 'none',
                'padding': '4px 10px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'fontSize': '1em'
                }),
            ], style={'display': 'flex', 'gap': '5px'})
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'marginBottom': '6px'
        }),
        html.Div(f"📆: {date}", style={'fontSize': '0.85em'}),
        html.Div(f"💵: {sub_title}", style={'fontSize': '0.85em'}),
        dcc.Markdown(body, style={'marginBottom': '10px'}),
        html.Div(f"Tags: {tags}", style={'fontSize': '0.85em'}),
        
    ], style={
        'backgroundColor': card_color,
        'padding': '20px',
        'borderRadius': '12px',
        'marginBottom': '20px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.05)',
        'fontFamily': FONT_FAMILY
    })


entry_types = ['Buy', 'Sell', 'Market Stories', 'Lessons Learned', 'Success Stories', 'Strategy']

app.layout = html.Div(style={
    'fontFamily': 'Segoe UI, sans-serif',
    'backgroundImage': 'url("https://www.transparenttextures.com/patterns/paper-fibers.png")',
    'backgroundRepeat': 'repeat',
    'minHeight': '100vh',
    'maxWidth': '65%',
    'margin': '0 auto',
    'padding': '30px',
    'backgroundColor': '#fdfcf5',
    'color': FONT_COLOR,
}, children=[
    html.H1("📝 Investment-Journal 📈", style={
        'textAlign': 'center',
        'marginBottom': '30px',
        'fontSize': '2.5em',
    }),

    dcc.Store(id='edit-entry-store'),

    html.Div([
        dcc.Dropdown(
            id='filter-type',
            options=[{'label': 'All', 'value': 'ALL'}] + [{'label': t, 'value': t} for t in entry_types],
            value='ALL',
            style={'minWidth': '180px', 'fontSize': '0.90em'}
        ),
        dcc.Input(id='filter-date', type='text', placeholder='Filter by year e.g. 2024', style={'border': '1px solid #ced4da'}), 
        dcc.Input(id='filter-tags', type='text', placeholder='Tags (comma-separated)', style={'border': '1px solid #ced4da'}),
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'marginBottom': '15px'}), 

    html.Div(id='entries-container'),

    html.H2("➕ Add New Entry", style={
        'textAlign': 'center',
        'marginTop': '40px',
        'marginBottom': '20px',
    }),

    html.Div([
        dcc.Dropdown(id='input-type', options=[{'label': t, 'value': t} for t in entry_types], value='Buy', style={'flex': '1', 'fontSize': '0.90em'}),
        dcc.Input(id='input-title', type='text', placeholder='Asset or Title', style={'flex': '2', 'border': '1px solid #ced4da'}),
        dcc.Input(id='input-price', type='number', placeholder='Price (EUR.CENT)', style={'flex': '1', 'border': '1px solid #ced4da',}),
        dcc.Input(id='input-amount', type='number', placeholder='Amount', style={'flex': '1', 'border': '1px solid #ced4da',}),
        dcc.Input(id='input-tags', type='text', placeholder='Tags (comma-separated)', style={'flex': '2', 'border': '1px solid #ced4da',}),
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px', 'marginBottom': '15px'}), 

    html.Div([
        dcc.Textarea(id='input-note', placeholder='My thoughts or analysis... (Markdown supported)', style={
            'padding': '20px',
            'width': '100%',
            'height': '200px',
            'boxSizing': 'border-box',
            'borderRadius': '12px',
            'marginBottom': '20px',
            'border': '1px solid #ced4da',
            'resize': 'none'
        }),
    ], style={'maxWidth': '100%', 'margin': '0 auto'}),

    html.Div([
        html.Button('Save Note', id='save-button', n_clicks=0, style={
            'backgroundColor': '#007bff',
            'color': 'white',
            'padding': '10px 20px',
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer',
            'fontSize': '16px',
            'marginTop': '10px'
        }),
    ], style={'textAlign': 'right'})
])


@app.callback(
    Output('edit-entry-store', 'data'),
    Input({'type': 'edit-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'edit-button', 'index': ALL}, 'id')
)
def load_entry_for_edit(n_clicks_list, ids):
    triggered = dash.ctx.triggered_id
    if triggered and isinstance(triggered, dict) and triggered['type'] == 'edit-button':
        for idx, item in enumerate(ids): 
            if item['index'] == triggered['index']: 
                if n_clicks_list[idx] != None: 
                    entry_id = triggered['index']
                    entries = load_entries()
                    for entry in entries:
                        if entry['id'] == entry_id:
                            return entry
    return dash.no_update

@app.callback(
    Output('input-type', 'value'),
    Output('input-title', 'value'),
    Output('input-price', 'value'),
    Output('input-amount', 'value'),
    Output('input-note', 'value'),
    Output('input-tags', 'value'),
    Input('edit-entry-store', 'data'),
    prevent_initial_call=True
)
def populate_form(entry):
    if not entry:
        raise dash.exceptions.PreventUpdate

    return (
        entry.get('type'),
        entry.get('title'),
        entry.get('price'),
        entry.get('amount'),
        entry.get('note'),
        ', '.join(entry.get('tags', []))
    )

@app.callback(
    Output('entries-container', 'children'),
    Input('filter-type', 'value'),
    Input('filter-date', 'value'),
    Input('filter-tags', 'value'),
    Input('save-button', 'n_clicks'),
    State('save-button', 'id'),
    State('input-type', 'value'),
    State('input-title', 'value'),
    State('input-price', 'value'),
    State('input-amount', 'value'),
    State('input-note', 'value'),
    State('input-tags', 'value'), 
    Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'delete-button', 'index': ALL}, 'id'),
    State('edit-entry-store', 'data')
)
def show_entries(filter_type, filter_date, filter_tags, # filter menu
                 n_clicks, save_button_id, typ, title, price, amount, note, tags, # new element
                 n_clicks_list, ids, edit_entry): # delete

    triggered = dash.ctx.triggered_id

    if triggered == 'save-button': # save button pressed
        # # save new notes
        save_new_entry(n_clicks, typ, title, price, amount, note, tags, edit_entry)

    else: # check for delete button
        try: 
            if triggered['type'] == 'delete-button':
                delete_entry(triggered, n_clicks_list, ids)
        except (ValueError, TypeError):
                    pass  # Skip entries with invalid or missing date

    entries = load_entries()

    # filter entries
    entries = update_entries(entries, filter_type, filter_date, filter_tags)
    
    entries.sort(key=lambda e: e.get('date', ''), reverse=True)
    return [create_card(e) for e in entries]


def update_entries(entries, filter_type, filter_date, filter_tags):
    # filter by entry type
    if filter_type != 'ALL':
        entries = [e for e in entries if e.get('type') == filter_type]
    # filter by year
    if filter_date:
        try:
            f_dt = datetime.strptime(filter_date, "%Y").year
            filtered_entries = []
            for e in entries:
                try:
                    e_dt = datetime.strptime(e.get('date'), "%Y-%m-%d").year
                    if e_dt == f_dt:
                        filtered_entries.append(e)
                except (ValueError, TypeError):
                    pass  # Skip entries with invalid or missing date
            entries = filtered_entries
        except ValueError:
            pass  # Skip filtering if filter_date is not in 'YYYY' format 
    # filter by specified tags
    if filter_tags:
        tag_list = [t.strip().lower() for t in filter_tags.split(',')]
        entries = [e for e in entries if any(t in [x.lower() for x in e.get('tags', [])] for t in tag_list)]
    
    return entries #[create_card(e) for e in entries]


def save_new_entry(n_clicks, typ, title, price, amount, note, tags, edit_entry):
    if n_clicks < 1:
        return
    new_entry = {
        'type': typ,
        'note': note,
        'tags': [t.strip() for t in tags.split(',')] if tags else [],
        'date': datetime.today().strftime('%Y-%m-%d')
    }

    new_entry['price'] = price
    new_entry['amount'] = amount
    new_entry['title'] = title

    if edit_entry and edit_entry.get('id'):
        new_entry['id'] = edit_entry['id']
        update_entry_in_file(new_entry)
    else:
        new_entry['id'] = str(uuid.uuid4())
        save_entry(new_entry)

def update_entry_in_file(updated_entry):
    if FILE == DUMMY_FILE:
        print("⚠️ Dummy mode: update not performed.")
        return
    with open(FILE, 'r') as f:
        data = yaml.safe_load(f) or {}
        entries = data.get('entries', [])
        for i, e in enumerate(entries):
            if e.get('id') == updated_entry['id']:
                entries[i] = updated_entry
                break
    data['entries'] = entries
    with open(FILE, 'w') as f:
        yaml.safe_dump(data, f, allow_unicode=True)

def delete_entry(triggered, n_clicks_list, ids):
    # delete from file and from entries
    for idx, item in enumerate(ids): 
        if item['index'] == triggered['index']: 
            if n_clicks_list[idx] != None: 
                delete_entry_from_file(triggered['index'])

if __name__ == '__main__':
    app.run(debug=True)
