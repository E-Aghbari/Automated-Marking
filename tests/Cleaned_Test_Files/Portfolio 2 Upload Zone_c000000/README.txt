RUNNING INSTRUCTIONS

	To understand what every parameter means, please check the comment documentation in Task_1_5. Here are some examples of what parameters to pass to each file to run it.
	
	Example of params to pass to Task_1_5:
	-k 2 -m computeMeasure1 -s True -u -train "..\training_data.csv" -test "..\testing_data.csv"
	
	WARNING: these are only the PARAMETERS. If you copy only them into the command-line, things won't work. If you want to run things, try:
	
	python Task_1_5.py -k 2 -m computeMeasure1 -s True -u -train "..\training_data.csv" -test "..\testing_data.csv"
	
	Example of params to pass to Task_2:
	-classified "..\classified_data.csv"
	
	Example of params to pass to Task 3:
	-k 2 -f 10 -m Task_1_5.computeMeasure1 -s True -train "..\training_data.csv"

ERRORS

	Please pay attention to the errors you are getting. Very often the trouble with running the program comes from the fact that the Images folder is not where it should be. The paths in the csv file are relative, if it is easier for you, it's fine to change them to absolute. Just please don't do any funny path modifications inside the code, as that will cause problems for me when running and marking your program.

	Please also make sure you use the correct version of Python. If the template does not compile, it means you are using wrong Python version. Check the assessment proforma.

PREPARING THE CODE FOR SUBMISSION

	Do not forget to make your code ready to be marked on a different machine - at the very least, please provide a requirements.txt file. Please also put the abbreviations of the names of measures you have used in Tasks 1 and 5 in the measures.txt file (one measure per line).

	You should submit a .zip file that contains the template files (Task files), measures.txt, requirements.txt, and any other Python files you have used. If you have used different Python version than stated in the assessment proforma, include an additional .txt file saying which 	version was used. 

	DO NOT INCLUDE ANY .CSV FILES, IMAGES, OR DUMMY FILE.