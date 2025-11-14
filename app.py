from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Convert existing names to lowercase for consistency
            data['competitors'] = [{'name': c['name'].lower()} for c in data['competitors']]
            data['judges'] = [{'name': j['name'].lower(), 'room': j['room']} for j in data['judges']]
            # Initialize rounds if not present
            if 'rounds' not in data:
                data['rounds'] = []
            # Migrate 'assignments' to 'schematics' for backward compatibility
            for round_data in data['rounds']:
                if 'assignments' in round_data and 'schematics' not in round_data:
                    round_data['schematics'] = round_data.pop('assignments')
            return data
    return {'competitors': [], 'judges': [], 'rounds': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def dashboard():
    data = load_data()
    return render_template('dashboard.html', rounds=data['rounds'])

@app.route('/create_round')
def create_round():
    data = load_data()
    return render_template('round_setup.html', competitors=data['competitors'], judges=data['judges'], enumerate=enumerate)

@app.route('/add_competitor', methods=['POST'])
def add_competitor():
    name = request.form.get('name')
    if not name.strip():
        flash("Competitor name cannot be empty.")
        return redirect(url_for('create_round'))
    data = load_data()
    if any(c['name'] == name.lower() for c in data['competitors']):
        flash(f"Competitor {name.title()} already exists.")
        return redirect(url_for('create_round'))
    data['competitors'].append({'name': name.lower()})
    save_data(data)
    flash(f"Added competitor: {name.title()}")
    return redirect(url_for('create_round'))

@app.route('/add_judge', methods=['POST'])
def add_judge():
    name = request.form.get('name')
    room = request.form.get('room')
    if not name.strip():
        flash("Judge name cannot be empty.")
        return redirect(url_for('create_round'))
    if not room.strip():
        flash("Room cannot be empty.")
        return redirect(url_for('create_round'))
    data = load_data()
    if any(j['name'] == name.lower() for j in data['judges']):
        flash(f"Judge {name.title()} already exists.")
        return redirect(url_for('create_round'))
    data['judges'].append({'name': name.lower(), 'room': room})
    save_data(data)
    flash(f"Added judge: {name.title()} in room {room}")
    return redirect(url_for('create_round'))

@app.route('/delete_competitor/<name>')
def delete_competitor(name):
    data = load_data()
    data['competitors'] = [c for c in data['competitors'] if c['name'] != name.lower()]
    save_data(data)
    flash(f"Deleted competitor: {name.title()}")
    return redirect(url_for('create_round'))

@app.route('/delete_judge/<name>')
def delete_judge(name):
    data = load_data()
    data['judges'] = [j for j in data['judges'] if j['name'] != name.lower()]
    save_data(data)
    flash(f"Deleted judge: {name.title()}")
    return redirect(url_for('create_round'))

@app.route('/start_competition', methods=['POST'])
def start_competition():
    data = load_data()
    if not data['competitors'] or not data['judges']:
        flash("Need at least one competitor and one judge.")
        return redirect(url_for('create_round'))

    # Get selected competitors
    selected_comp_indices = request.form.getlist('competitors')
    if not selected_comp_indices:
        flash("No competitors selected.")
        return redirect(url_for('create_round'))
    selected_comps = [data['competitors'][int(i)] for i in selected_comp_indices if 0 <= int(i) < len(data['competitors'])]

    # Get selected judges
    selected_judge_indices = request.form.getlist('judges')
    if not selected_judge_indices:
        flash("No judges selected.")
        return redirect(url_for('create_round'))
    selected_judges = [data['judges'][int(i)] for i in selected_judge_indices if 0 <= int(i) < len(data['judges'])]

    # Assign randomly: 3-7 comps per judge
    assignments = {j['name']: [] for j in selected_judges}
    comp_list = selected_comps.copy()
    random.shuffle(comp_list)
    judge_names = list(assignments.keys())
    for comp in comp_list:
        # Find judge with least assignments, preferring 3-7
        available_judges = [j for j in judge_names if len(assignments[j]) < 7]
        if not available_judges:
            break
        judge = min(available_judges, key=lambda j: len(assignments[j]))
        assignments[judge].append(comp['name'])

    # Prepare assignments for display
    assignment_list = []
    for judge, comps in assignments.items():
        room = next(j['room'] for j in selected_judges if j['name'] == judge)
        assignment_list.append({
            'judge': judge.title(),
            'room': room,
            'competitors': [comp.title() for comp in comps]
        })

    # Save the round
    from datetime import datetime
    round_id = len(data['rounds']) + 1
    round_name = f"Round {round_id}"
    new_round = {
        'id': round_id,
        'name': round_name,
        'date': datetime.now().isoformat(),
        'schematics': assignment_list
    }
    data['rounds'].append(new_round)
    save_data(data)

    return render_template('assignments.html', assignments=assignment_list)

@app.route('/view_round/<int:round_id>')
def view_round(round_id):
    data = load_data()
    round_data = next((r for r in data['rounds'] if r['id'] == round_id), None)
    if not round_data:
        flash("Round not found.")
        return redirect(url_for('dashboard'))
    return render_template('assignments.html', assignments=round_data['schematics'])

@app.route('/clear_rounds')
def clear_rounds():
    data = load_data()
    data['rounds'] = []
    save_data(data)
    flash("All rounds have been cleared.")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
