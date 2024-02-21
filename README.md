# regex_search

regex_search is a multithreading Python tool designed to search for regular expression patterns within files located in a specified directory and its subdirectories. This tool is useful for analyzing and filtering large datasets or collections of files, allowing users to quickly identify and extract valuable information based on complex search criteria. The results are comprehensively documented, detailing the file location where the pattern was found, the specific pattern matched, the line numbers where matches occurred, and more. Furthermore, regex_search offers flexibility in output formats, supporting both .csv and .xlsx file types for easy viewing and analysis. 

# Basic patterns(optional):
### are case insensitive
# advanced patterns(optional):
 
### advanced_patterns[] array might be the only thing you would ever touch in the python code if you wanted to do so.
### can be whichever regex patters you specify in the advanced_patterns array. examples shown below

# User input
### When you run the program with python regex_search.py in your project folder (wherever you stored the regex_search.py file), the command line interface will walk you through all of the steps for filtering your search with brief explinations on what you would need to enter. There are checks in place to make sure you entered a valid path. please look out for those messages! 

## example of prompt:
```
1) You are set to search inside of directories ['N:\\cclprod']. Would you like to change your search directories? (y/n) n
2) Enter basic patterns to search for separated by ',' (e.g., 'birth_dt_tm,dob,mrn' or 'none' if you don't have any): dob,micro
3) Enter file extensions to search for separated by ',' (e.g., 'txt,prg,bak,dpb' or '*' for any): prg,dbp
4) Enter the output file type (e.g., 'csv', 'xlsx'): xlsx
5) Enter file path keywords to ignore separated by ',' (e.g., 'backup,bkp' or 'none' if you don't have any). 
You can also enter the a file to ignore with the full path (e.g., 'C:\Users\temp\file.txt'): backup,bkp
6)
   Select search option:
   1) Search specified directories recursively (Top-level and subdirectories)
   2) Search top level files only (No subdirectories)
   3) Exit
   Enter your choice: 1

# I will go with 1 in this case

7) Are there any directories/subdirectories that you want to exclude? (y/n): y
Enter the directories to exclude separated by ',' (e.g., 'C:\Users\temp,D:\Data\backup'): N:\cclprod\bhs_rpt_item_master_cdm

   The valid excluded dirs are:
    - N:\cclprod\bhs_rpt_item_master_cdm
   Starting search in N:\cclprod including subdirectories...

```
## Another example using different directories to search in and using advanced patterns instead of basic patterns (you are allowed to use both in same search. I chose not to for this example):
```
1) You are set to search inside of directories ['N:\\cclprod']. Would you like to change your search directories? (y/n)
y

2) Enter new directories separated by ',' (e.g., 'C:\Users\,D:\Data'): N:\cclprod, N:\InterfaceScripts
The following directories are set for search:
 - N:\cclprod
 - N:\InterfaceScripts

3) Enter basic patterns to search for separated by ',' (e.g., 'birth_dt_tm,dob,mrn' or 'none' if you don't have any): none
No basic patterns entered. Using only advanced patterns specified in advanced_patterns[] array.

4) Enter file extensions to search for separated by ',' (e.g., 'txt,prg,bak,dpb' or '*' for any): *
...
```
# Goal
### input:
#### choice #1
![image](https://github.com/agbowman/regex_search/assets/148987179/fb73cff1-0d08-44c8-8608-4fd630b5ab37)
#### choice #2
![image](https://github.com/agbowman/regex_search/assets/148987179/9d7bae3d-4d01-4966-b48a-4e8d9c02b183)


### output:
#### from choice #2
![image](https://github.com/agbowman/regex_search/assets/148987179/eba9b854-9aaa-4768-b0dd-a3e8bd73af63)


## Features

Multiple File Type Support: Users can specify one or multiple file extensions to narrow down the search, enhancing efficiency and focus.
Advanced Regex Patterns: Beyond basic text matching, regex_search allows for the inclusion of advanced regex patterns. This capability enables users to construct and apply complex search criteria that can match many textual patterns within files.
Exclusion of Directories: To increase search specificity and reduce processing time, users have the option to exclude certain directories from the search. This feature is particularly useful for skipping over directories that are known to be irrelevant or that contain sensitive information not intended for search.
Output Customization: regex_search supports output in multiple file formats. Users can choose between .csv and .xlsx formats for the output file for easy readability.
Fast searching with multithreading. Searches files in parallel with searching inside of a single file for regex patterns.
## Things to know/modify:
### in "main_menu" function, if you want to add more advanced regex patterns (optional - beyond basic word/phrase parsing "basic_patterns") you can add them to the advanced_patterns = [] array. i.e: 

```bash
#change this:
     advanced_patterns = []
#to something like this with your given regex
     advanced_patterns = [  # Advanced patterns as pre-compiled regex objects
         re.compile(r"(?<![0-9])(\bcode_set\s*=\s*71\b|,?\s*71\s*,?)(?![0-9])"),
         re.compile(r"CKI\.CODEVALUE!(3958|3957|3959|24695|8320|17613|8318|4203425924|9547|1302227|2160170007)\b")
     ]
```
### If you want more verbose patterns i.e. matching a bunch of different ids, etc.
you can put the pattern in the advanced patterns array as shown before with the verbose flag so its treated as one line/expression. ex: 
```bash
    advanced_patterns = [
re.compile(r"""
           (1232|963109|966624|966630|4963309|35886935|25626074|4963311|966636|1446219|12991994|
           4963313|966640|966642|966644|966646|50317422|966648|966654|12991998|35886938|966660|4963324|
           4963315|93279627|87088309|966666|35886940|35886942|4963329|25626079|25626077|966676|966680|
           19937089|93279629|966691|19937087|966695|35886952|966702|966706|966714|93297627|966718|4963321|
           966720|12992007|966724|966726|966802)""", re.VERBOSE),

re.compile(r"""
    (21924989|23017435|23017457|23017427|23013425|23017411|23017465|23121513|21852993|22205413|23121517|22421423|
           21884963|22100947|22069269|22345415|22004955|21964997|22349413|22205539|22009073|21965111|21968953|21968951|
           21856969|21852983|22241417|23121521|23121525|21840915|21856905|23121541|22557907|22329437|21973169|22041019|
           22037165|22065237|22153165|22069223|22105273|22269481|22349419|22513417|22473411|22501453|22004965|22105345|
           22005351|22561437|22337435|21965041|23121545|23121549|23037411|23037421|23033411|21856995|23121561|22485779|
           22205445|23121565|21965009|23121569|23121573|21973003|21860911|23121577|21973039|23121581|22165217|23121585|
           
           21964995|22201475|22421419|22509683|22561539|22561431|22325411|22569435|22525423|22345411|22241413|22325431|
           21908953|21928953|21884957|23121427|23121441|23121419|23121415|23117467|23117411|22161643|22088945|22513413|
           22513459|21960981|21836963|23121451|22533445|21837001|22797427|22917411|22885433|22945411|23121411|22281437|
           23121455|23121465|23121469|22989419|23117443|23117499|23121437|23121481|23121473|23121485|23117511|23117431|
           23117455|23117487|23001437|22417411|21973149|22373501|22165359|22373511|22009115|22008989|21952959|22269427|
           22113171|23121601|22181431) """, re.VERBOSE)
    ] 
   
```


## Things I find usefull
### This extension lets you view the output without needing to hop out of vscode.

![image](https://github.com/agbowman/regex_search/assets/148987179/0d619689-5231-457b-bad3-0d4f24e3645a)

### Coming up with regex patterns is hard...
If you want a more advanced regex pattern to put inside of "advanced_patterns" array (as mentioned before), chatgpt is actually really good at coming up with regex patterns. I strongly recommend using it for this type of task.
Try running on small set of example files first to see if the criterea fits what you wanted. You can also validate your regex pattern here: Regex101: https://regex101.com/

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
