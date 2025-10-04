# BMI = Weight / Height^2    kg and m

def convert_to_m(height_cm: float) -> float:
    return height_cm / 100.0

def calculate_bmi(height_m: float, weight_kg: float) -> float:
    if height_m <= 0:
        raise ValueError("Height must be greater than 0.")
    return weight_kg / (height_m ** 2)

def classify_bmi(bmi: float) -> tuple[str, str]:
    if bmi < 18.5:
        return "Underweight", "You'd better eat more!"
    elif bmi < 25:
        return "Normal", "Good job!"
    elif bmi < 30:
        return "Overweight", "You'd better do some exercises"
    else:
        return "Obesity", "You'd better consult doctor"

def prompt_number(prompt: str, cast, min_v=None, max_v=None):
    while True:
        s = input(prompt).strip()
        if s.lower() in {"q", "quit", "exit"}:
            raise SystemExit
        try:
            val = cast(s)
        except ValueError:
            print("Please enter a number.")
            continue
        if min_v is not None and val < min_v:
            print(f"Value must be ≥ {min_v}.")
            continue
        if max_v is not None and val > max_v:
            print(f"Value must be ≤ {max_v}.")
            continue
        return val

def bmi_app():
    print("BMI Calculator (type 'q' to quit)")
    while True:
        try:
            age = prompt_number("What's your age? ", int, 0, 120)
            if age < 18:
                print("Sorry, I can't help you.")
                print("-" * 43)
                continue

            height_cm = prompt_number("What's your height (in cm)? ", float, 50, 300)
            weight_kg = prompt_number("What's your weight (in kg)? ", float, 10, 500)

            height_m = convert_to_m(height_cm)
            bmi = calculate_bmi(height_m, weight_kg)
            label, msg = classify_bmi(bmi)

            print(f"Your BMI is {bmi:.2f} — {label}. {msg}")
            print("-" * 43)
        except SystemExit:
            print("Bye.")
            break
        except KeyboardInterrupt:
            print("\nBye.")
            break

if __name__ == "__main__":
    bmi_app()
