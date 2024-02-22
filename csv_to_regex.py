import re
import pandas as pd
import os

def get_row_indices_from_input(user_input, max_rows):
    """
    Parse user input and return a list of row indices.
    Supports ranges like '1-5', individual numbers like '7', and '*' for all rows.
    """
    try:
        if user_input.strip() == '*':
            return list(range(max_rows))
        
        indices = set()
        for part in user_input.split(','):
            if '-' in part:
                start, end = part.split('-')
                start, end = int(start), int(end)
                if start <= 0 or end > max_rows:
                    raise ValueError(f"Range {start}-{end} is out of bounds. Please enter a valid range.")
                indices.update(range(start - 1, end))
            else:
                index = int(part) - 1
                if index < 0 or index >= max_rows:
                    raise ValueError(f"Index {index + 1} is out of bounds. Please enter a valid index.")
                indices.add(index)
        return sorted(indices)
    except ValueError as e:
        print(f"Error: {e}")
        return []

def select_and_display_columns(csv_filepath):
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_filepath)
    
    # Display available headers
    headers = df.columns.tolist()
    print("Available columns in the CSV file:")
    for idx, header in enumerate(headers, 1):
        print(f"{idx}. {header}")
    
    # User input for column selection
    selected_headers_input = input("Which columns do you want to use? (Enter as a comma-separated list): ")
    selected_headers = [header.strip() for header in selected_headers_input.split(',')]
    
    # Check if the selected headers exist in the dataframe
    selected_headers = [header for header in selected_headers if header in headers]
    if not selected_headers:
        print("None of the entered column headers were found. Please check for typos and try again.")
        return
    
    print(f"Selecting data from {', '.join(selected_headers)}")
    
    # Ask user if they want to strip trailing .0 from floats
    strip_trailing_zero = input("Do you want to strip trailing .0 from float values? (yes/no): ").lower().startswith('y')
    
    # Display the data for the selected columns and ask for rows to include
    unique_selected_data = {}
    for header in selected_headers:
        print(f"\nData for column '{header}':")
        for idx, value in enumerate(df[header], 1):
            if strip_trailing_zero and isinstance(value, float) and value.is_integer():
                value = int(value)  # Convert float to int if it's a whole number
            print(f"{idx}. {value}")

        row_selection = input(f"Which rows would you like to use from {header}? "
                              "Please enter like: 1-5,8-10,20 or * for all rows: ")
        selected_rows = get_row_indices_from_input(row_selection, len(df))
        # Use set to get unique values and then convert back to list to maintain DataFrame compatibility
        selected_data = df.iloc[selected_rows][header].dropna().tolist()
        if strip_trailing_zero:
            selected_data = [int(value) if isinstance(value, float) and value.is_integer() else value for value in selected_data]
        unique_selected_data[header] = list(set(selected_data))

    # Display the rows selected for each column
    print("\nHere are the rows selected for each column:")
    for header, data in unique_selected_data.items():
        print(f"{header}: {data}")
    make_unique_selected_data_to_regex(unique_selected_data)
    return unique_selected_data

def make_unique_selected_data_to_regex(unique_selected_data):
    # Ask the user if they want the regex to be case-insensitive
    case_insensitive = input("Would you like the regex to be case-insensitive? (yes/no): ").lower().startswith('y')
    
    # Open a file named 'regex.txt' in write mode
    with open('regex.txt', 'w') as file:
        # Write the beginning of the array declaration
        file.write("advanced_patterns = [\n")
        
        # Determine the regex flag based on user choice
        regex_flag = "re.IGNORECASE" if case_insensitive else ""
        
        # Create a regex pattern for each column and write them in re.compile format
        for header, data in unique_selected_data.items():
            # Escape special characters, add word boundaries, and join the data with '|'
            escaped_data = [r"\b" + re.escape(str(value)) + r"\b" for value in data]
            regex_pattern = '|'.join(escaped_data)
            # Write the pattern to the file, wrapping it in a call to re.compile() with the chosen flag
            if regex_flag:
                file.write(f"    re.compile(r\"{regex_pattern}\", {regex_flag}),\n")
            else:
                file.write(f"    re.compile(r\"{regex_pattern}\"),\n")
        
        # Write the closing bracket for the array
        file.write("]\n")
    print("Regex patterns written to regex.txt based on your case sensitivity preference.")
    print("Here are the regex patterns: ")
    with open('regex.txt', 'r') as file:
        print(file.read())



# Helper function to verify file existence
def verify_file_exists(filepath):
    if os.path.exists(filepath):
        print(f"File found: {filepath}")
        return True
    else:
        print(f"File not found: {filepath}")
        print("Please enter the correct file path.")
        return False

# Main part of the script
if __name__ == "__main__":
    file_exists = False
    while not file_exists:
        csv_file_path = input("Enter the path to your CSV file: ")
        file_exists = verify_file_exists(csv_file_path)
        if file_exists:
            select_and_display_columns(csv_file_path)
