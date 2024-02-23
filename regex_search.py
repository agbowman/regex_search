import os
import re
import pandas as pd
import concurrent.futures


import tkinter as tk
from tkinter import filedialog

specific_dirs = [r"N:\cclprod"]
basic_patterns = []
advanced_patterns = []
custom_patterns = []
ignore_paths_keywords = []
exclude_dirs = []
file_extensions = []


def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Temporarily make the window stay on top
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(title="Select a CSV file", filetypes=[("CSV files", "*.csv")])
    
    # Set it back to not always on top after file dialog closes
    root.attributes('-topmost', False)
    
    return file_path
def select_text_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Temporarily make the window stay on top
    root.attributes('-topmost', True)

    file_path = filedialog.askopenfilename(title="Select a text file", filetypes=[("Text files", "*.txt")])

    # Set it back to not always on top after file dialog closes
    root.attributes('-topmost', False)

    return file_path

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
    
    # Create a mapping of lowercase column names to original column names
    original_headers = df.columns.tolist()
    lower_to_original = {header.lower(): header for header in original_headers}
    
    # Display available headers (in original case)
    print("Available columns in the CSV file:")
    for idx, header in enumerate(original_headers, 1):
        print(f"{idx}. {header}")
    
    # User input for column selection (converted to lower case for case-insensitive matching)
    selected_headers_input = input("Which columns do you want to use? (Enter as a comma-separated list): ").lower()
    selected_headers = [header.strip() for header in selected_headers_input.split(',')]
    
    # Map the lowercase user input back to the original case column names
    selected_headers = [lower_to_original[header] for header in selected_headers if header in lower_to_original]
    
    if not selected_headers:
        print("None of the entered column headers were found. Please check for typos and try again.")
        return {}
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
  
    if not unique_selected_data:  # Check if unique_selected_data is empty
        print("No rows selected for any column.")
        return {}  # Return an empty dictionary if no data was selected

    # Display the rows selected for each column
    print("\nHere are the unique rows selected for each column:")
    for header, data in unique_selected_data.items():
        print(f"{header}: {data}")

    # Return the collected data at the end
    return unique_selected_data


def make_unique_selected_data_to_regex(unique_selected_data):
    case_insensitive = input("Would you like the regex to be case-insensitive? (yes/no): ").lower().startswith('y')
    regex_flag = re.IGNORECASE if case_insensitive else 0

    compiled_patterns = []
    for header, data in unique_selected_data.items():
        # Include word boundaries (\b) in each pattern
        escaped_data = [r"\b" + re.escape(str(value)) + r"\b" for value in data]
        regex_pattern = '|'.join(escaped_data)
        compiled_pattern = re.compile(regex_pattern, regex_flag)
        compiled_patterns.append(compiled_pattern)
    
    return compiled_patterns



# Helper function to verify file existence
# def verify_file_exists(filepath):
#     if os.path.exists(filepath):
#         print(f"File found: {filepath}")
#         return True
#     else:
#         print(f"File not found: {filepath}")
#         print("Please enter the correct file path.")
#         return False

# Main part of the script
def open_csv():
    csv_file_path = select_csv_file()
    if csv_file_path:  # Check if a file was selected
        print(f"File selected: {csv_file_path}")
        unique_selected_data = select_and_display_columns(csv_file_path)
        if unique_selected_data:  # Ensure unique_selected_data is not empty
            compiled_patterns = make_unique_selected_data_to_regex(unique_selected_data)
            return compiled_patterns  # Return the compiled regex patterns
        else:
            print("No data was selected or an error occurred.")
            return []  # Return an empty list if there's an error or no data
    else:
        print("No CSV file was selected.")
        return []  # Return an empty list if no file was selected






def specify_file_paths_to_ignore():
    global ignore_paths_keywords
    print("Current file paths to ignore:", ignore_paths_keywords)
    new_ignore_paths = input("Enter file paths to ignore separated by ',' (e.g., 'temp,backup'): ").strip()
    if new_ignore_paths:
        ignore_paths_keywords.extend([path.strip() for path in new_ignore_paths.split(',') if path.strip()])
        print("Updated file paths to ignore:", ignore_paths_keywords)
    else:
        print("No changes made to file paths to ignore.")

def specify_dirs_to_exclude():
    global exclude_dirs
    print("Current directories to exclude:", exclude_dirs)
    new_exclude_dirs_input = input("Enter directories to exclude separated by ',' (e.g., 'C:\\temp,D:\\backup'): ").strip()
    if new_exclude_dirs_input:
        new_exclude_dirs = [dir_path.strip() for dir_path in new_exclude_dirs_input.split(',') if dir_path.strip()]
        valid_dirs, invalid_dirs = validate_directories(new_exclude_dirs)
        if valid_dirs:
            exclude_dirs.extend(valid_dirs)
            print("Updated directories to exclude:")
            for valid_dir in valid_dirs:
                print(f" - {valid_dir}")
        if invalid_dirs:
            print("The following directories are not valid and will be ignored:")
            for invalid_dir in invalid_dirs:
                print(f" - {invalid_dir}")
    else:
        print("No changes made to directories to exclude.")



def process_pattern(pattern):
    # Initialize the final pattern variable
    final_pattern = pattern

    # Patterns to match the 'case' and 'whole' directives
    case_pattern = re.compile(r'^case\((.*)\)$')
    whole_pattern = re.compile(r'^whole\((.*)\)$')

    # Flags for detected directives
    is_case = False
    is_whole = False

    # Attempt to match and process 'case' and 'whole' directives
    while True:
        case_match = case_pattern.match(final_pattern)
        whole_match = whole_pattern.match(final_pattern)

        if case_match:
            is_case = True
            final_pattern = case_match.group(1)  # Update final_pattern to the captured group
        elif whole_match:
            is_whole = True
            final_pattern = whole_match.group(1)  # Update final_pattern to the captured group
        else:
            break  # Exit loop if no more matches

    # Apply whole word boundaries if 'whole' directive was detected
    if is_whole:
        final_pattern = r'\b' + final_pattern + r'\b'

    # Compile the final pattern with or without case sensitivity based on 'case' directive
    if is_case:
        processed_pattern = re.compile(final_pattern)
    else:
        processed_pattern = re.compile(final_pattern, re.IGNORECASE)

    return processed_pattern
# Combined Patterns (Both Basic and Advanced)
def compile_all_patterns(basic_patterns, advanced_patterns, custom_patterns):
    compiled_patterns = []

    # Compile basic patterns, with special handling for case-sensitive patterns
    for pattern in basic_patterns:
        compiled_patterns.append(process_pattern(pattern))

    # Compile advanced patterns, assuming they already handle case sensitivity as needed
    for pattern in advanced_patterns:
        if isinstance(pattern, str):
            compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
        else:  # Assuming advanced patterns are already compiled regex objects
            compiled_patterns.append(pattern)
    
    # Compile custom patterns, assuming they're input as raw strings by the user
    for pattern in custom_patterns:
        if isinstance(pattern, str):
            compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
        else:  # Assuming custom patterns are already compiled regex objects
            compiled_patterns.append(pattern)

    return compiled_patterns


# This function processes a single file against compiled patterns.
def search_file(file_path, compiled_patterns):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for pattern in compiled_patterns:
                for i, line in enumerate(lines, 1):
                    if pattern.search(line):
                        matches.append((file_path, pattern.pattern, line.strip(), i))
    except UnicodeDecodeError:
        print(f"Skipping file due to encoding issues: {file_path}")
    return matches

def search_files(directory, patterns, file_extensions, include_subdirs=True, exclude_dirs=None, ignore_paths_keywords=None):
    matches_dict = {}
    compiled_patterns = patterns
    files_to_search = []

    directory = os.path.abspath(directory)  # Convert to absolute path for safety

    if exclude_dirs:
        exclude_dirs = [os.path.abspath(dir_path) for dir_path in exclude_dirs]

    # Compile ignore paths patterns for efficiency
    ignore_patterns = []
    if ignore_paths_keywords:
        ignore_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in ignore_paths_keywords]

    for root, dirs, files in os.walk(directory, topdown=True):
        if not include_subdirs:
            dirs.clear()

        if exclude_dirs:
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]

        # Apply ignore patterns to filter dirs and files before adding them to the search list
        dirs[:] = [d for d in dirs if not any(pat.search(os.path.join(root, d)) for pat in ignore_patterns)]
        filtered_files = [f for f in files if not any(pat.search(os.path.join(root, f)) for pat in ignore_patterns)]

        for file in filtered_files:
            if '*' in file_extensions or any(file.endswith('.' + ext) for ext in file_extensions):
                files_to_search.append(os.path.join(root, file))

    # Use ThreadPoolExecutor to process files in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(search_file, file, compiled_patterns): file for file in files_to_search}
        for future in concurrent.futures.as_completed(future_to_file):
            matches = future.result()
            for file_path, pattern_str, line, line_number in matches:
                if file_path not in matches_dict:
                    matches_dict[file_path] = {
                        "file location": file_path,
                        "patterns": [],
                        "matched lines": [],
                        "line numbers": []
                    }
                if pattern_str not in matches_dict[file_path]["patterns"]:
                    matches_dict[file_path]["patterns"].append(pattern_str)
                matches_dict[file_path]["matched lines"].append(line)
                matches_dict[file_path]["line numbers"].append(line_number)

    return list(matches_dict.values())



def validate_exclude_dirs(exclude_dirs):
    valid_dirs = [os.path.abspath(dir_path) for dir_path in exclude_dirs if os.path.isdir(os.path.abspath(dir_path))]
    invalid_dirs = [dir_path for dir_path in exclude_dirs if not os.path.isdir(os.path.abspath(dir_path))]

    # Notify about valid and invalid excluded directories
    if invalid_dirs:
        print("The following paths in your excluded dirs are not valid directories:")
        for invalid_dir in invalid_dirs:
            print(f" - {invalid_dir}")
    if valid_dirs:
        print("The valid excluded dirs are:")
        for valid_dir in valid_dirs:
            print(f" - {valid_dir}")

    return valid_dirs

 


def validate_specific_dirs(specific_dirs, base_directory):
    """Validate specific_dirs paths and inform the user about any invalid ones."""
    valid_dirs = []
    print("Your current selected directories to search include:", specific_dirs)
    for dir_path in specific_dirs:
        # Construct the full path assuming specific_dirs are relative to base_directory
        full_path = os.path.abspath(os.path.join(base_directory, dir_path))
        if is_valid_path(full_path):
            valid_dirs.append(dir_path)
        else:
            print(f"{dir_path} is not a valid path")
    return valid_dirs

def is_valid_path(path):
    """Check if the provided path is valid and is a directory."""
    return os.path.isdir(path)

def get_user_confirmation(prompt):
    """Utility function to get yes/no answers from the user."""
    answer = input(prompt + " (yes/no/back): ").lower()
    while answer not in ["yes", "no", "back"]:
        answer = input("Please enter 'yes', 'no', or 'back': ").lower()
    return answer

def generate_filename_prefix(specific_dirs, basic_patterns, max_length=60):
    """Generate a concise filename prefix within the max_length limit."""
    dir_names = "_".join([os.path.basename(dir_path) for dir_path in specific_dirs])
    patterns_str = "_".join(basic_patterns).replace('*', 'all')
    
    # Construct the base filename and ensure it does not exceed max_length
    base_filename = f"{dir_names}_{patterns_str}_matches"
    if len(base_filename) > max_length:
        return base_filename[:max_length-6] + "...-"
    return base_filename

def save_matches(df, output_type, specific_dirs, basic_patterns):
    """Save the DataFrame of matches to a file in the specified format."""
    
    # Construct the filename prefix
    filename_prefix = generate_filename_prefix(specific_dirs, basic_patterns)
    
    if not df.empty:
        filename = f"{filename_prefix}.{output_type}"
        
        # Determine the output format and save accordingly
        if output_type == 'csv':
            df.to_csv(filename, index=False)
        elif output_type == 'xlsx':
            df.to_excel(filename, index=False)
        elif output_type == 'html':
            df.to_html(filename, index=False)
        else:
            print(f"Unsupported file type: {output_type}")
            return
        
        print(f"Matches saved to {filename}")
    else:
        print("No matches found.")


def test_current_patterns_against_test_strings():
    compiled_patterns = compile_all_patterns(basic_patterns, advanced_patterns, custom_patterns)
    
    # Predefined default test strings
    default_test_strings = [
        'This is a test for caffeine.',
        'I am allergic to Ragweed.',
        'Coconut oil is good for health.',
        'Fish and oats are included.',
        'Shrimp and oysters are seafood.',
        'ALCoHOl consumption is restricted.',
        'papaya is a tropical fruit. 1',
        'Test1 and TEST1 ! = 10 ) 343 fksjf !*(&). bbtest1bb test2  sffdtest3./'
    ]
    default_test_strings_display = "\n".join(default_test_strings)

    # Allow the user to choose between using a custom test string or default test strings
    user_choice = input(f"\nDo you want to input a custom test string? If no, the following default test strings will be used:\n\n{default_test_strings_display}\n\n(yes/no): ").strip().lower()

    test_strings = []
    if user_choice == 'yes':
        custom_test_string = input("Enter your custom test string: ")
        test_strings.append(custom_test_string)
    else:
        test_strings = default_test_strings

    # Check each test string against all compiled patterns
    for test_string in test_strings:
        print(f"\nTesting: \"{test_string}\"")
        for pattern in compiled_patterns:
            match = pattern.search(test_string)
            if match:
                print(f"Match found: \"{match.group()}\" with pattern: {pattern.pattern}")
            else:
                print(f"No match for pattern: {pattern.pattern}")


def add_basic_patterns():
    global basic_patterns
    if basic_patterns:
        view_current_patterns()
        print("Basic patterns already exist. Do you want to overwrite them?")
        overwrite = input("Enter 'yes' to overwrite or 'no' to add more patterns: ").strip().lower()
        if overwrite == 'yes':
            basic_patterns = []
        else:
            patterns_input = input("Enter basic patterns separated by ',' (e.g., 'pattern1,pattern2') \nYou may also wrap word in 'whole()' or 'case()' directives, (learn more in pattern management readme), (e.g., 'whole(pattern1),case(PaTtErn2), whole(case(pATTERn3))'):\n")
            basic_patterns.extend([pattern.strip() for pattern in patterns_input.split(',') if pattern.strip()])
            
            print("Basic patterns added.")
            view_current_patterns()
            return

    else: 
        patterns_input = input("Enter basic patterns separated by ',' (e.g., 'pattern1,pattern2') \nYou may also wrap word in 'whole()' or 'case()' directives, (learn more in pattern management readme), (e.g., 'whole(pattern1),case(PaTtErn2), whole(case(pATTERn3))'):\n")
        basic_patterns = [pattern.strip() for pattern in patterns_input.split(',') if pattern.strip()]
        print("Basic patterns added.")
       
        view_current_patterns()

def add_patterns_from_csv():
    global advanced_patterns
    advanced_patterns.extend(open_csv())  # Assuming open_csv() returns a list of patterns
    print("Patterns from CSV added.")
def list_regex_examples():
    return [
        ("\\btest\\b", "Matches 'test' as a whole word.", "Example match: 'test'", "Example non-match: 'testing'"),
        ("\\d{2,3}\\b", "Matches 2 or 3 digit numbers at word boundaries.", "Example match: '123'", "Example non-match: '1234'"),
        ("[a-zA-Z]+", "Matches one or more letters.", "Example match: 'hello'", "Example non-match: '1234'"),
        ("^\\w+", "Matches the beginning of a string with one or more word characters.", "Example match: 'hello'", "Example non-match: ' hello'"),
        ("\\b\\w{4}\\b", "Matches exactly 4 letter words.", "Example match: 'word'", "Example non-match: 'words'"),
        ("[A-Z][a-z]+", "Matches words starting with a capital letter.", "Example match: 'Hello'", "Example non-match: 'hello'"),
        ("\\b(?:test|text)\\b", "Matches either 'test' or 'text' as whole words.", "Example match: 'test'", "Example non-match: 'testing'"),
        ("\\d+(?:\\.\\d+)?", "Matches integers or decimals.", "Example match: '1.23'", "Example non-match: 'abc'"),
        ("(?<=@)\\w+", "Matches a word following '@' character without including '@'.", "Example match: 'user' in '@user'", "Example non-match: 'user' in 'user@'"),
    ]
def add_custom_patterns():
    while True:
        print("\nWould you like to:")
        print("1) Enter your custom regex pattern manually.")
        print("2) Read in regex from a text file.")
        choice = input("Please enter 1 or 2: ").strip()

        if choice == '1':
            print("\n***************************************************************************************************************************************************************")
            print("Regex pattern examples:")
            regex_examples = list_regex_examples()
            for pattern, description, example_match, example_non_match in regex_examples:
                print(f" - Pattern: '{pattern}' => {description}\n   Example match: {example_match}\n   Example non-match: {example_non_match}\n")
            custom_pattern = input("Enter your custom regex pattern: ").strip()
            # Compile the pattern before adding
            try:
                compiled_custom_pattern = re.compile(custom_pattern)
                custom_patterns.append(compiled_custom_pattern)  # Add the compiled pattern
                print("Custom pattern added.")
            except re.error as e:
                print(f"Regex error: {e}. Please enter a valid regex pattern.")
        elif choice == '2':
            file_path = select_text_file()  # Use the select_text_file function
            if file_path:  # Check if a file was selected
                invalid_patterns = []  # To keep track of invalid patterns
                with open(file_path, "r") as file:
                    for line in file:
                        custom_pattern = line.strip()
                        if custom_pattern:  # Ensure non-empty pattern
                            try:
                                # Attempt to compile the custom pattern
                                compiled_custom_pattern = re.compile(custom_pattern)
                                custom_patterns.append(compiled_custom_pattern)  # Add the compiled pattern
                            except re.error as e:
                                # If an error occurs, add the pattern to the list of invalid patterns
                                invalid_patterns.append(custom_pattern)
                if invalid_patterns:
                    print(f"Some patterns were invalid and not added: {', '.join(invalid_patterns)}")
                else:
                    print(f"Custom patterns added from {file_path}.")
            else:
                print("No file was selected.")

        else:
            print("Invalid choice. Please enter 1 or 2.")
            continue

        # Proceed to test the patterns
        test_current_patterns_against_test_strings()
        
        add_more = input("\nDo you want to add more custom patterns? (yes to add more, anything else to finish): ").strip().lower()
        if add_more != 'yes':  # More explicit check
            break

def view_current_patterns():
    print("Currently applied patterns:")
    print("Basic patterns:", [pattern for pattern in basic_patterns])
    print("Advanced patterns from CSV:", [pattern.pattern for pattern in advanced_patterns])
    print("Custom patterns:", [pattern.pattern for pattern in custom_patterns])


def view_current_directories():
    print("Current selected directories:")
    for directory in specific_dirs:
        print(directory)
def view_file_types_to_search():
    print("Current file types to search:", file_extensions if file_extensions else "All")


def view_excluded_dirs_and_file_paths():
    global exclude_dirs, ignore_paths_keywords
    print("Currently excluded directories:")
    if exclude_dirs:
        for directory in exclude_dirs:
            print(f" - {directory}")
    else:
        print(" - None")

    print("\nCurrently ignored file paths (keywords):")
    if ignore_paths_keywords:
        for keyword in ignore_paths_keywords:
            print(f" - {keyword}")
    else:
        print(" - None")


def select_search_directory():
    global specific_dirs
    while True:
        print(f"Current search directories: {', '.join(specific_dirs)}")
        print("Would you like to change the search directories? (y/n)")
        change_dirs = input().strip().lower()
        if change_dirs == 'y':
            new_dirs_input = input("Enter new directories separated by ',' (e.g., 'C:\\Users\\,D:\\Data'): ").strip()
            new_dirs = [dir_path.strip() for dir_path in new_dirs_input.split(',') if dir_path.strip()]
            valid_dirs, invalid_dirs = validate_directories(new_dirs)
            
            if valid_dirs:
                specific_dirs = valid_dirs  # Update specific_dirs with valid directories only
                print("Updated search directories:")
                for valid_dir in valid_dirs:
                    print(f" - {valid_dir}")
                
            if invalid_dirs:
                print("The following directories are not valid and will be ignored:")
                for invalid_dir in invalid_dirs:
                    print(f" - {invalid_dir}")
            break  # Exit after updating or deciding not to change directories
        elif change_dirs == 'n':
            break
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")



def validate_directories(dir_paths):
    """Validate the given list of directory paths and return two lists: valid and invalid directories."""
    valid_dirs = [dir_path for dir_path in dir_paths if os.path.isdir(dir_path)]
    invalid_dirs = [dir_path for dir_path in dir_paths if not os.path.isdir(dir_path)]
    return valid_dirs, invalid_dirs


def pattern_management():
    while True:
        print("\nPattern Management:")
        print("1) Add basic patterns")
        print("2) Add patterns from CSV")
        print("3) Test current patterns against test strings")
        print("4) Add custom patterns (Future feature)")
        print("5) Back")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_basic_patterns()
        elif choice == "2":
            add_patterns_from_csv()
        elif choice == "3":
            test_current_patterns_against_test_strings()
        elif choice == "4":
            add_custom_patterns()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

def search_directory_configuration():
    global specific_dirs
    while True:
        print("\nSearch Directory Configuration:")
        print("1) Change search directories")
        print("2) Change file types to search")
        print("4) View current search directories")
        print("5) View file types to search")
        print("6) Back")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            select_search_directory()
        elif choice == "2":
            select_file_types()

        elif choice == "4":
            view_current_directories()
        elif choice == "5":
            view_file_types_to_search()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")
def exclusion_settings():
    while True:
        print("\nExclusion Settings:")
        print("1) Specify file paths to ignore")
        print("2) Specify directories to exclude")
        print("3) Back")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            specify_file_paths_to_ignore()
        elif choice == "2":
            specify_dirs_to_exclude()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")
def view_excluded_dirs():
    global exclude_dirs
    print("\nCurrently excluded directories:")
    if exclude_dirs:
        for directory in exclude_dirs:
            print(f" - {directory}")
    else:
        print(" - None")

def view_ignored_file_paths():
    global ignore_paths_keywords
    print("\nCurrently ignored file paths (keywords):")
    if ignore_paths_keywords:
        for keyword in ignore_paths_keywords:
            print(f" - {keyword}")
    else:
        print(" - None")

def view_configuration_menu():
    while True:
        print("\nView Configuration:")
        print("1) View applied patterns")
        print("2) View current search directories")
        print("3) View applied file types to search")
        print("4) View excluded directories")
        print("5) View ignored file paths")
        print("6) Back")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            view_current_patterns()
        elif choice == "2":
            view_current_directories()
        elif choice == "3":
            view_file_types_to_search()
        elif choice == "4":
            view_excluded_dirs()
        elif choice == "5":
            view_ignored_file_paths()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")
def select_file_types():
    global file_extensions
    # print("\nCurrent file types to search:", file_extensions if file_extensions else "All")
    new_file_types = input("Enter file extensions separated by ',' (e.g., 'txt,log,csv') or '*' for any: ").strip()
    if new_file_types == '*':
        file_extensions = ['*']
    else:
        file_extensions = [ext.strip() for ext in new_file_types.split(',') if ext.strip()]
    print("Updated file types to search:", file_extensions if file_extensions != ['*'] else "Any")

def start_search():
    if not basic_patterns and not advanced_patterns and not custom_patterns:
        print("No search patterns specified. Please add patterns before starting the search.")
        return

    compiled_patterns = compile_all_patterns(basic_patterns, advanced_patterns, custom_patterns)

    # Check if file extensions have been specified, if not, ask for them
    if not file_extensions:
        select_file_types()
    else:
        print("Current file types to search:", file_extensions if file_extensions != ['*'] else "Any")
        change_file_types = input("Would you like to change the file types to search? (yes/no): ").strip().lower()
        if change_file_types == "yes":
            select_file_types()

    search_depth = input("Do you want to search in subdirectories as well? (yes/no): ").strip().lower()
    include_subdirs = search_depth == "yes"
    print("\nStarting search with the following configurations:")
    print("- Directories:", specific_dirs)
    print("- Excluded Directories:", exclude_dirs)
    print("- Ignored File Paths:", ignore_paths_keywords)
    print("- File Types:", file_extensions if file_extensions != ['*'] else "Any")
    print("- Patterns:", [pattern.pattern for pattern in compiled_patterns])
    print("- Include Subdirectories:", "Yes" if include_subdirs else "No")
    # Starting the search with the specified configurations
    print("\nStarting search...")
    # Placeholder for search logic; implement the search using the search_files function

    # Iterate through each directory specified in specific_dirs
    all_matches = []
    for directory in specific_dirs:
        matches = search_files(directory, compiled_patterns, file_extensions, include_subdirs, exclude_dirs, ignore_paths_keywords)
        all_matches.extend(matches)

    # Handling the results
    if all_matches:
        print(f"Found {len(all_matches)} matches.")
        df_matches = pd.DataFrame(all_matches)
        output_type = input("Enter the output file type (csv/xlsx/html): ").strip().lower()
        save_matches(df_matches, output_type, specific_dirs, basic_patterns)
    else:
        print("No matches found.")

    # Optionally, you can save the results to a file or further process them

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1) Search Directory Configuration")
        print("2) Pattern Management")
        print("3) Exclusion Settings")
        print("4) View Current Configuration")
        print("5) Start Search")
        print("6) Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            search_directory_configuration()
        elif choice == "2":
            pattern_management()
        elif choice == "3":
            exclusion_settings()
        elif choice == "4":
            view_configuration_menu()
        elif choice == "5":
            start_search()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")


if __name__ == "__main__":
    main_menu()



