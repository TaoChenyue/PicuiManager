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
