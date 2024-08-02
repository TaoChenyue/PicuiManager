def confirm(message: str):
    """Confirm the user's choice."""

    while True:
        confirm = input(f"{message} (y/n): ").lower()
        if confirm == "y":
            return True
        elif confirm == "n":
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def confirm_choice(message: str, choices):
    """Confirm the user's choice from a list of choices."""

    while True:
        choice = input(message)
        if choice in choices:
            return choice
        else:
            print(f"Invalid choice. Please choose from the following: {', '.join(choices)}")