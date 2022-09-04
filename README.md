# Vocabulary Trainer
 In the process of learning a new language, I couldn't find a free tool for testing what words I memerized. I also looked through multiple open-source python projects on github (example: ), although they were great, they didn't do what I wanted. So I built this code. 
 ## Offered Features
 The tool has the following feature:
 - A graphical interface for reciting vocabulary from an excel database in two ways (language you know to language you're learning and vice-versa).
 - A question sampling method that focuses on questions you're answering wrong.
 - A way to store scores over multiple sessions (scores for an exercise are stored as json files with ID linking to the database)
 - The tool is more custimized towards English as the "language you know", but could work with other langauges.
 - The tool detects the languages (language you know and language you want to learn) from the database.
 - A way to edit, delete, or add alternative translations when working with the app.
 - A way to visualize the score for a particular exercise.
 - You can do exercises on small samples of a the database to memorize words one batch at a time.
 
 ## Installation and Usage
 Installing and using the app is easy (for someone comfortable with python at least):
 - Clone the repository on your device.
 - [Optional] Create a conda environment with python 3.10:
```
   conda create --name vocab_tool python=3.10
   conda activate vocab_tool
 ```
 - Install the python packages necessary:
```
  pip install -r requirments.txt
``` 
 To use the tool, just activate your environment (if on conda), and run the script in main.py
```
  python main.py
```
 By default, the tool will select the database in "resources/german_database.xlsx" and the excel sheet "A1". You can add word by updating the selected database, or change the selected excel path to a custom file (make sure your file have the same columns as the one in "german_database.xlsx").
 ## Possible Additions
 - Adding settings to the GUI that allow for custimizing several parameters.
 - Several exercises for nouns (female-to-male, singular-to-plural)
 - A custimaizable sampling strategy for choosing the questions.
 - Verb cojugations (this have some challenges, mainly seeing a good way for collecting and storing different verbs with their conjugation)
 - A better design for the app, instead of the bland design used as of now.
 
 ## Collaboration Plea
 For me, the tool "as-is" is still a vrey good way to recite and memorize vocabulary. That said, the more features added to the tool the better. So if anybody wants to help implement any of the open features it would be appreciated. Also, in case you used the tool with a cutom database consider sharing it so people could benefit from it.
 
 ## Acknowledgements
The tool was inspired by [LearnDW](https://learngerman.dw.com/en/overview) which is a website for teaching german language. The database I collected is from there. They also have a tool to help you memorize vocabulary (it's really good but still neither tracks your scores nor focuses on stuff you don't know).
Also, I haven't done a GUI interface before, so I got started by learning from the code in ["codecravings/Speed-Typing-Test-Python"](https://github.com/codecravings/Speed-Typing-Test-Python).

## Documentation tasks
- Add documentation for the tool structure.
- Add some screenshots for the tool
- Add instructions for building the database
