## regex_search

regex_search is a Python tool designed to search for regular expression patterns within files located in a specified directory and its subdirectories. This tool is useful for analyzing and filtering large datasets or collections of files, allowing users to quickly identify and extract valuable information based on complex search criteria. The results are comprehensively documented, detailing the file location where the pattern was found, the specific pattern matched, the line numbers where matches occurred, and more. Furthermore, regex_search offers flexibility in output formats, supporting both .csv and .xlsx file types for easy viewing and analysis.

## Goal
### input:

![image](https://github.com/agbowman/regex_search/assets/148987179/9d7bae3d-4d01-4966-b48a-4e8d9c02b183)
### output:

![image](https://github.com/agbowman/regex_search/assets/148987179/eba9b854-9aaa-4768-b0dd-a3e8bd73af63)



## Features

Multiple File Type Support: Users can specify one or multiple file extensions to narrow down the search, enhancing efficiency and focus.
Advanced Regex Patterns: Beyond basic text matching, regex_search allows for the inclusion of advanced regex patterns. This capability enables users to construct and apply complex search criteria that can match many textual patterns within files.
Exclusion of Directories: To increase search specificity and reduce processing time, users have the option to exclude certain directories from the search. This feature is particularly useful for skipping over directories that are known to be irrelevant or that contain sensitive information not intended for search.
Output Customization: regex_search supports output in multiple file formats. Users can choose between .csv and .xlsx formats for the output file for easy readability.

## Things to know/modify:
### in "main_menu" function, if you want to add more advanced regex patterns (beyond basic word/phrase parsing "basic_patterns") you can add them to the advanced_patterns = [] array. i.e: 

```bash
#change this:
     advanced_patterns = []
#to something like this with your given regex
     advanced_patterns = [  # Advanced patterns as pre-compiled regex objects
         re.compile(r"(?<![0-9])(\bcode_set\s*=\s*71\b|,?\s*71\s*,?)(?![0-9])"),
         re.compile(r"CKI\.CODEVALUE!(3958|3957|3959|24695|8320|17613|8318|4203425924|9547|1302227|2160170007)\b")
     ]
```
### If you want to exclude certain directories in search, you can add them to exclude_dirs = []  array. (must use "r" for raw string absolute path) i.e: 
```bash
exclude_dirs = [r"N:\InterfaceScripts\Build\backup", r"N:\InterfaceScripts\Build\temp"]
```
### If you want ot change the directories in which you are searching in just add or remove them here: 
```bash
specific_dirs = [r"N:\cclprod", r"N:\InterfaceScripts"]
```
### Keep in mind that specific_dirs is asigned twice. once in choice1 and once in choice2 to allow for different searches. You most likely want to update in both places.


## Things I find usefull
### This extension lets you view the output without needing to hop out of vscode.

![image](https://github.com/agbowman/regex_search/assets/148987179/0d619689-5231-457b-bad3-0d4f24e3645a)

### Coming up with regex patterns is hard...
If you want a more advanced regex pattern to put inside of "advanced_patterns" array (as mentioned before), chatgpt is actually really good at coming up with regex patterns. I strongly recommend using it for this type of task.
Try running on small set of example files first to see if the criterea fits what you wanted. 

## Getting Started

This guide will help you set up your environment to run the `regex_search` tool.


## Install Python

1. **Download Python**: Go to the [official Python website](https://www.python.org/downloads/) and download the latest version for your operating system. Ensure you download Python 3.x as this script is not compatible with Python 2.x.
2. **Install Python**: Run the installer. Make sure to check the box that says **Add Python to PATH** to ensure your system recognizes Python commands in the terminal.

## Set Up Your Environment in VSCode

1. **Download and Install VSCode**: If you haven't already, download VSCode from the [official site](https://code.visualstudio.com/) and install it.
2. **Open VSCode** and navigate to the Extensions view by clicking on the square icon on the sidebar or pressing `Ctrl+Shift+X`.
3. **Install the Python Extension**: Search for `Python` and install the extension provided by Microsoft. This extension provides enhanced support for Python, including debugging, linting, and code completion.
4. **Open the Project Folder**: Use `File > Open Folder` to open the folder where you've saved the `regex_search` script.

## Install Necessary Packages

`regex_search` requires `pandas` and potentially `openpyxl` (for `.xlsx` file support). Install these packages using the following commands in your terminal or command prompt: (in vscode: terminal -> new terminal)

```bash
pip install pandas
pip install openpyxl
