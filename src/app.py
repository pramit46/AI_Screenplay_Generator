import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import uuid
from fileutil.fileHelper import FileHelper
from ai.storyGenerator import GenerateStory
from generalutil.generalUtil import GeneralUtil
import logging
import logging.config


# Setup logging
logging.config.fileConfig('logger-config.conf')

# Create logger
logger = logging.getLogger('ai_gen')

# Entry Point.. for debugging purpose
logger.info(f"Firing up the application")

### Initial Setup ###
# Load environment variables
load_dotenv()
logger.info(f"Loaded the environment variables")

#Create Session ID
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}
session_id = st.session_state.id
logger.info(f"session_id: {session_id}")
file_path=""

fh=FileHelper()
gs=GenerateStory()
gu=GeneralUtil()

# Create the adidtional directories like temp, logs etc in order to initialize the application.
gu.createDirectories()

# Streamlit page config
st.set_page_config(page_title="AI Story to Screenplay Generator", page_icon="🦄", layout="wide")


### Page Design ###

# Title and description
st.title("🎇 AI Story to Screenplay Generator")
st.markdown("Generate comprehensive small screenplays out of the user provided stories using AI agents.")


# This is supposed to enforce the consent page at the beginnin but will move this function to generate_button press action
#if "consent" not in st.session_state or st.session_state.consent!=True:    
#    gu.showConsent()


# Build Sidebar
with st.sidebar:
    st.header("Content Settings")
    #st.markdown("### Content Settings")
    
    # Make the text input take up more space # @Pramit SHOULD ONLY WORK IF FILE UPLOAD IS NOT DONE
    story_prompt = st.text_area(
        "What's your Story? (Type/Paste your story)",
        height=150,
        placeholder="Enter the Story that you want to generate the screenplays for..."
    )
    # Add the prompt to session_state for future reference. Not needed immediately
    if(story_prompt is not None):
        st.session_state.story_prompt=story_prompt
        
    # Add some spacing. May not be needed in order to declutter the page.
    #st.markdown("----------------------------OR-------------------------")
    
    # Add a File Uploader widget as an alternative to prompt typing # @Pramit SHOULD ONLY WORK IF STORY PROMPT IS NOT FILLED
    uploaded_file = st.file_uploader(
        "Upload a file (Alternative Option)", 
        type=['pdf', 'txt'], 
        accept_multiple_files=False, 
        key=None, 
        help="Alternatively, you can upload a pdf or text formatted story file. But prompt will take precedence over an uploaded file", 
        disabled=False, 
        label_visibility="visible"        
    )
    
    # For uploaded_file in uploaded_files: # Use only if accept_multiple_files=True
    if uploaded_file is not None:
        st.session_state.uploaded_file=uploaded_file.name         
        #st.write("filename:", uploaded_file.name) # It's optional to show the filename and other details since we are already showing the uploaded filename once
        file_path=fh.storeUplaodedFileInTempLocation(uploaded_file)          
        #file_path=x(uploaded_file)
        
    
    # Add more sidebar controls if needed. Add/remove as per the need
    st.markdown("### Advanced Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2)
    st.session_state.temperature=temperature
    #max_tokens = st.slider("Max Tokens", 500, 5000, 3000)
    #st.session_state.max_tokens=max_tokens
    #top_p=st.slider("Top P", 0,10,5)
    #st.session_state.top_p=top_p
    
    # Add some spacing
    st.markdown("---")

    
    # Make the generate button more prominent in the sidebar
    generate_button = st.button("Generate Screenplays", type="primary", use_container_width=True)
    gu=GeneralUtil()
    st.button("Clear ↺", on_click=gu.reset_chat, type="tertiary", use_container_width=True) # @Pramit NOT WORKING
    
    # Add some helpful information
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. Enter your story in the text area above
        2. Alternatively, upload story file (Optional).
        3. Adjust the temperature if needed (higher = more creative, lower = more realistic)
        4. Click 'Generate Screenplay' to start
        5. Wait for the AI to generate your scenes
        6. Download the result as a markdown file
        """)


# Main content Display area
if generate_button and (story_prompt or uploaded_file):
    if("consent" not in st.session_state or st.session_state.consent!=True):
        f"The consent is needed before generating the output."
        try: 
            gu.showConsent()
        except Exception as e:
            logger.error(e)
        st.stop()
    else:
        with st.spinner('Generating Screenplay... This may take a moment.'):
            validity=fh.validateContent(prompt=story_prompt)
            if validity:
                try:
                    summaryOfUploadedFile=""
                    result=""                                    
                    if(story_prompt is None):
                        if(uploaded_file is not None): 
                            summaryOfUploadedFile = gs.summarizeUploadedFile(uploaded_file)
                            story_prompt = summaryOfUploadedFile                    
                    #logger.info(f"Story Prompt: {story_prompt}") # Moved this to validation section due to G##MODE
                    if(story_prompt is not None):                        
                        result = gs.generate_story(story_prompt=story_prompt, temperature=temperature)                        
                    st.markdown("### Generated Screenplays")
                    st.markdown(result)
                    logger.info(f"story has been generated and displayed")
                    
                    # Add download button
                    st.download_button(
                        label="Download Screenplay Content",
                        data=result, #result.raw
                        #file_name=f"{topic.lower().replace(' ', '_')}_screenplay.md",
                        file_name=f"Story_To_Screenplay_{datetime.now()}.md",
                        mime="text/markdown"
                    )
                    logger.info(f"the story has been downloaded")
                except Exception as e:
                    logger.error(f"An error occurred: {str(e)}")
                    st.error(f"An error occurred: {str(e)}")
            else:
                logger.warning(f"failed due to validation concern")
                gu.showValidationWarning()                
# Footer
st.markdown("---")
# Footer:: Show uploaded PDF for side-by-side comparison between the uploaded content vs generated story
if(uploaded_file is not None):
    # Display the uploaded PDF    
    fh.display_uploaded_file(uploaded_file=file_path) 
st.markdown("Built with Streamlit and powered by Cohere's Command R7B")