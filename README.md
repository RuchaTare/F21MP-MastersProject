# F21MP-MastersProject
## Problem Statement: To build a conversational AI to give recipes, ingredients, equipment and any trivia related to the recipes. The agent was able to give recipes based on dietary requirements and allergies. 
## Tech Stack 
 - RASA NLU - For Language understanding
 - Rasa core
 - RASA’s pipeline - DIET Classifier and BERT.
 - Spooncular API was used as a database using its request response model  and payload
 - Prompt Engineering using Open AI’s LLM - text-davinci-001 to enable general-purpose question-answering
 - Python
 - Slack - Ngrok acts as remote server to deploy
 -  Alana proprietary code 
## Data and strategy 
	• Intent classification and Entity Recognition: Leveraged RASA NLU component(Data, rules, policies) giving manual data examples to understand intent and entity
	• Custom actions
		• 3 API calls were made for getting recipes, getting substitutes and getting general information questions
		• Added a fallback to get substitute from text-da-Vinci-001 if API call to spooncular gets null
		• Implemented cache mechanism to store the recipe, and last output for ease of navigating through recipes
	• RASA pipeline - Tried different pipelines with 10% test data and 20% test data
		• SpacyTokenizer versus WhiteSpaceTokenizer
		• CountVectorsFeaturizer vs LanguageModelFeaturizer Vs Both
		• DIET classifier for dual intent and entity recognition vs CRF entity Extractor for entity recognition and DIET classifier for intent classification
	• Prompt Engineering 
		• temperature =0.1 - Keeps the value of the responses precise
		• max tokens = 50 - Word limit
		•  model="text-davinci-001"
		•  prompt=prompt
		•  n=1
		•  top_p=0.1
## Evaluation Metrics
	• Human Evaluation - Took survey from 15 people to try three systems. Website, Alana Conversational agent and Chatgpt
	• Confusion Matrix for MLCM - Leveraged DIET classifiers confusion matrix function for intent classification and entity recognition
	• Accuracy, Precision, Recall, F1 for intent and entity classification - 
	• 94.87 per cent, a precision of 95.92 per cent,
	• a recall of 93.63 per cent and an f1 score of 94.35 per cent.
## Challenges 
	• Make it human like 
	• Experiment with prompt engineering
	• Finding a right data source
	• Needed a lot of data
## Future Work
• As of now, the bot does not understand follow-up questions based on contextual history and it would be interesting to explore ways to achieve it. The bot understands “What oil is most famous in Italy?” and replies accurately with Olive oil. But does not understand the context of the follow-up question “How is it made?” unless explicitly asked, “How is olive oil made?”. This would be really animportant feature to hold longer meaningful conversations with the user.
• Add customized ingredient quantities. As of now, the system can respond with ingredients and their quantities but should be able to upsize or downsize these quantities based on the number of servings given by the user.
• Add nutritional information for the recipe and enable recipe search based on nutritional information. For example, Find me a high-protein pancake recipe.
• A lot of features can be explored in recipe-bot in the future, by using pre-trained LLMs for image detection for identifying food items
