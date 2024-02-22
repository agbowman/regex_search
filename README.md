# regex_search

regex_search is a multithreading Python tool designed to search for regular expression patterns within files located in a specified directory and its subdirectories. This tool is useful for analyzing and filtering large datasets or collections of files, allowing users to quickly identify and extract valuable information based on complex search criteria. The results are comprehensively documented, detailing the file location where the pattern was found, the specific pattern matched, the line numbers where matches occurred, and more. Furthermore, regex_search offers flexibility in output formats, supporting both .csv and .xlsx file types for easy viewing and analysis. 


# advanced patterns (optional):
 
### advanced_patterns[] array might be the only thing you would ever touch in the python code if you wanted to do so.
### can be whichever regex patters you specify in the advanced_patterns array. You can also generate the advanced_patterns from a csv file using the csv_to_regex.py program. examples shown below

# Basic patterns (also optional, but recommended):
### are case insensitive by default. if you want to use case sensitive words at the command line just wrap "case()" around your word. example:

```
 Enter basic patterns to search for separated by ',' (e.g., 'birth_dt_tm,dob,mrn' or 'none' if you don't have any):

 case(DOB),case(MRN),case(ExAmPlE),example2,example3
```

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
## More about adding your own regex patterns to search for, "advanced_patterns" (optional):
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

### If you want to ignore case with advanced patterns, or add variable spacing between items such as an equal sign:
```bash
advanced_patterns = [
re.compile(r"\.event_cd\s*=\s*ALLERGIES", re.IGNORECASE)
]
```

# If you want to generate the advanced regex patterns by reading in a csv you can do that too!

Just run csv_to_regex.py with python csv_to_regex.py 
```
1) Enter the path to your CSV file: Ad Hoc Query.csv    <- (this would just be a relative path, you can just place the csv file in where the python script is and use the name of the csv)
2) Available columns in the CSV file:
     1. CODE_VALUE
     2. DISPLAY
     3. CDF_MEANING
     4. DESCRIPTION
     5. DISPLAY_KEY
     6. CKI
3) Which columns do you want to use? (Enter as a comma-separated list): CODE_VALUE,CKI
4) Do you want to strip trailing .0 from float values? (yes/no): yes
5)

CODE_VALUE:
     ...
     20. 64092637
     21. 562709540
     22. 564177390
     23. 64092638
     24. 564177370
     ...

    Which rows would you like to use from CODE_VALUE? Please enter like: 1-5,8-10,20 or * for all rows: *


 CKI:
    ...
    138. CKI.CODEVALUE!4102993476
    139. CKI.CODEVALUE!4104641397
    140. CKI.CODEVALUE!2570057763
    141. CKI.CODEVALUE!3250741
    ...

   Which rows would you like to use from CKI? Please enter like: 1-5,8-10,20 or * for all rows: 1-20,60

6) Regex patterns written to regex.txt


7) example output looks like: advanced_patterns = [
    re.compile(r"564177410|584377859|584377864|626467857|2315283|2315284|2315285|463397403|463397408|562709540|463397413|562709545|463397418|562709550|682603055|463397423|513663026|562709555|463397428|682603063|562709560|463397433|513663031|562709565|463397438|682603071|626467906|562709570|463397443|562709575|682603079|562709580|682603087|562709585|682603095|682603103|682603111|682603119|352043123|682603127|352043128|352043132|682603135|566634139|569767579|1692319|566634144|569767584|1692320|1692322|1692321|566634149|566634154|626468011|566634159|576135347|480502963|566634164|576135352|576135357|576135363|576135368|641156817|641156821|626468056|641156825|641156829|411528926|641156833|411528930|641156837|411528934|411528938|411528942|411528946|566129909|411528950|411528954|566129914|411528958|566129919|796809473|411528962|566129924|570795781|411528966|566129929|411528970|566129934|411528975|244978960|244978964|598116629|626468121|598116634|598116639|598116644|618753316|598116649|598116654|569413958|569413963|704757583|569413968|569413973|618752878|572115826|626468214|572115831|572115836|618752895|572115841|572115846|572115851|572115856|626468243|572115861|626468248|572115866|626468253|180238754|180238755|180238756|180238757|180238758|180238759|180238760|180238761|180238762|180238764|180238765|626468270|567369659|626468287|567369664|626467791|564177360|626467796|564177365|950702551|564177370|64092637|64092638|64092639|564177375|564177380|746503655|564177385|564177390|746503663|1103469555|564177395|1103469559|564177400|564177405|584377854"),
    re.compile(r"CKI\.CODEVALUE!2160697114|CKI\.CODEVALUE!4114156349|CKI\.CODEVALUE!4113926079|CKI\.CODEVALUE!4110884854|CKI\.CODEVALUE!2160697115|CKI\.CODEVALUE!4114156360|CKI\.CODEVALUE!4105322163|CKI\.CODEVALUE!4105322164|CKI\.CODEVALUE!4115557756|CKI\.CODEVALUE!2160697116|CKI\.CODEVALUE!4112640271|CKI\.CODEVALUE!4114156348|CKI\.CODEVALUE!4113875394|CKI\.CODEVALUE!4115352728|CKI\.CODEVALUE!4117294672|CKI\.CODEVALUE!2160697113|CKI\.CODEVALUE!2570188280|CKI\.CODEVALUE!4044109|CKI\.CODEVALUE!4112640272|CKI\.CODEVALUE!4102433467|CKI\.CODEVALUE!2570192024"),
]

8) just paste that into the regex_search.py advanced_patterns array!
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
