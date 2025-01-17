# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import Restarted
import smtplib
import os

# Runs if bot does not understand user's input
class ActionDefaultAskAffirmation(Action):

    def name(self):
        return "action_default_ask_affirmation"

    async def run(self, dispatcher, tracker, domain):
        print("in ActionDefaultAskAffirmation!!!")
	
	# Last thing user typed
        lastOutput = tracker.latest_message['text']
        # Gets the user's last intent by extracting it from tracker dict
        lastUserIntentDictionary = tracker.latest_message['intent']
        lastUserIntent = list(lastUserIntentDictionary.values())[0]
        
	# Gets last output of bot (last question that bot asked user)
        for event in tracker.events:
            if (event.get("event") == "bot"):
                lastBotMessage = event.get("text")
        print(lastBotMessage)

        # Fallback for if the bot doesn't understand the receipient's name for the email or the email address
        if "Please type the name of the person you want to email." in lastBotMessage:
            dispatcher.utter_message('The person you want to email is ' + lastOutput)
            SlotSet("recipient", lastOutput)
        elif "Please enter the email address of the person you want to email." in lastBotMessage:
            dispatcher.utter_message('The email address is ' + lastOutput)
            SlotSet("email", lastOutput)
        # else
        else:
            dispatcher.utter_message(text="すみません、わかりません。 Sorry, I don't quite understand (,,>﹏<,,).", image = "https://media.tenor.com/-caxkmc867EAAAAC/mochi-cat.gif")

        print(lastUserIntent)
        
        return [FollowupAction("after_handle_did_not_understand_answer")]	

# Followup action from ActionDefaultAskAffirmation that
# generates the bot's next response        
class AfterHandleDidNotUnderstandAnswer(Action):

    def name(self) -> Text:
        return "after_handle_did_not_understand_answer"

    def run(self, dispatcher, tracker, domain):
        print("in AfterHandleDidNotUnderstandAnswer")
        
        # dispatcher.utter_message('We bonked at the beginning, so do not have any valid slots I can use to make bot look smart.  Ohe well.  Let us just resume the story with student asking bot a question.')

        # Gets last output of bot (based on dispatcher.utter_message from ActionDefaultAskAffirmation)
        for event in tracker.events:
            if (event.get("event") == "bot"):
                lastBotMessage = event.get("text")
        print(lastBotMessage)

        # Gets the user's last intent by extracting it from tracker dict
        lastUserIntentDictionary = tracker.latest_message['intent']
        lastUserIntent = list(lastUserIntentDictionary.values())[0]

	# Asks user for to ask bot a question
        # The lastBotMessage is coming from the ActionDefaultAskAffirmation
        # and these if/elif statements are checking what the bot last said
        # and using substrings of the last message to identify what the bot says next
        
        # Fallback for if the bot doesn't understand the receipient's name for the email or the email address
        if "The person you want to email is" in lastBotMessage:
            dispatcher.utter_message('Great. Now we need their email.')
        elif "The email address is" in lastBotMessage:
            dispatcher.utter_message('Thank you for the information.')
        # else
        else:
            dispatcher.utter_message("I am a simple bot. Please rephrase.")
        
        print(lastUserIntent)
        return [Restarted()]

#Create action to log conversation, each time called will capture last bot output
class LogConversationBot(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "log_conversation_bot"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
	
	# Get last conversation for bot
        for event in tracker.events:
            if (event.get("event") == "bot"):
                lastBotMessage = "Bot message: " + event.get("text")

        print("Last bot message: " + lastBotMessage)

        # Creates/Open function to open the file "conversation_[senderID].txt" 
        # with the senderID being unique to each user
        uniqueFile = "conversation" + tracker.sender_id + ".txt"
        conversation_txt = open(uniqueFile,"a")


        conversation_log_bot = "\n" + lastBotMessage 
        
        # write latest conversations to txt file
        conversation_txt.write(conversation_log_bot)

        conversation_txt.close()
        return [SlotSet("conversation_log", conversation_log_bot)]

#Create action to log conversation, each time called will capture last user response
class LogConversationUser(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "log_conversation_user"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
	
        # print last user message
        print("Last user message: " + tracker.latest_message.get("text"))


        # Creates/Open function to open the file "conversation_[senderID].txt" 
        # with the senderID being unique to each user
        uniqueFile = "conversation" + tracker.sender_id + ".txt"
        conversation_txt = open(uniqueFile,"a")

        # Get last conversation from user
        conversation_log_user = "\nUser message: " + tracker.latest_message.get("text")
        
        # write latest conversations to txt file
        conversation_txt.write(conversation_log_user)

        conversation_txt.close()
        return [SlotSet("conversation_log", conversation_log_user)]


# Creating new class to send emails.
class ActionEmail(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "action_email"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Tracker message log
        # message_log = tracker.latest_message['text']
        # conversation_log = str(tracker.get_slot("conversation_log"))        

        # Getting the data stored in the
        # slots and storing them in variables.
        # these are for the person RECIEVING the mail
        
        recipient = tracker.get_slot("recipient")
        email_id = tracker.get_slot("email")
        name = tracker.get_slot("name")
        # recipient = "Leah"
        # email_id = "goldberl@dickinson.edu"
          
        # Code to send email
        # Creating connection using smtplib module
        s = smtplib.SMTP('localhost')
          
        # Making connection secured
        s.starttls() 
         
        # Authentication
        # s.login("goldberl@dickinson.edu")

        
        # Open the file "conversation_[senderID].txt" 
        # with the senderID being unique to each user
        uniqueFile = "conversation" + tracker.sender_id + ".txt"
        conversation_txt = open(uniqueFile,"r")

        conversation_log = ''
        # Using for loop
        for line in conversation_txt:
            conversation_log = conversation_log + line +'\n'
    
        # Closing files
        conversation_txt.close()
          
        # Message to be sent
        # Ideally we would like to say who this conversation is from which can be extracted 
        # from the NAME slot if the bot did not delete all the slots
        # But the bot sometimes deletes all the slots
        # One way we can fix this is storing the user's name in a text file and reading it
        # Additionally, to ensure the bot understands the email address, we can put that in a 
        # txt file as well and read it
        message = "Subject: Japanese Chatbot Message Log\n\n Hello {}, \n\nThis is a message from the RASA Japanese chatbot!\n\nRegards,\nThe Dickinson College RASA Japanese Chatbot".format(recipient) + "\n\nPlease find the message log below for the conversation: \n" + conversation_log
        
	# The email address below is the person who is SENDING the mail  
        # Sending the mail
        s.sendmail("academictechnology@dickinson.edu",email_id, message.encode("utf8"))
          
        # Closing the connection
        s.quit()

        # Delete contents of conversation_[senderID].txt
        uniqueFile = "conversation" + tracker.sender_id + ".txt"
        if os.path.exists(uniqueFile):
            os.remove(uniqueFile)
          
        # Confirmation message
        dispatcher.utter_message(text="Email has been sent.")
        return []
       

# Creating new class to send emails.
class DeleteConversationTxt(Action):
  
    def name(self) -> Text:
         # Name of the action
        return "action_delete_conversation_txt"
  
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Delete contents of conversation.txt
        uniqueFile = "conversation" + tracker.sender_id + ".txt"
        if os.path.exists(uniqueFile):
            os.remove(uniqueFile)
        return []

# class ActionTest(Action):
#
#     def name(self) -> Text:
#         return "action_test"
#
#     def run(self, dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         print("HELLO this is a test action")
#         return[]
