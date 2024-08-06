import os
import re
import pandas as pd
import concurrent.futures
import subprocess
import sys


import tkinter as tk
from tkinter import filedialog

specific_dirs = [r"N:\cclprod"]
basic_patterns = []
csv_patterns = []
custom_patterns = []
ignore_paths_keywords = []
exclude_dirs = []
file_extensions = []
root = tk.Tk()
root.withdraw()

def select_outdump_file():
    try:
        # Use the global root window for the file dialog
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(parent=root, title="Select an Outdump file", filetypes=[("Outdump files", "*.dat")])
        root.attributes('-topmost', False)
        
        if not file_path:
            print("Outdump file selection was canceled. Returning to the previous menu.")
            return None
        return file_path
    except Exception as e:
        print(f"An error occurred while selecting an outdump file: {e}")
        return None


                
def select_csv_file():
    try:
        # Use the global root window for the file dialog
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(parent=root, title="Select a CSV file", filetypes=[("CSV files", "*.csv")])
        root.attributes('-topmost', False)
        
        if not file_path:
            print("File selection was canceled. Returning to the previous menu.")
            return None
        return file_path
    except Exception as e:
        print(f"An error occurred while selecting a file: {e}")
        return None


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def open_text_file(file_name):
    file_path = resource_path(file_name)
    try:
        if sys.platform.startswith('win'):
            # Windows
            os.startfile(file_path)
        elif sys.platform.startswith('darwin'):
            # macOS
            subprocess.run(['open', file_path], check=True)
        elif sys.platform.startswith('linux') or sys.platform.startswith('linux2'):
            # Linux
            subprocess.run(['xdg-open', file_path], check=True)
        else:
            print(f"Unsupported OS: {sys.platform}")
    except Exception as e:
        print(f"Failed to open file: {e}")

def select_text_file():
    try:
        # Use the global root window for the file dialog
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(parent=root, title="Select a text file", filetypes=[("Text files", "*.txt")])
        root.attributes('-topmost', False)

        if not file_path:
            print("File selection was canceled. Returning to the previous menu.")
            return None
        return file_path
    except Exception as e:
        print(f"An error occurred while selecting a file: {e}")
        return None

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
def make_unique_selected_data_to_regex(unique_selected_data):
    # Ask the user if they want the regex to be case-sensitive
    case_sensitive = input("Would you like the regex to be case-sensitive? (yes/no): ").lower().startswith('y')
    sensitivity = "case-sensitive" if case_sensitive else "case-insensitive"

    # Ask the user if they want whole word matching
    whole_word = input("Would you like to match whole words only? (yes/no): ").lower().startswith('y')

    pattern_objects = []
    for header, data in unique_selected_data.items():
        # Apply whole word boundaries (\b) if whole word matching is desired
        if whole_word:
            escaped_data = [r"\b" + re.escape(str(value)) + r"\b" for value in data]
        else:
            escaped_data = [re.escape(str(value)) for value in data]

        regex_pattern = '|'.join(escaped_data)
        
        # Create a pattern object with the desired configuration
        pattern_object = {
            'pattern': regex_pattern,
            'sensitivity': sensitivity,
            'whole': whole_word
        }
        pattern_objects.append(pattern_object)
    
    return pattern_objects

def select_and_display_columns(csv_filepath):
    df = pd.read_csv(csv_filepath)
    
    original_headers = df.columns.tolist()
    lower_to_original = {header.lower(): header for header in original_headers}
    
    while True:
        print("\nAvailable columns in the CSV file:")
        for idx, header in enumerate(original_headers, 1):
            print(f"{idx}. {header}")

        selected_headers_input = input("\nIf you would like to go back type 'back'.\nWhich columns do you want to use? (Enter as a comma-separated list or type 'back' to return): ").lower()
        if selected_headers_input == 'back':
            return {}
        
        selected_headers = [header.strip() for header in selected_headers_input.split(',')]
        selected_headers = [lower_to_original.get(header, '') for header in selected_headers]
        selected_headers = [header for header in selected_headers if header]
        
        if not selected_headers:
            print("None of the entered column headers were found. Please check for typos and try again.")
            continue

        print(f"Selecting data from {', '.join(selected_headers)}")
        confirmation = input("Proceed with these columns? (yes/no/back): ").lower()
        if confirmation == 'back':
            continue
        elif confirmation != 'yes':
            return 'back'

        unique_selected_data = {}
        for header in selected_headers:
            print(f"\nData for column '{header}':")
            for idx, value in enumerate(df[header].unique(), 1):
                print(f"{idx}. {value}")
        for header in selected_headers:
            # print(f"\nData for column '{header}':")
            contains_trailing_zeros = False
            for value in df[header].unique():
                if isinstance(value, float) and value.is_integer():
                    contains_trailing_zeros = True
                    break
            
            strip_trailing_zero = 'no'
            if contains_trailing_zeros:
                strip_trailing_zero = input(f"Column '{header}' contains float values with trailing zeros. Do you want to strip trailing .0 from float values in this column? (yes/no/back): \nThis is best for searching ids in the code base with trailing 0's. code base often references ids without trailing .0's ").lower()
                if strip_trailing_zero == 'back':
                    return 'back'
                elif strip_trailing_zero not in ['yes', 'no']:
                    print("Invalid input. Please enter 'yes', 'no', or 'back'.")
                    continue
            # print every 


            row_selection = input(f"Which rows would you like to use from {header}? (Enter like: 1-5,8-10,20 or * for all rows or type 'back' to return): ")
            if row_selection == 'back':
                return 'back'

            selected_rows = get_row_indices_from_input(row_selection, len(df))
            selected_data = df.iloc[selected_rows][header].dropna().unique().tolist()
            if strip_trailing_zero == 'yes':
                selected_data = [int(value) if isinstance(value, float) and value.is_integer() else value for value in selected_data]
            unique_selected_data[header] = list(set(selected_data))

        print("\nHere are the unique rows selected for each column:")
        for header, data in unique_selected_data.items():
            data_str = ', '.join(str(v) for v in data)
            print(f"{header}: {data_str}")

        return unique_selected_data

def add_patterns_from_csv():
    global csv_patterns
    csv_patterns.extend(open_csv())  # Assuming open_csv() returns a list of patterns
    print("Patterns from CSV added.")



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

    # Flags for detected directives
    is_case = False
    is_whole = False

    # Patterns to match the 'case' and 'whole' directives
    case_pattern = re.compile(r'^case\((.*)\)$')
    whole_pattern = re.compile(r'^whole\((.*)\)$')

    # Attempt to match and process 'case' and 'whole' directives
    while True:
        case_match = case_pattern.match(final_pattern)
        whole_match = whole_pattern.match(final_pattern)

        if case_match:
            is_case = True
            final_pattern = case_match.group(1)
        elif whole_match:
            is_whole = True
            final_pattern = whole_match.group(1)
        else:
            break

    # Apply whole word boundaries if 'whole' directive was detected
    final_pattern = r'\b' + final_pattern + r'\b' if is_whole else final_pattern

    # Determine sensitivity
    sensitivity = "case-sensitive" if is_case else "case-insensitive"

    # Return a pattern object instead of compiling the regex
    pattern_object = {
        'pattern': final_pattern,
        'sensitivity': sensitivity,
        'whole': is_whole
    }

    return pattern_object




def search_file(file_path, pattern_objects):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):  # Iterate through each line
                for obj in pattern_objects:  # For each line, check against all patterns
                    if obj.get('isCustomPattern'):
                        pattern = re.compile(obj['pattern'])
                    else:
                        regex_flag = 0 if obj.get('sensitivity', '') == 'case-sensitive' else re.IGNORECASE
                        pattern = re.compile(obj['pattern'], regex_flag)
                    if pattern.search(line):  # If a match is found, append it to the matches list
                        matches.append((file_path, obj['pattern'], line.strip(), i))
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
    
    # Sanitize each pattern to remove or replace invalid filename characters
    sanitized_patterns = []
    for pattern in basic_patterns:
        sanitized = re.sub(r'[\\/*?:"<>|]+', "_", pattern)  # Replace invalid characters with an underscore
        sanitized_patterns.append(sanitized)
    
    patterns_str = "_".join(sanitized_patterns).replace('*', 'all').replace('\\b', '')

    # Construct the base filename and ensure it does not exceed max_length
    base_filename = f"{dir_names}_{patterns_str}_matches"
    if len(base_filename) > max_length:
        return base_filename[:max_length-3] + "..."
    return base_filename


def save_matches(df, output_type, specific_dirs, basic_patterns):
    """Save the DataFrame of matches to a file in the specified format."""
    
    if df.empty:
        print("No matches found.")
        return

    # Construct the filename prefix
    filename_prefix = generate_filename_prefix(specific_dirs, basic_patterns)

    # Set up the file dialog options
    file_types = {
        'csv': [('CSV files', '*.csv')],
        'xlsx': [('Excel files', '*.xlsx')],
        'html': [('HTML files', '*.html')]
    }
    file_extension = file_types.get(output_type, [('All Files', '*.*')])
    
    # Prompt the user for a location to save the file
  
    root.attributes('-topmost', True)  # Bring the dialog on top
    save_path = filedialog.asksaveasfilename(
        defaultextension=f".{output_type}",
        filetypes=file_extension,
        title="Save the matches to a file",
        initialfile=filename_prefix
    )
    root.attributes('-topmost', False)  # Remove the always on top attribute

    if not save_path:  # If the user cancels the save dialog
        print("Save operation cancelled.")
        return

    # Save the DataFrame to the specified file type
    if output_type == 'csv':
        df.to_csv(save_path, index=False)
    elif output_type == 'xlsx':
        df.to_excel(save_path, index=False)
    elif output_type == 'html':
        df.to_html(save_path, index=False)

    print(f"Matches saved to {save_path}")

    # Open the saved file with the default application
    if os.path.exists(save_path):
        if sys.platform.startswith('win'):
            os.startfile(save_path)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', save_path])
        elif sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', save_path])
        else:
            print("The file has been saved, but automatic opening is not supported on this OS.")
            print(f"Please open the following file manually: {save_path}")

def test_current_patterns_against_test_strings():
    print("Select the group of patterns to test:")
    print("1) Test basic patterns")
    print("2) Test csv patterns")
    print("3) Test custom patterns")
    print("4) Test all patterns")
    print("5) Back")
    pattern_choice = input("Enter your choice (1/2/3/4): ").strip()

    if pattern_choice == '1':
        pattern_objects = basic_patterns
    elif pattern_choice == '2':
        pattern_objects = csv_patterns
    elif pattern_choice == '3':
        pattern_objects = custom_patterns
    elif pattern_choice == '4':
        pattern_objects = basic_patterns + csv_patterns + custom_patterns
    elif pattern_choice == '5':
        return
    else:
        print("Invalid choice. Testing all patterns by default.")
        pattern_objects = basic_patterns + csv_patterns + custom_patterns

    print("\nPatterns selected for testing:")
    for obj in pattern_objects:
        if obj.get('isCustomPattern'):
            print(f" - Custom Pattern: {obj['pattern']}")
        else:
            print(f" - Pattern: {obj['pattern']}, Sensitivity: {obj.get('sensitivity', 'N/A')}, Whole word: {obj.get('whole', 'N/A')}")

    default_test_strings = [
        'This is a test for caffeine.',
        # Add the rest of your test strings here...
    ]
    default_test_strings_display = "\n".join(default_test_strings)

    user_choice = input(f"\nDo you want to input a custom test string? If no, the following default test strings will be used against your patterns:\n\n{default_test_strings_display}\n\n(yes/no): ").strip().lower()

    test_strings = []
    if user_choice == 'yes':
        custom_test_string = input("Enter your custom test string: ")
        test_strings.append(custom_test_string)
    else:
        test_strings = default_test_strings

    for test_string in test_strings:
        print(f"\nTesting: \"{test_string}\"")
        for obj in pattern_objects:
            # Adjust the logic to skip the sensitivity and whole flags for custom patterns
            if obj.get('isCustomPattern'):
                pattern = re.compile(obj['pattern'])  # Directly compile without flags
            else:
                regex_flag = 0 if obj.get('sensitivity', 'case-insensitive') == 'case-sensitive' else re.IGNORECASE
                pattern = re.compile(obj['pattern'], regex_flag)
            
            match = pattern.search(test_string)
            if match:
                match_info = f"Match found: \"{match.group()}\" with pattern: {obj['pattern']}"
                if not obj.get('isCustomPattern'):
                    match_info += f" (Whole word: {obj.get('whole', 'N/A')}) and Sensitivity: {obj.get('sensitivity', 'N/A')}"
                print(match_info)
            else:
                no_match_info = f"No match for pattern: {obj['pattern']}"
                if not obj.get('isCustomPattern'):
                    no_match_info += f" (Whole word: {obj.get('whole', 'N/A')}) and Sensitivity: {obj.get('sensitivity', 'N/A')}"
                print(no_match_info)
def example_basic_patterns():
    
            return[
        ("searchword", "Matches 'searchword' as part of a word with case insensitivity.", "Example match: 'SearchWord' or 'searchwords'", "Example non-match: 'wordsearch'"),
        ("whole(searchword)", "Matches 'searchword' as a whole word.", "Example match: 'searchword'", "Example non-match: 'searchwords'"),
        ("case(SearchWord)", "Matches 'searchword' with case sensitivity.", "Example match: 'SearchWord'", "Example non-match: 'searchword'"),
        ("whole(case(SearchWord))", "Matches 'searchword' as a whole word with case sensitivity.", "Example match: 'SearchWord'", "Example non-match: 'SearchWords'"),
            ]
       

def add_basic_patterns():
    global basic_patterns
    if basic_patterns:
        view_current_patterns()
        print("Basic patterns already exist. Do you want to overwrite them?")
        overwrite = input("Enter 'yes' to overwrite or 'no' to add more patterns: ").strip().lower()
        if overwrite == 'yes':
            basic_patterns = []
        else:
            #print example basic patterns
            print("\nSome example basic patterns:\n")
            for i, (pattern, description, match_example, non_match_example) in enumerate(example_basic_patterns(), 1):
                print(f"{i})   {pattern}\n")
                print(f"   - {description}")
                
                print(f"   - Example match: {match_example}")
                print(f"   - Example non-match: {non_match_example}\n")
            print()

            patterns_input = input("\n\nEnter basic patterns separated by ',' (e.g., 'pattern1,pattern2') \nYou may also wrap word in 'whole()' or 'case()' directives (e.g., 'whole(pattern1),case(PaTtErn2), whole(case(pATTERn3))'):\n")
            
            input_patterns = [pattern.strip() for pattern in patterns_input.split(',') if pattern.strip()]
        
        # Process and compile each pattern immediately
            compiled_patterns = [process_pattern(pattern) for pattern in input_patterns]
        
        # Extend the basic_patterns list with the newly compiled patterns
            basic_patterns.extend(compiled_patterns)
            print("Basic patterns added.")
            view_current_patterns()
            return

    else: 
                #print example basic patterns
        print("\nSome example basic patterns:\n")
        for i, (pattern, description, match_example, non_match_example) in enumerate(example_basic_patterns(), 1):
            print(f"{i})   {pattern}\n")
            print(f"   - {description}")
            
            print(f"   - Example match: {match_example}")
            print(f"   - Example non-match: {non_match_example}\n")
        print()
        patterns_input = input("\n\nEnter basic patterns separated by ',' (e.g., 'pattern1,pattern2') \nYou may also wrap word in 'whole()' or 'case()' directives (e.g., 'whole(pattern1),case(PaTtErn2), whole(case(pATTERn3))'):\n")

        input_patterns = [pattern.strip() for pattern in patterns_input.split(',') if pattern.strip()]

        # Process and compile each pattern immediately
        compiled_patterns = [process_pattern(pattern) for pattern in input_patterns]

        # Extend the basic_patterns list with the newly compiled patterns
        basic_patterns.extend(compiled_patterns)


        view_current_patterns()


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
        ("^hello", "Matches a specific word at the beginning of a line.", "Example match: 'hello world'", "Example non-match: 'say hello'"),
        ("world$", "Matches a specific word at the end of a line.", "Example match: 'hello world'", "Example non-match: 'world peace'"),
        ("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", "Matches an email address (simplified pattern).", "Example match: 'email@example.com'", "Example non-match: 'email@com'"),
        ("\\d{4}-\\d{2}-\\d{2}", "Matches a date in yyyy-mm-dd format.", "Example match: '2023-01-01'", "Example non-match: '01-01-2023'"),
        ("(\\(\\d{3}\\)|\\d{3})[-. ]?\\d{3}[-. ]?\\d{4}", "Matches a phone number in various formats.", "Example match: '123-456-7890'", "Example non-match: '1234567890'"),
        ("https?:\\/\\/(www\\.)?[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}(/.*)?", "Matches a URL.", "Example match: 'http://www.example.com'", "Example non-match: 'www.example'"),
        
        ("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}", "Matches an IP address (simplified pattern).", "Example match: '192.168.1.1'", "Example non-match: '192.168.1'"),
        ("([01]?[0-9]|2[0-3]):[0-5][0-9]", "Matches a time in 24-hour format.", "Example match: '23:59'", "Example non-match: '24:00'"),
        ("\\d{5}(-\\d{4})?", "Matches a ZIP code (US).", "Example match: '12345-6789'", "Example non-match: '123456789'"),
        ("-?\\d+(\\.\\d+)?", "Matches a negative or positive integer or decimal.", "Example match: '-123.45'", "Example non-match: 'abc'"),

        ("^\\S+$", "Matches any string without spaces (useful for usernames).", "Example match: 'username'", "Example non-match: 'user name'"),
    ]

def add_custom_patterns():
    global custom_patterns
    while True:
        print("\nWould you like to:")
        print("1) Enter your custom regex pattern manually.")
        print("2) Read in regex from a text file.")
        print("3) View regex examples.")
        print("4) View regex example text file.")
        print("5) Back")
        choice = input("Please enter 1 or 2 to continue or 3 to go back: ").strip()
        
        pattern_added = False
        if choice == '1':
            display_examples = input("Do you want to see some regex examples? (yes/no): ").strip().lower()
            if display_examples == 'yes':
                print("\nSome regex examples:")
                for i, (pattern, description, match_example, non_match_example) in enumerate(list_regex_examples(), 1):
                    print(f"{i}) {description}")
                    print(f"   - {pattern}")
                    print(f"   - Example match: {match_example}")
                    print(f"   - Example non-match: {non_match_example}")
                print()
            custom_pattern = input("Enter your custom regex pattern or type 'back' to go back: ").strip()
            try:
                # Directly store the pattern string with an isCustomPattern flag
                if custom_pattern == 'back':
                    continue

                custom_patterns.append({'pattern': custom_pattern, 'isCustomPattern': True})
                pattern_added = True
                print("Custom pattern added.")
            except re.error as e:
                print(f"Regex error: {e}. Please enter a valid regex pattern.")
        elif choice == '2':
            file_path = select_text_file()  # Assuming this function prompts the user to choose a file and returns the file path
            if file_path:
                invalid_patterns = []  # List to store invalid patterns
                with open(file_path, "r") as file:
                    for line in file:
                        # Strip whitespace and ignore empty lines or lines starting with '#'
                        custom_pattern = line.strip()
                        if custom_pattern and not custom_pattern.startswith('#'):
                            try:
                                # Attempt to compile the pattern to validate its correctness
                                re.compile(custom_pattern)
                                # If compilation succeeds, add it to the custom patterns
                                custom_patterns.append({'pattern': custom_pattern, 'isCustomPattern': True})
                                pattern_added = True
                            except re.error:
                                # If an error occurs during compilation, add to invalid patterns list
                                invalid_patterns.append(custom_pattern)
                
                if invalid_patterns:
                    # If there are any invalid patterns, notify the user
                    print("Some patterns were invalid and not added:")
                    for pattern in invalid_patterns:
                        print(f"Invalid pattern: {pattern}")
                    # Only print "Custom patterns added" if at least one valid pattern was added
                    if pattern_added:
                        print("Valid custom patterns added.")
                elif pattern_added:
                    # If no invalid patterns and at least one pattern was added
                    print("Custom patterns added.")
                else:
                    # If no patterns were added, likely due to all being invalid or file being empty
                    print("No valid patterns were added. Ensure the file contains valid regex patterns and does not only consist of comments or empty lines.")
            else:
                print("No file was selected.")

        elif choice == '3':
            print("\nSome regex examples:")
            for i, (pattern, description, match_example, non_match_example) in enumerate(list_regex_examples(), 1):
                print(f"{i}) {description}")
                print(f"   - {pattern}")
                print(f"   - Example match: {match_example}")
                print(f"   - Example non-match: {non_match_example}")
            print()
        elif choice == '4':
            #open the file
            open_text_file("regex_example_file.txt")

        elif choice == '5':
            break

        else:
            print("Invalid choice. Please enter 1 or 2.")
            continue
        if pattern_added:
            test_pattern = input("Do you want to test the custom pattern against example strings? (yes/no): ").strip().lower()
            while test_pattern == 'yes':
                test_current_patterns_against_test_strings()
                test_pattern = input("Do you want to test the custom pattern again? (yes/no): ").strip().lower()

            add_more = input("\nDo you want to add more custom patterns? (yes to add more, anything else to finish): ").strip().lower()
            if add_more != 'yes':
                break

def view_current_patterns():
    print("Currently applied patterns:")
    
    # Display basic patterns
    if basic_patterns:
        print("Basic patterns:")
        for obj in basic_patterns:
            print(f" - Pattern: {obj['pattern']}, Sensitivity: {obj.get('sensitivity', 'N/A')}, Whole word: {obj.get('whole', 'N/A')}")

    # Display csv patterns from CSV
    if csv_patterns:
        print("csv patterns from CSV:")
        for obj in csv_patterns:
            print(f" - Pattern: {obj['pattern']}, Sensitivity: {obj.get('sensitivity', 'N/A')}, Whole word: {obj.get('whole', 'N/A')}")

    # Display custom patterns, handling them differently
    if custom_patterns:
        print("Custom patterns:")
        for obj in custom_patterns:
            # Directly display the pattern for custom patterns
            print(f" - Custom Pattern: {obj['pattern']}")


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

def clear_all_patterns():
    global basic_patterns, csv_patterns, custom_patterns
    print("Are you sure you want to clear all patterns? This action cannot be undone.")
    confirm_clear = input("Enter 'yes' to clear all patterns: ").strip().lower()
    if confirm_clear == 'yes':
        basic_patterns.clear()
        csv_patterns.clear()
        custom_patterns.clear()
        print("All patterns cleared.")
    else:
        print("No patterns were cleared.")

def clear_patterns():
    global basic_patterns, csv_patterns, custom_patterns
    while True:
        
        print("\nClear Patterns:")
        print("1) Clear all patterns")
        print("2) Clear all basic patterns")
        print("3) Clear all csv patterns")
        print("4) Clear all custom patterns")
        print("5) Clear a specific basic pattern")
        print("6) Clear a specific csv pattern")
        print("7) Clear a specific custom pattern")
      
        print("8) Back")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            clear_all_patterns()
        elif choice == "2":
            if confirm_clear("basic"):
                basic_patterns.clear()
        elif choice == "3":
            if confirm_clear("csv"):
                csv_patterns.clear()
        elif choice == "4":
            if confirm_clear("custom"):
                custom_patterns.clear()
        elif choice in ["5", "6", "7"]:
            pattern_list = basic_patterns if choice == "4" else csv_patterns if choice == "5" else custom_patterns
            clear_specific_pattern(pattern_list)
        elif choice == "8":
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

def confirm_clear(pattern_type):
    print(f"Are you sure you want to clear all {pattern_type} patterns? This action cannot be undone.")
    confirm_clear = input("Enter 'yes' to clear: ").strip().lower()
    if confirm_clear == 'yes':
        print(f"All {pattern_type} patterns cleared.")
        return True
    else:
        print("No patterns were cleared.")
        return False

def clear_specific_pattern(pattern_list):
    if not pattern_list:
        print("There are no patterns to clear.")
        return

    print("\nSelect a pattern to clear:")
    for idx, pattern in enumerate(pattern_list, 1):
        pattern_display = pattern['pattern'] if isinstance(pattern, dict) else pattern
        print(f"{idx}) {pattern_display}")
    
    choice = input("Enter the number of the pattern to clear, or 'back' to return: ").strip().lower()
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(pattern_list):
            removed_pattern = pattern_list.pop(index)
            print(f"Pattern removed: {removed_pattern}")
        else:
            print("Invalid choice. No pattern removed.")
    elif choice == 'back':
        return
    else:
        print("Please enter a valid number or 'back'.")


def validate_directories(dir_paths):
    """Validate the given list of directory paths and return two lists: valid and invalid directories."""
    valid_dirs = [dir_path for dir_path in dir_paths if os.path.isdir(dir_path)]
    invalid_dirs = [dir_path for dir_path in dir_paths if not os.path.isdir(dir_path)]
    return valid_dirs, invalid_dirs


def pattern_management():
    while True:
        print("\nPattern Management:")
        print("1) Add basic patterns")
        print("2) Add patterns from CSV (ex: Using results from adhoc query csv to find results in code base)")
        print("3) Add custom regex patterns")
        print("4) Test current patterns against test strings")
        print("5) View current patterns")
        print("6) Clear patterns")
        print("7) Back")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_basic_patterns()
        elif choice == "2":
            add_patterns_from_csv()
        elif choice == "3":
            add_custom_patterns()   
        elif choice == "4":
            test_current_patterns_against_test_strings()
        elif choice == "5":
            view_current_patterns()
        elif choice == "6":
            clear_patterns()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

def search_directory_configuration():
    global specific_dirs
    while True:
        print("\nSearch Directory Configuration:")
        print("1) Change search directories")
        print("2) Change file types to search")
        print("3) View current search directories")
        print("4) View file types to search")
        print("5) Back")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            select_search_directory()
        elif choice == "2":
            select_file_types()

        elif choice == "3":
            view_current_directories()
        elif choice == "4":
            view_file_types_to_search()
        elif choice == "5":
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
    if not basic_patterns and not csv_patterns and not custom_patterns:
        print("No search patterns specified. Please add patterns before starting the search.")
        return

    # Merge all patterns into a single list of pattern objects
    pattern_objects = basic_patterns + csv_patterns + custom_patterns

    # Extract the pattern strings for display
    pattern_strings = [obj['pattern'] for obj in pattern_objects]

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
    print("- Patterns:", pattern_strings)  # Display the extracted pattern strings
    print("- Include Subdirectories:", "Yes" if include_subdirs else "No")


    confirm_search = input("Are you ready to start the search? (yes/no): ").strip().lower()
    if confirm_search != 'yes':
        print("Search canceled. Returning to main menu...")
        return  # Ex
    print("\nStarting search...")
    # Placeholder for search logic; implement the search using the search_files function

    all_matches = []
    for directory in specific_dirs:
        matches = search_files(directory, pattern_objects, file_extensions, include_subdirs, exclude_dirs, ignore_paths_keywords)  # Pass the original pattern objects here
        all_matches.extend(matches)

    # Handling the results
    if all_matches:
        print(f"Found {len(all_matches)} matches.")
        # Assuming df_matches is correctly defined elsewhere in your search_files function or similar
        df_matches = pd.DataFrame(all_matches)
        output_type = input("Enter the output file type (csv/xlsx/html): ").strip().lower()
        save_matches(df_matches, output_type, specific_dirs, pattern_strings)  # Adjust as necessary for saving logic
    else:
        print("No matches found.")


    # Optionally, you can save the results to a file or further process them

def clean_text(text):
    """
    Remove or replace characters that are not allowed in Excel cells.
    """
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E]+', '', text)
    # Replace other potentially problematic characters as needed, for example:
    text = text.replace('\x00', '')  # Remove NULL characters
    return text

def split_dat_file_to_blocks(input_file_path, skip_compiler_prefix=None, skip_source_prefix=None):
    """
    Reads a .dat file line by line and groups lines into blocks based on starting with
    'CREATE PROGRAM' or 'DROP PROGRAM' and ending with 'END GO'.
    Captures 'Compiled By' and 'Source' information for each block.
    Optionally skips blocks compiled by compilers or sourced from sources starting with specified prefixes.
    Returns a list of tuples, each containing a block's name, its content, compiled by, and source.
    """
    blocks = []
    current_block = []
    block_name = ""
    compiled_by = ""
    source = ""
    da2 = "" 
    ops = "" 
    last_run_by = ""
    in_block = False

    try:
        with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                # Capture compiled by and source information
                if '<<COMPILED_BY:' in line:
                    compiled_by_parts = line.strip().split('<<COMPILED_BY: ')
                    if len(compiled_by_parts) > 1:
                        compiled_by = compiled_by_parts[1].rstrip(' >>')
                    else:
                        compiled_by = "Unknown"
                if '<<SOURCE:' in line:
                    source_parts = line.strip().split('<<SOURCE: ')
                    if len(source_parts) > 1:
                        source = source_parts[1].rstrip(' >>')
                    else:
                        source = "Unknown"
                if '<<DA2:' in line:
                    da2_parts = line.strip().split('<<DA2: ')
                    da2 = da2_parts[1].rstrip(' >>') if len(da2_parts) > 1 else "Unknown"
                if '<<OPS:' in line:
                    ops_parts = line.strip().split('<<OPS: ')
                    ops = ops_parts[1].rstrip(' >>') if len(ops_parts) > 1 else "Unknown"
                if '<<LAST_RUN_BY:' in line:
                    last_run_by_parts = line.strip().split('<<LAST_RUN_BY: ')
                    last_run_by = last_run_by_parts[1].rstrip(' >>') if len(last_run_by_parts) > 1 else "Unknown"


                # Check if the line starts a block
                if 'CREATE PROGRAM' in line or 'DROP PROGRAM' in line:
                    in_block = True
                    block_name = line.split()[2]  # Assuming the name is the third word
                    current_block = [line]  # Start a new block with the current line
                elif 'END GO' in line and in_block:
                    current_block.append(line)
                    if not ((skip_compiler_prefix and compiled_by.lower().startswith(skip_compiler_prefix)) or
                            (skip_source_prefix and skip_source_prefix in source.lower())):
                        # Include da2 and ops in the saved block
                        blocks.append((block_name, '\n'.join(current_block), compiled_by, source, da2, ops, last_run_by))
                    in_block = False
                    compiled_by, source, da2, ops, last_run_by = "", "", "", "", ""  # Reset all for next block
                elif in_block:
                    current_block.append(line)


    except IOError as e:
        print(f"Error reading file {input_file_path}: {e}")

    return blocks



def search_blocks_aggregated(named_blocks, pattern_objects, detailed_output=False):
    """
    Searches through named blocks for specified patterns and compiles matches.
    If detailed_output is True, each pattern gets its own row in the output.
    Ensures that only virtual files with matches are included in the final output.
    Provides progress updates every 100 files.
    """
    total_files = len(named_blocks)  # Total number of virtual files
    aggregated_matches = []
    file_count = 0  # Counter to keep track of how many files have been processed

    for program_name, block_content, compiled_by, source, da2, ops, last_run_by in named_blocks:
        lines = block_content.split('\n')
        pattern_data = {}

        for line_index, line in enumerate(lines, start=1):
            for obj in pattern_objects:
                pattern = re.compile(obj['pattern'], 0 if obj.get('sensitivity', '') == 'case-sensitive' else re.IGNORECASE)
                if pattern.search(line):
                    if obj['pattern'] not in pattern_data:
                        pattern_data[obj['pattern']] = {
                            "Matched Lines": [],
                            "Line Numbers": []
                        }
                    pattern_data[obj['pattern']]["Matched Lines"].append(line.strip())
                    pattern_data[obj['pattern']]["Line Numbers"].append(line_index)

        file_count += 1  # Increment the processed file count

        # Only add entries for virtual files with at least one pattern match
        if pattern_data:
            if detailed_output:
                # Create a single entry per pattern matched in each virtual file
                for pattern, data in pattern_data.items():
                    aggregated_matches.append({
                        "File": program_name,
                        "Pattern": pattern,
                        "Matched Lines": "; ".join(data["Matched Lines"]),
                        "Line Numbers": ", ".join(map(str, data["Line Numbers"])),
                        "Compiled By": compiled_by,
                        "Source": source,
                        "DA2": da2,  # Add DA2 info to the output
                        "OPS": ops,
                        "Last Run By": last_run_by 
                    })
            else:
                # Aggregate all patterns in a single entry per file
                all_patterns = ", ".join(pattern_data.keys())
                all_matched_lines = "; ".join("; ".join(data["Matched Lines"]) for data in pattern_data.values())
                all_line_numbers = ", ".join(", ".join(map(str, data["Line Numbers"])) for data in pattern_data.values())
                aggregated_matches.append({
                    "File": program_name,
                    "Patterns": all_patterns,
                    "Matched Lines": all_matched_lines,
                    "Line Numbers": all_line_numbers,
                    "Compiled By": compiled_by,
                    "Source": source,
                    "DA2": da2,
                    "OPS": ops,
                    "Last Run By": last_run_by
                })

        # Provide progress update every 100 files
        if file_count % 100 == 0:
            print(f"Processed {file_count} out of {total_files} files...")

    return aggregated_matches



def process_and_search_dat_file(dat_file_path, pattern_objects):
    skip_compiler_input = input("Enter the prefix of 'compiled by' names to skip (e.g., 'd' to skip files with 'compiled by' names starting with 'd', leave empty if none(press enter)): ").strip().lower()
    skip_compiler_prefix = skip_compiler_input if skip_compiler_input else None

    skip_source_input = input("Enter the prefix of source names to skip (e.g., '\\\\certification' or 'certification' to skip sources that contain 'certification', leave empty if none (press enter)): ").strip().lower()

    skip_source_prefix = skip_source_input if skip_source_input else None 
    if skip_compiler_prefix:
        print(f"Ignoring files with compiled by names starting with '{skip_compiler_prefix}'.")
    if skip_source_prefix:
        print(f"Ignoring files with source names starting with '{skip_source_prefix}'.")
   
    output_format = input("Choose output format: 1 for each file per row, 2 for each pattern per row: ").strip()
    detailed_output = output_format == "2"
    pattern_string = "\n".join(f"-{obj['pattern']}" for obj in pattern_objects)
    
    print(f"Patterns used for searching:\n{pattern_string}\n") 
    print(f"Reading and processing {dat_file_path} , this may take a minute...")
    named_blocks = split_dat_file_to_blocks(dat_file_path, skip_compiler_prefix, skip_source_prefix)
    if named_blocks:
        print(f"Searching through {len(named_blocks)} 'virtual files' for patterns...")
        # Let the user decide the output format
        matches = search_blocks_aggregated(named_blocks, pattern_objects, detailed_output)
        if matches:
            print(f"Found matches in {len(matches)} 'virtual files'.")
            for match in matches:
                match['Compiled By'] = clean_text(match['Compiled By'])
                match['Source'] = clean_text(match['Source'])
                match['Matched Lines'] = clean_text(match['Matched Lines'])
            df_matches = pd.DataFrame(matches)
            output_type = input("Enter the output file type (csv/xlsx/html): ").strip().lower()
            save_matches(df_matches, output_type, [dat_file_path], [obj['pattern'] for obj in pattern_objects])
        else:
            print("No matches found within the 'virtual files'.")
    else:
        print("No 'virtual files' to search.")


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1) Search Directory Configuration")
        print("2) Pattern Management")
        print("3) Exclusion Settings")
        print("4) View Current Configuration")
        print("5) Start Search")
        print("6) search outdump file")
        print("7) Exit")
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
            if not basic_patterns and not csv_patterns and not custom_patterns:
                print("No search patterns specified. Please add patterns before starting the search.")
                continue
            outdump_file_path = select_outdump_file()
            if outdump_file_path:
                print(f"Outdump file selected: {outdump_file_path}\n")
                user_confirmation = get_user_confirmation("Do you want to proceed with the selected outdump file?")
                if user_confirmation == "yes":
                    # Concatenate all patterns into a single list
                    all_patterns = basic_patterns + csv_patterns + custom_patterns
                    # Pass this combined list to the processing function
                    process_and_search_dat_file(outdump_file_path, all_patterns)

        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")






if __name__ == "__main__":
    main_menu()
    
