def log_message(message):
    print(f"[LOG] {message}")

def handle_error(error):
    log_message(f"[ERROR] {error}")

def format_date(date):
    return date.strftime("%Y-%m-%d")

def calculate_percentage_change(old_value, new_value):
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def save_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(data)