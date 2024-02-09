import tkinter as tk
import PySimpleGUI as sg
import requests
import json
import threading
import queue
import textwrap

# Create class for funtions that will help with the user experience when working, this is where the functions
# like the chat history will be stored, and any other things that might be needed to do the main task at hand
class compute_ai_logic:
    def chathist(method=None, Information=None):
        # Initialize veriables
        Information = Information
        method = method


        chathistory = []

        # Handle different outcomes based on what was requested

        # Get information from the chat history
        if method == "get":
            return chathistory
        # Add information to the chat history
        elif method == "add":
            chathistory.append(Information)
        # Reset the chat history
        elif method == "clear":
            chathistory = []
        else:
            # Handle Errors
            return "Error: Invalid Method"


# Simple (somewhat) function to get information from the API (I stole this from my Discord bot, though this also support word
# streaming, and it able to make them come up as they are ready instead of just dumping all of the words when it
# finishes generating the response)
def ask_chat(prompt, window, output_queue, font_info):
    try:
        mixtral_api_url = 'http://localhost:11434/api/generate'
        headers = {'Content-Type': 'application/json'}
        payload = {'model': 'dolphin-mistral', 'prompt': prompt}

        response = requests.post(mixtral_api_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if line:
                response_data = json.loads(line)
                output_queue.put(response_data.get('response', ''))


        # Ensure that there is space after finishing generating the prompt.
        output_queue.put("\n\n\n")

        # Use write_event_value to update GUI from streaming thread
        window.write_event_value('-OUTPUT-', '\n')  # Insert newline between responses

    except Exception as e:
        output_queue.put(f"An error occurred: {e}")

# Function to display the "How to Chat" window to help people understand how to use the chatbot and to fit the criteria of the project
# WARNING: This is BROKEN!!! On my machine it was giving errors for a bit, then the formatting broke, I tried removing the function from textwrap,
# and then the formatting was still broken, just no errors, if anyone smart wants to fix this, please make the new lines work, trying with just
# \n was not really doing anything so anyone that wants to fix that, thanks
def open_how_to_chat_window():
    how_to_chat_text_new = (
        "General Question Examples:  ",
        "Can you guide me on understanding mental health issues and how to talk about them?  ",
        "What resources do you recommend for someone wanting to learn about mental health and engage in conversations about it?  ",
        "How can I educate myself about various mental health conditions to be more informed in discussions?  ",
        "Are there specific websites or books you suggest for learning about mental health to better communicate with others?  ",
        "I'm interested in discussing mental health topics. Where should I start my learning journey?  ",
        "Could you provide me with tips on talking about mental health in a sensitive and respectful manner?  ",
        "What are some key points I should be aware of when conversing with individuals facing mental health challenges?  ",
        "I want to be more knowledgeable about mental health. Any online courses or platforms you recommend?  ",
        "Can you share some conversation starters for discussing mental health without causing discomfort?  ",
        "How do I approach discussions about mental health without stigmatizing or stereotyping?  ",
        "I'd like to be more empathetic when talking about mental health. Any advice on cultivating empathy?  ",
        "Where can I find information on destigmatizing mental health to promote open conversations?  ",
        "What are the best practices for creating a supportive environment when discussing mental health?  ",
        "Are there specific organizations that focus on mental health education and awareness?  ",
        "I'm curious about mental health advocacy. Can you guide me on ways to contribute positively to the conversation?  ",
        "Specific Question Examples:  ",
        "I'm interested in learning more about anxiety disorders. Can you recommend resources for understanding the various types and effective ways to discuss them?  ",
        "Could you provide insights into bipolar disorder? I want to educate myself and discuss it with empathy and accuracy.  ",
        "What are some reliable sources for information on depression? I'd like to better understand its impact and engage in supportive conversations.  ",
        "I'm curious about schizophrenia. Where can I find reliable information to enhance my understanding and communicate about it in a respectful manner?  ",
        "Can you guide me on learning about OCD (Obsessive-Compulsive Disorder)? I want to be informed and approach discussions with sensitivity.  "
    )

    sg.popup_scrolled(how_to_chat_text_new, title='How to Chat', size=(80, 40), non_blocking=True)

# List of available fonts for Linux to help if they have trouble reading to me more accessible
available_fonts = [
    'DejaVu Sans',
    'Liberation Sans',
    'Arial',
    'Hermit',
    'Roboto',
    'Source Code Pro'
    # Personally I dont know what other fonts are available on Linux, so I just added the ones that I know of
]

# Create the main window and add the functiosn to be able to change all of the setting and to be able to open windows that I put together before.
layout = [
    [sg.Multiline(size=(120, 40), key='-OUTPUT-', font=('DejaVu Sans', 14), autoscroll=True)],
    [
        sg.Input(key='-IN-', size=(60, 1)),
        sg.Button('Send'),
        sg.Button('How to Chat'),
        sg.Text('Font:'),
        sg.Combo(values=available_fonts, default_value='DejaVu Sans', key='-FONT-'),
        sg.Text('Size:'),
        sg.Combo(values=[str(i) for i in range(8, 21)], default_value='14', key='-SIZE-')
    ]
]

window = sg.Window('Chatbot', layout, finalize=True)

# Use a separate thread for the streaming response so that it is not interrupted. If it is not on a seperate thread, it will never show, the while true loop
# for the GUI will not allow it to execute its functions and the screen updater is somehow not a part of that I dont know if you want fix that
output_queue = queue.Queue()
streaming_thread = threading.Thread(target=ask_chat, args=('Greetings', window, output_queue, None), daemon=True)
streaming_thread.start()

while True:
    event, values = window.read(timeout=100)  # Add a timeout to allow GUI updates (opens small holes for it to be able to pass information instead of just being a wall)

    if event == sg.WINDOW_CLOSED:
        break
    elif event == sg.TIMEOUT_KEY:
        try:
            response_chunk = output_queue.get_nowait()
            # Update the GUI with the entire response on one line without creating a new line like it was before :(
            window['-OUTPUT-'].update(response_chunk, append=True)
        except queue.Empty:
            pass
    elif event == 'Send' or (event == '-IN-' and values['-IN-'] and values['-IN-'][-1] == '\n'):
        # Get the text from the input field to send to the API
        prompt = values['-IN-'].strip()

        if prompt:  # Check if the input is not empty for no errors or crashes
            # Use the ask_chat function to interact with the chatbot
            font_info = (values['-FONT-'], int(values['-SIZE-']))
            streaming_thread = threading.Thread(target=ask_chat, args=(prompt, window, output_queue, font_info), daemon=True)
            streaming_thread.start()
    elif event == 'How to Chat':
        # Open the "How to Chat" window for nerds that are stoopid
        open_how_to_chat_window()

# Close the window "ALT + F4 for free robux!!!11!!1!!11!!1!1!!!1"
window.close()
