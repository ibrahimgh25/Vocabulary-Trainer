# Vocabulary Trainer
 In the process of learning a new language, I couldn't find a free tool for testing what words I memerized. I also looked through multiple open-source python projects on github (example: ), although they were great, they didn't do what I wanted. So I built this code. 
 ## Offered Features
 The tool has the following feature:
 - A console interface for reciting vocabulary from an excel database in two ways (language you know to language you're learning and vice-versa).
 - A question sampling method that focuses on questions you're answering wrong.
 - A way to store scores over multiple sessions (for now they're stored as rows in the excel sheet)
 
 ## Possible Editions
 - Adding settings to the GUI that allow for custimizing several parameters.
 - Several exercises for nouns (female-to-male, singular-to-plural)
 - A custimaizable sampling strategy for choosing the questions.
 - Verb cojugations (this have some challenges, mainly seeing a good way for collecting and storing different verbs with their conjugation)
 - A more flexible way for matching the answers.
 - A way to update some entries while the program is running (for exmaple, when you're asked about a translation for a phrase, you notice a problem with the answer in the excel sheet and need to quickly solve it, this makes more sense when a GUI is implemented)
 
 ## Collaboration Plea
 For me, the tool "as-is" is still a vrey good way to recite and memorize vocabulary. That said, the more features added to the tool the better. So if anybody wants to help implement any of the open features it would be appreciated. Also, in case you used the tool with a cutom database consider sharing it so people could benefit from it.
 
 ## Acknowledgements
The tool was inspired by [LearnDW](https://learngerman.dw.com/en/overview) which is a website for teaching german language. The database I collected is from there. They also have a tool to help you memorize vocabulary (it's really good but still neither tracks your scores nor focuses on stuff you don't know).

## Documentation tasks
- Add how to install and use the tool.
- Add documentation for tool structure.

## Bugs
- Fix a bug where an excel sheet changes it's relative order when the database is updated (easy to fix, I will get to it later)
