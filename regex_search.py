import os
import re
import pandas as pd


# Combined Patterns (Both Basic and Advanced)
def compile_all_patterns(basic_patterns, advanced_patterns):
    compiled_basic = [re.compile(pattern, re.IGNORECASE) for pattern in basic_patterns]
    return compiled_basic + advanced_patterns

# Helper Function to Search Files
def search_files(directory, patterns, file_extensions, include_subdirs=True, exclude_dirs=None):
    matches_dict = {}
    compiled_patterns = patterns
    directory = os.path.abspath(directory)  # Convert to absolute path for safety

    if exclude_dirs:
        exclude_dirs = [os.path.abspath(dir_path) for dir_path in exclude_dirs]

    for root, dirs, files in os.walk(directory, topdown=True):
        if not include_subdirs:
            # If we're not including subdirectories, clear the dirs list
            # This prevents os.walk from going into any subdirectories
            dirs.clear()

        if exclude_dirs:
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]

        for file in files:
            if '*' in file_extensions or any(file.endswith('.' + ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for pattern in compiled_patterns:
                            for i, line in enumerate(lines, 1):
                                if pattern.search(line):
                                    if file_path not in matches_dict:
                                        matches_dict[file_path] = {
                                            "file location": file_path,
                                            "patterns": [],
                                            "matched lines": [],
                                            "line numbers": []
                                        }
                                    pattern_str = pattern.pattern if hasattr(pattern, 'pattern') else str(pattern)
                                    if pattern_str not in matches_dict[file_path]["patterns"]:
                                        matches_dict[file_path]["patterns"].append(pattern_str)
                                    matches_dict[file_path]["matched lines"].append(line.strip())
                                    matches_dict[file_path]["line numbers"].append(i)
                except UnicodeDecodeError:
                    print(f"Skipping file due to encoding issues: {file_path}")

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


def save_matches(df, output_type, filename_prefix="matches"):
    """Save the DataFrame of matches to a file in the specified format."""
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



######################################################################################################################
#example usage of patterns:

    # basic_patterns = []  # if you don't have any basic patterns
    # advanced_patterns = []  # if you don't have any advanced patterns
    # basic_patterns = ['birth_dt_tm', 'dob']  # Basic patterns. Will find all occurrences of 'birth_dt_tm' and 'dob'

    # advanced_patterns = [  # Advanced patterns as pre-compiled regex objects
    #     re.compile(r"(?<![0-9])(\bcode_set\s*=\s*71\b|,?\s*71\s*,?)(?![0-9])"),
    #     re.compile(r"CKI\.CODEVALUE!(3958|3957|3959|24695|8320|17613|8318|4203425924|9547|1302227|2160170007)\b")
    # ]
######################################################################################################################

# Main Menu
def main_menu():
  ######################################################################################################################
    advanced_patterns = [] # set to empty array. if you don't have any advanced patterns
    #ADD ANY ADVANCED REGEX PATTERNS HERE^^^^^ 
  ######################################################################################################################
    while True:
        basic_patterns = input("Enter basic patterns separated by ',' (e.g., 'birth_dt_tm,dob,mrn' or 'none' if you don't have any): ").strip()
        if basic_patterns.lower() == "none":                                                                                                                                                          
            basic_patterns = []  # if you don't have any basic patterns
            print("No basic patterns entered. Using only advanced patterns if specified.")
        else:
            basic_patterns = basic_patterns.split(',')
            basic_patterns = [pattern.strip() for pattern in basic_patterns]
        all_patterns = compile_all_patterns(basic_patterns, advanced_patterns)
        file_extensions_input = input("Enter file extensions to search for separated by ',' (e.g., 'txt,prg,bak,dpb' or '*' for any): ").strip()
        file_extensions = [ext.strip() for ext in file_extensions_input.split(',')] if file_extensions_input != '*' else ['*']

        while not file_extensions_input:
            print("File extension cannot be empty.")
            file_extensions_input = input("Enter file extensions to search for separated by ',' (e.g., 'txt,prg,bak,dpb' or '*' for any): ").strip()
            file_extensions = [ext.strip() for ext in file_extensions_input.split(',')] if file_extensions_input != '*' else ['*']
        output_type = input("Enter the output file type (e.g., 'csv', 'xlsx'): ").strip().lower()
        while output_type not in ['csv', 'xlsx', 'html']:
            print("Invalid output type. Please choose a valid output type. (csv, xlsx, html)")
            output_type = input("Enter the output file type (e.g., 'csv', 'xlsx'): ").strip().lower()
        print("\nSelect search option:")
        print("1) Search specified directories recursively (Top-level and subdirectories)")
        print("2) Search top level files only (No subdirectories)")
        print("3) Exit")

        choice = input("Enter your choice: ")
        # exclude_dirs = [r"N:\InterfaceScripts\Build\backup"]  # Example exclude_dirs
        exclude_dirs = []  
        if choice in ["1", "2"]:
            # Validate exclude_dirs before proceeding with the search.
            exclude_dirs = validate_exclude_dirs(exclude_dirs)

        if choice == "1":
            specific_dirs = [r"N:\cclprod", r"N:\InterfaceScripts"]  # Use raw strings for each path
            # specific_dirs = [r"N:\InterfaceScripts\Build"]
            specific_dirs = validate_specific_dirs(specific_dirs, os.getcwd())  # Validate directories

            all_matches = []  # Collect matches from all specific directories
            for specific_dir in specific_dirs:
                specific_dir_abs = os.path.abspath(specific_dir)
                print(f"Starting search in {specific_dir_abs} including subdirectories...")
                matches = search_files(specific_dir_abs, all_patterns,file_extensions,  include_subdirs=True, exclude_dirs=exclude_dirs)
                
                if matches:
                    all_matches.extend(matches)
                    print(f"Matches found in {specific_dir}: {len(matches)}")
                else:
                    print(f"No matches found in {specific_dir}.")

            if all_matches:
                df = pd.DataFrame(all_matches)
                save_matches(df, output_type, filename_prefix="matches_specific_dirs")



        elif choice == "2":
            specific_dirs = [r"N:\cclprod", r"N:\InterfaceScripts"]  # Use raw strings for each path
            specific_dirs = validate_specific_dirs(specific_dirs, os.getcwd())  # Validate directories

            all_matches = []  # Collect matches from all specific directories
            for specific_dir in specific_dirs:
                specific_dir_abs = os.path.abspath(specific_dir)
                print(f"Starting search in {specific_dir_abs} without including subdirectories...")
                matches = search_files(specific_dir_abs, all_patterns, file_extensions, include_subdirs=False, exclude_dirs=exclude_dirs)
                
                if matches:
                    all_matches.extend(matches)
                    print(f"Matches found in {specific_dir}: {len(matches)}")
                else:
                    print(f"No matches found in {specific_dir}.")

            if all_matches:
                df = pd.DataFrame(all_matches)
                save_matches(df, output_type, filename_prefix="matches_top_level_files_in_specific_directories")


        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice, please select a valid option.")

if __name__ == "__main__":
    main_menu()