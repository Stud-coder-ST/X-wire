# TODO List for Implementing Multiple Rounds Dashboard

- [x] Update data.json structure to include 'rounds' list (each round: ID, name, date, assignments)
- [x] Update load_data and save_data in app.py to handle rounds
- [x] Create new dashboard route (/) rendering dashboard.html
- [x] Rename templates/index.html to templates/round_setup.html
- [x] Update the index route in app.py to create_round route
- [x] Modify start_competition in app.py to save the round and redirect to dashboard
- [x] Update templates/assignments.html to link back to dashboard
- [x] Create new templates/dashboard.html (list rounds, create round button)
- [x] Ensure round IDs are unique (incremental)
- [x] Test creating multiple rounds and navigation (app running on http://127.0.0.1:5000)
