## Application Description:
**PLEASE NOTE THAT THE APPLICATION IS IN WIP STAGE. HENCE NEW MODIFICATIONS MAY BE PUSHED REGULARLY**




## How to Run:
    1. `cd` to app-directory
    2. Add .env file to the repo locally. add the following  API keys in there: *SERPER_API_KEY*, *COHERE_API_KEY*, *OPENAI_API_KEY*. You may need to create the keys of your own
    3. Run the command: `streamlit run app.py --server.port=<<PORT_NUMBER>> --server.maxUploadSize <<UPLOADED_FILE_SIZE_LIMIT>>`. Replace *PORT_NUMBER* and *UPLOADED_FILE_SIZE_LIMIT* values according to your requirement
    4. Step #3 should open up a new tab in the default browser and bring up the application

## How to Use:
    1. Add the prompt for the story in the prompt text-area
    2. Alternatively, you can also upload a file with PDF or TXT format. Please be mindful about the file format and size restrcitions
    3. Please ensure to follow the other validation rules in order to ensure the inputs are not rejected by the system
    4. If you upload a file and also add prompt in the text area, please note that only the prompt will take precedence over the uploaded file and be considered for the generation
    5. Once you are satisfied with the input, then you can optionally select the 'Temperature' value to decide the creativeness of the generation
    6. After you are done, click on the 'Generate Screenplays' button
    7. The system may take some time to provide the output. Please be patient while the spinner is running
    8. Upon satisfaction, you can download the screen play details from the output. Or re-do the Steps from #1 through #6, for any modification

### TIP: press win+; or win+. to insert emojis in the source files in windows environment
