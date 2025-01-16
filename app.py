import pyttsx3
import speech_recognition as sr
from datetime import datetime
import json

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize an empty list to store orders
orders = []
user_preferences = {"diet": None}  # Default to None for explicit user selection

# Load menu from a configuration file
with open("menu_config.json", "r") as menu_file:
    menu = json.load(menu_file)

def speak_text(text):
    """Speak the provided text."""
    engine.say(text)
    engine.runAndWait()

def get_greeting():
    """Return a greeting based on the current time."""
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

def filter_menu(menu):
    """Filter menu based on user preferences."""
    filtered_menu = {}
    for dish, details in menu.items():
        # Include only items that match the preference or are available for all diets
        if user_preferences["diet"] is None or details["type"] == user_preferences["diet"] or details["type"] == "all":
            filtered_menu[dish] = details
    return filtered_menu

def process_command(command):
    """Process the user's voice command and return a response."""
    global orders, user_preferences
    command = command.lower()

    # Handle preferences
    if "veg" in command or "vegetarian" in command:
        user_preferences["diet"] = "veg"
        return "Vegetarian preference set."
    elif "non-veg" in command or "non-vegetarian" in command:
        user_preferences["diet"] = "non-veg"
        return "Non-vegetarian preference set."
    elif "mix" in command:
        user_preferences["diet"] = "all"
        return "Mixed preference set."

    # Ensure user preference is set
    if user_preferences["diet"] is None:
        return "Please set your dietary preference (vegetarian, non-vegetarian, or mix) before proceeding."

    # Filtered menu based on preferences
    filtered_menu = filter_menu(menu)

    # Show menu
    if "menu" in command:
        if filtered_menu:
            return "Our menu includes: " + ", ".join(filtered_menu.keys())
        else:
            return "No items match your preferences."

    # Add to order
    elif "order" in command or "add" in command:
        for item in filtered_menu:
            if item in command:
                orders.append(item)
                return f"{item} has been added to your order. Anything else you'd like to add?"
        return "I'm sorry, I couldn't recognize the dish. Please try again."

    # Remove from order
    elif "remove" in command:
        for item in orders:
            if item in command:
                orders.remove(item)
                return f"{item} has been removed from your order. Anything else you'd like to modify?"
        return "I'm sorry, I couldn't recognize the dish to remove. Please try again."

    # Show order
    elif "show order" in command or "what's my order" in command:
        if orders:
            return f"Your current order includes: {', '.join(orders)}."
        else:
            return "You haven't ordered anything yet."

    # Thank you and exit
    elif "thank you" in command or "bye" in command:
        if orders:
            return f"Thank you for your order! You have ordered: {', '.join(orders)}. Your food will arrive shortly. Have a great day!"
        else:
            return "Thank you! Your food will arrive shortly. Have a great day!"

    else:
        return "I'm sorry, I don't understand. Could you please repeat?"

if __name__ == "__main__":
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    greeting = get_greeting()
    print(f"{greeting} Welcome to our restaurant. Speak now! (Press Ctrl+C to stop)")
    speak_text(f"{greeting} Welcome to our restaurant. Do you prefer vegetarian, non-vegetarian, or a mix of both?")

    while True:
        try:
            # Listen to the user's command
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = recognizer.listen(source)

            # Convert audio to text
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")

            # Process the command
            response = process_command(command)
            print(f"Response: {response}")

            # Speak the response
            speak_text(response)

            # Exit if the conversation ends
            if "thank you" in command or "bye" in command:
                break

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Please repeat.")
            speak_text("Sorry, I didn't catch that. Please repeat.")
        except KeyboardInterrupt:
            print("\nExiting... Goodbye!")
            speak_text("Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            speak_text("An error occurred. Please try again.")
