import os
import re
import pandas as pd
import concurrent.futures

# Combined Patterns (Both Basic and Advanced)
def compile_all_patterns(basic_patterns, advanced_patterns):
    compiled_basic = [re.compile(pattern, re.IGNORECASE) for pattern in basic_patterns]
    return compiled_basic + advanced_patterns

# Helper Function to Search Files


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




def save_matches(df, output_type, specific_dirs, basic_patterns):
    """Save the DataFrame of matches to a file in the specified format."""

    # Extract the basename of each directory and join them with "_"
    dir_names = [os.path.basename(os.path.normpath(dir_path)) for dir_path in specific_dirs]
    dir_names_str = "_".join(dir_names)
    
    # Join the patterns with "_"
    patterns_str = "_".join(basic_patterns).replace('*', 'all')  # Replace '*' to avoid invalid filename
    
    # Construct the filename prefix
    filename_prefix = f"{dir_names_str}_{patterns_str}_matches" if basic_patterns else f"{dir_names_str}_matches"
    
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






def main_menu():
##################################################################################################################
    # default settings 
    advanced_patterns = [] # set to empty array. if you don't have any advanced patterns
    #ADD ANY ADVANCED REGEX PATTERNS HERE^^^^^ 
#######################################################################################################################
    #example usage of advanced patterns:

    # advanced_patterns = [  # Advanced patterns as pre-compiled regex objects
    #     re.compile(r"(?<![0-9])(\bcode_set\s*=\s*71\b|,?\s*71\s*,?)(?![0-9])"),
    #     re.compile(r"CKI\.CODEVALUE!(3958|3957|3959|24695|8320|17613|8318|4203425924|9547|1302227|2160170007)\b")
    # ]
######################################################################################################################

######################################################################################################################
    specific_dirs = [r"N:\cclprod"]  # Default specific directories to search
########################################################################################################################
    while True:
        print(f"You are set to search inside of directories {specific_dirs}. Would you like to change your search directories? (y/n)")
        change_dirs = input().strip().lower()
        if change_dirs == 'y':
            new_dirs_input = input("Enter new directories separated by ',' (e.g., 'C:\\Users\\,D:\\Data'): ").strip()
            new_dirs = [dir_path.strip() for dir_path in new_dirs_input.split(',') if dir_path.strip()]
            valid_dirs, invalid_dirs = [], []
            for dir_path in new_dirs:
                if os.path.isdir(dir_path):
                    valid_dirs.append(dir_path)
                else:
                    invalid_dirs.append(dir_path)
            
            if valid_dirs:
                print("The following directories are set for search:")
                for valid_dir in valid_dirs:
                    print(f" - {valid_dir}")
                specific_dirs = valid_dirs  # Update specific_dirs with valid directories only
                
            if invalid_dirs:
                print("The following directories are not valid and will be ignored:")
                for invalid_dir in invalid_dirs:
                    print(f" - {invalid_dir}")


        basic_patterns_input = input("Enter basic patterns to search for separated by ',' (e.g., 'birth_dt_tm,dob,mrn' or 'none' if you don't have any): ").strip()
        if basic_patterns_input.lower() == "none":
            basic_patterns = []  # If you don't have any basic patterns
            print("No basic patterns entered. Using only advanced patterns if specified.")
        else:
            basic_patterns = [pattern.strip() for pattern in basic_patterns_input.split(',')]
        
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
        
        ignore_keywords_input = input("Enter file path keywords to ignore separated by ',' (e.g., 'backup,bkp' or 'none' if you don't have any): ").strip()
        ignore_paths_keywords = [] if ignore_keywords_input.lower() == "none" else [keyword.strip() for keyword in ignore_keywords_input.split(',')]
        
        print("\nSelect search option:")
        print("1) Search specified directories recursively (Top-level and subdirectories)")
        print("2) Search top level files only (No subdirectories)")
        print("3) Exit")
        
        choice = input("Enter your choice: ")
        
       
        
        if choice == "1":
            exclude_input = input("Are there any directories/subdirectories that you want to exclude? (y/n): ").strip().lower()
            if exclude_input == 'y':
                exclude_dirs_input = input("Enter the directories to exclude separated by ',' (e.g., 'C:\\Users\\temp,D:\\Data\\backup'): ").strip()
                exclude_dirs = [dir_path.strip() for dir_path in exclude_dirs_input.split(',') if dir_path.strip()]
                # Optionally, validate the excluded directories
                exclude_dirs = validate_exclude_dirs(exclude_dirs)
            
            all_matches = []
            for specific_dir in specific_dirs:
                specific_dir_abs = os.path.abspath(specific_dir)
                print(f"Starting search in {specific_dir_abs} including subdirectories...")
                matches = search_files(specific_dir_abs, all_patterns, file_extensions, include_subdirs=True, exclude_dirs=exclude_dirs, ignore_paths_keywords=ignore_paths_keywords)
                
                if matches:
                    all_matches.extend(matches)
                    print(f"Matches found in {specific_dir}: {len(matches)}")
                else:
                    print("No matches found.")
            
            if all_matches:
                df = pd.DataFrame(all_matches)
                save_matches(df, output_type, specific_dirs, basic_patterns)
        
        elif choice == "2":
            # specific_dirs = [r"N:\cclprod", r"N:\InterfaceScripts"]  # Example specific directories
            # specific_dirs = validate_specific_dirs(specific_dirs, os.getcwd())
            
            all_matches = []
            for specific_dir in specific_dirs:
                specific_dir_abs = os.path.abspath(specific_dir)
                print(f"Starting search in {specific_dir_abs} without including subdirectories. Top level files only...")
                matches = search_files(specific_dir_abs, all_patterns, file_extensions, include_subdirs=False, exclude_dirs=exclude_dirs, ignore_paths_keywords=ignore_paths_keywords)
                
                if matches:
                    all_matches.extend(matches)
                    print(f"Matches found in {specific_dir}: {len(matches)}")
                else:
                    print("No matches found.")
            
            if all_matches:
                df = pd.DataFrame(all_matches)
                save_matches(df, output_type, specific_dirs, basic_patterns)
        
        elif choice == "3":
            print("Exiting...")
            break
       


if __name__ == "__main__":
    main_menu()
