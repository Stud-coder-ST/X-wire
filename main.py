import json
import os
import random

DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # Convert existing names to lowercase for consistency
            data['competitors'] = [{'name': c['name'].lower()} for c in data['competitors']]
            data['judges'] = [{'name': j['name'].lower(), 'room': j['room']} for j in data['judges']]
            return data
    return {'competitors': [], 'judges': []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_competitor(name):
    if not name.strip():
        print("Competitor name cannot be empty.")
        return
    data = load_data()
    if any(c['name'] == name.lower() for c in data['competitors']):
        print(f"Competitor {name.title()} already exists.")
        return
    data['competitors'].append({'name': name.lower()})
    save_data(data)
    print(f"Added competitor: {name.title()}")

def add_judge(name, room):
    if not name.strip():
        print("Judge name cannot be empty.")
        return
    if not room.strip():
        print("Room cannot be empty.")
        return
    data = load_data()
    if any(j['name'] == name.lower() for j in data['judges']):
        print(f"Judge {name.title()} already exists.")
        return
    data['judges'].append({'name': name.lower(), 'room': room})
    save_data(data)
    print(f"Added judge: {name.title()} in room {room}")

def delete_competitor(name):
    data = load_data()
    data['competitors'] = [c for c in data['competitors'] if c['name'] != name.lower()]
    save_data(data)
    print(f"Deleted competitor: {name.title()}")

def delete_judge(name):
    data = load_data()
    data['judges'] = [j for j in data['judges'] if j['name'] != name.lower()]
    save_data(data)
    print(f"Deleted judge: {name.title()}")

def start_competition():
    data = load_data()
    if not data['competitors'] or not data['judges']:
        print("Need at least one competitor and one judge.")
        return
    print("Available competitors:")
    for i, c in enumerate(data['competitors']):
        print(f"{i+1}. {c['name'].title()}")
    comp_input = input("Enter competitor numbers to select (comma-separated, or 'all'). Note: Enter numbers only: ")
    if comp_input.lower() == 'all':
        selected_comps = data['competitors']
    else:
        try:
            indices = [int(x.strip())-1 for x in comp_input.split(',')]
            selected_comps = [data['competitors'][i] for i in indices if 0 <= i < len(data['competitors'])]
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas or 'all'.")
            return

    print("Available judges:")
    for i, j in enumerate(data['judges']):
        print(f"{i+1}. {j['name'].title()} (Room: {j['room']})")
    judge_input = input("Enter judge numbers to select (comma-separated, or 'all'). Note: Enter numbers only: ")
    if judge_input.lower() == 'all':
        selected_judges = data['judges']
    else:
        try:
            indices = [int(x.strip())-1 for x in judge_input.split(',')]
            selected_judges = [data['judges'][i] for i in indices if 0 <= i < len(data['judges'])]
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas or 'all'.")
            return

    if not selected_comps or not selected_judges:
        print("No selection made.")
        return

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

    print("Assignments:")
    for judge, comps in assignments.items():
        room = next(j['room'] for j in selected_judges if j['name'] == judge)
        print(f"Judge {judge.title()} (Room {room}): {', '.join(comp.title() for comp in comps)}")

def main():
    while True:
        print("\nMenu:")
        print("1. Add Competitor")
        print("2. Add Judge")
        print("3. Delete Competitor")
        print("4. Delete Judge")
        print("5. Start Competition")
        print("6. Exit")
        choice = input("Choose: ")
        if choice == '1':
            name = input("Competitor name: ")
            add_competitor(name)
        elif choice == '2':
            name = input("Judge name: ")
            room = input("Room: ")
            add_judge(name, room)
        elif choice == '3':
            name = input("Competitor name to delete: ")
            delete_competitor(name)
        elif choice == '4':
            name = input("Judge name to delete: ")
            delete_judge(name)
        elif choice == '5':
            start_competition()
        elif choice == '6':
            break
        else:
            print("Invalid choice.")

if __name__ == '__main__':
    main()
