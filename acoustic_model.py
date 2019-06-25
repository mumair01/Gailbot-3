'''
	Script that provides an interface between the user and IBM Watson's STT
	API's custom acoustic model.

	Please see IBM's documentation here:
	https://cloud.ibm.com/apidocs/speech-to-text#create-a-custom-acoustic-model

	Part of the Gailbot-3 development project.

	Developed by:

		Muhammad Umair								
		Tufts University
		Human Interaction Lab at Tufts

	Initial development: 5/20/19	

	Changelog:
		

'''

import requests
import json
import codecs
import os, sys, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pydub import AudioSegment
from pydub.utils import make_chunks
from termcolor import colored
from prettytable import PrettyTable				# Table printing library

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Global variables / invariants.
base_model = "en-US_BroadbandModel"								# Default base model
headers = {'Content-Type' : "application/json"}					# Type of API data
customization_id_length = 36									# Length of custom ID
original = {"base-model": base_model, "acoustic-model" : None}	# Default model values.
output = {"base-model": base_model, "acoustic-model" : None}	# Output for the script.


# User interface function
def interface(username,password):
	main_menu(username,password,{})
	return output

# Main menu function
def main_menu(username,password,closure):
	while True:
		os.system('clear')
		x = PrettyTable()
		x.field_names = [colored('Setting','blue'),colored('Value','blue')]
		x.add_row(["Default model",base_model])
		x.add_row(["Current custom model",str(output["acoustic-model"])])
		print("Welcome to Gailbot's custom " + colored('acoustic model','red')+ " interface!\n")
		print('Use options 1 through 3 to select the model(s) that you would like to use.\n'
			'Press 4 to proceed once all changes are made.\n')
		print(x)
		print("\nPlease choose one of the following options:")
		print("1. Select a custom acoustic model")
		print("2. Delete a custom acoustic model")
		print("3. Create a custom acoustic model")
		print("4. Train an existing custom acoustic model")
		print("5. Advanced options")
		print("6. Reset selections to default values")
		print(colored("7. Proceed / Confirm selection",'green'))
		print(colored("8. Quit",'red'))
		choice = input(" >>  ")
		if choice == '7' : return
		exec_menu(choice,menu_actions,username,password,closure)

# Custom model menu function
def custom_menu(username,password,closure):
	while True:
		os.system('clear')
		print("1. Train custom model using a single audio file")
		print("2. Return to main menu")
		choice = input(" >>  ")
		if choice == '2' : return
		exec_menu(choice,custom_menu_actions,username,password,closure)
		if choice == '1' : return

# Advanced options menu function
def advanced_menu(username,password,closure):
	while True:
		os.system('clear')
		print(colored("Advanced options\n",'red'))
		print("1. List all audio resources for a custom acoustic model")
		print("2. Upgrade base model of an existing custom language model")
		print("3. Reset a custom language model")
		print("4. Return to main menu")
		choice = input(" >>  ")
		if choice == '4': return
		exec_menu(choice,advanced_menu_actions,username,password,closure)

# *** Helper functions ***

# Function that gets custom ID input. (Helper Function)
def get_ID():
	customID = input("Enter customization ID from list\nPress 0 to go back to options\n")
	if customID == '0' : return '0'
	while len(customID) != 36:
		customID = input("\nERROR: Input must be 36 characters\nEnter customization ID from list\n"
			"Press 0 to go back to options\n")
		if customID == '0' : return '0'
	return customID

# Exit program
def exit(username,password,closure):
    sys.exit()

# Selects the custom acoustic model
def select_custom(username,password,closure):
	customID = ''
	get_model_list(username,password)
	customID = get_ID()
	if customID == '0': return
	output["acoustic-model"] = customID
	input('\nSelected!\nPress any key to return to main menu...')

# Function that delets a custom model.	
def delete_custom(username,password,closure):
	get_model_list(username,password)
	customID = get_ID()
	if customID == '0': return
	delete_model(username,password,customID)
	input('Press any key to return to main menu...')


# Function that creates and trians a new custom model.
def create_custom(username,password,closure):
	closure = {}
	try:
		name, description = input("Enter custom model name and description\n"
			"Press 0 to go back to options\n").split()
	except ValueError: return
	customID = create_model(username = username, password = password, name = name, description = description)
	closure["customID"] = customID
	custom_menu(username,password,closure)

# Function that allows user to train an untrained custom language model.
def train_existing(username,password,closure):
	closure = {}
	get_model_list(username,password)
	customID = get_ID()
	if customID == '0': return
	closure["customID"] = customID
	custom_menu(username,password,closure)

# Function that resets the model selections to their default values
def reset(username,password,closure):
	output["acoustic-model"] = original["acoustic-model"]
	output["base-model"] = original["base-model"]
	input('Values reset!\nPress any key to return to main menu...')

# Executes the appropriate function based on user input.
def exec_menu(choice,function_list,username,password,closure):
    os.system('clear')
    choice = choice.lower()
    if choice == '': return
    else:
        try: function_list[choice](username,password,closure)
        except KeyError: print("Invalid selection, please try again.\n")
    return


# Actions for the main menu
menu_actions = {
    '1': select_custom,
    '2': delete_custom,
    '3': create_custom,
    '4': train_existing,
    '5': advanced_menu,
    '6': reset,
    '8': exit
}

# *** Definitions for functions used in the custom menu ***

# Function that trains the model on a text corpus file
def single_file(username,password,closure):
	customID = closure["customID"]
	print("NOTE: The audio file must be " + colored("10 minutes",'red') + 
		" long and have the " + colored("'.wav'",'red') + " extension")
	filename = input("Enter name of audio file\n")
	while not os.path.isfile(filename):
		filename = input("ERROR: The specified file does not exist\nRe-enter audio filename\n")
	add_audio(username,password,filename,customID)
	train_model(username,password,customID)
	input('Press any key to return to main menu...')

# Actions for the new custom model menu
custom_menu_actions = {
	'1': single_file
}


# *** Definitions for functions used in the advanced menu ***
def list_resources_custom(username,password,closure):
	get_model_list(username,password)
	customID = get_ID()
	if customID == '0': return
	list_resources(username,password,customID)
	input('Press any key to return to main menu...')

# Function that upgrades the base model of a custom language model.
def upgrade_base_custom(username,password,closure):
	get_model_list(username,password)
	customID = get_ID()
	if customID == '0': return
	upgrade_base_model(username,password,customID)
	input('Press any key to return to main menu...')

# Function that resets a custom language model
def reset_custom(username,password,closure):
	get_model_list(username,password)
	customID = get_ID()
	if customID == '0': return
	reset_model(username,password,customID)
	input('Press any key to return to main menu...')

# Actions for the new advanced menu
advanced_menu_actions = {
	'1': list_resources_custom,
	'2': upgrade_base_custom,
	'3': reset_custom
}


# *** Functions that interact with Watson's STT API ***

# Function that resets the training of the given custom model.
def reset_model(username,password,customID):
	print("Resetting custom model...")
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/{}/reset".format(customID)
	r = requests.post(uri, auth=(username,password), verify=False, headers=headers)
	if r.status_code == 200: print("Model successfully reset")
	else: print("Model failed to reset")

# Function that upgrades the base model of the given custom model
def upgrade_base_model(username,password,customID):
	print("Upgrading base model...")
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/{}/upgrade_model".format(customID)
	r = requests.post(uri, auth=(username,password), verify=False, headers=headers)
	if r.status_code == 200: print("Base model successfully upgraded")
	else: print("Base model failed to upgrade")

# Function that lists all the audio resources for a custom acoustic model.
def list_resources(username,password,customID):
	print("Listing all audio resources...")
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/{}/audio".format(customID)
	r = requests.get(uri, auth=(username,password), verify=False, headers=headers)
	if r.status_code == 200: print(r.text)
	else : print("Unable to list custom audio information")

# Function that returns a list of all the available models
def get_model_list(username,password):
	print("\nGetting custom acoustic models...")
	uri =("https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations")
	r = requests.get(uri, auth=(username,password), verify=False, headers=headers)
	print("Get models returns: ", r.status_code)
	print(r.text)


# Function that adds audio to the acoustic model
def add_audio(username,password,filename,customID):

	custom_headers = {'Content-Type': "audio/wav"}

	if len(AudioSegment.from_file(filename)) <= 600000:
		print('Error: The audio file must be at least 10 minutes long')
		#sys.exit(-1)
		return
	if check_extension(filename,'wav') == False:
		print("Error: Wav audio file expected")
		#sys.exit(-1)
		return
	print('\nAdding audio file...')
	name = filename[:filename.rfind('.')]
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/{0}/audio/{0}".format(customID,name)
	with open(filename, 'rb') as f:
		r = requests.post(uri, auth=(username,password), verify=False, headers=custom_headers, data=f)

	print("Adding audio file returns: ", r.status_code)
	if r.status_code != 201:
	   print("Failed to add audio file")
	   print(r.text)
	   sys.exit(-1)
	   return

	print('Checking status of audio analysis...')
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/{0}/audio/{0}".format(customID,name)
	r = requests.get(uri, auth=(username,password), verify=False, headers=custom_headers)
	respJson = r.json()
	status = respJson['status']
	time_to_run = 10
	while (status != 'ok'):
	    time.sleep(10)
	    r = requests.get(uri, auth=(username,password), verify=False, headers=custom_headers)
	    respJson = r.json()
	    if respJson['status'] == 'invalid':
	    	print('Error: Audio file size exceeds 100 MB')
	    	sys.exit(-1)
	    	return
	    status = respJson['status']
	    print("status: ", status, "(", time_to_run, ")")
	    time_to_run += 10

	print("Audio analysis done!")

# Function that trains the acoustic model with the added audio file
def train_model(username,password,customID):
	print('\nTraining custom acoustic model')
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/{0}/train".format(customID)
	data = {}
	jsonObject = json.dumps(data).encode('utf-8')
	r = requests.post(uri, auth=(username,password), verify=False, data=jsonObject)

	print("Training request returns: ", r.status_code)
	if r.status_code != 200:
	   print("Training failed to start - exiting!")
	   sys.exit(-1)
	   return

	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/{0}".format(customID)
	r = requests.get(uri, auth=(username,password), verify=False, headers=headers)
	respJson = r.json()
	status = respJson['status']
	time_to_run = 10
	while (status != 'available'):
	    time.sleep(10)
	    r = requests.get(uri, auth=(username,password), verify=False, headers=headers)
	    respJson = r.json()
	    status = respJson['status']
	    print("status: ", status, "(", time_to_run, ")")
	    time_to_run += 10

	print("Training complete!")

# Function that creates a new model
def create_model(username,password, description,name):
	print("\nCreating custom acoustic model...")
	data = {"name" : name, "base_model_name" : "en-US_BroadbandModel", "description" : description}
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations"
	jsonObject = json.dumps(data).encode('utf-8')
	resp = requests.post(uri, auth=(username,password), verify=False, headers=headers, data=jsonObject)

	print("Acoustic Model creation returns: ", resp.status_code)
	if resp.status_code != 201:
	   print("Failed to create acoustic model")
	   print(resp.text)
	   sys.exit(-1)
	   return

	respJson = resp.json()
	customID = respJson['customization_id']
	print("Acoustic Model customization_id: ", customID)
	return customID

# Function that deletes the model corresponding to the given model ID.
def delete_model(username,password,customID):
	print("\nDeleting custom acoustic model...")
	uri = "https://stream.watsonplatform.net/speech-to-text/api/v1/acoustic_customizations/"+customID
	r = requests.delete(uri, auth=(username,password), verify=False, headers=headers)
	respJson = r.json()


if __name__ == '__main__':
 	interface(sys.argv[1],sys.argv[2])





























