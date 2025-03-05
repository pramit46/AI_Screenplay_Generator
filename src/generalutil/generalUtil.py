import streamlit as st
import gc, os
import logging
import logging.config
import configparser


class GeneralUtil():
   
    # Setup logging
    logging.config.fileConfig('logger-config.conf')

    # Create logger
    logger = logging.getLogger('ai_gen')


    def __init__(self):
        pass


    # Reset Chat if session is invalid/expired # @Pramit NOT WORKING
    def reset_chat(self):
        self.logger.info(f"invoked reset")
        st.session_state.messages = []
        st.session_state.context = None
        st.session_state.story_prompt=""
        st.session_state.uploaded_file=""    
        st.session_state.temperature=0.2 
        #st.session_state.max_tokens=3000 
        #st.session_state.top_p=5 
        gc.collect()
        
    # Consent Dialgue pop up
    # @Pramit NOT WORKING FOR ESC PRESSING OR OUTSIDE CLICKING, 
    # But will still be enforced due to verification of true/false at the generate level
    @st.dialog("Please provide your consent")
    def showConsent(self,):
        # Disable the close icon on the top right corner of the page. This should be handled via CSS later instead of hardcoding here
        st.html(
        '''
            <style>
                div[aria-label="dialog"]>button[aria-label="Close"] {
                    display: none;
                }
            </style>
        '''
        )        
        st.write("I will be responsible for what I type in the prompt section or the file(s) I upload. I realize that the application is run by GenAI models hence may be prone to error or incorrect/harmful information. I will verify/do my own research before accepting the outcome of the application")
        # Use container to show the buttons side by side
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                agree=st.button("I Agree")            
            with col2:
                disagree=st.button("I don't Agree")           
        # Use another container to show the messages based on selction        
        with st.container():        
            if agree:
                st.session_state.consent = True
                self.logger.info(f"selected st.session_state.consent value is: {st.session_state.consent}")
                st.html('''<font color="green"><b>Provided Consent</b></font>''')
                st.rerun()
            else:
                st.session_state.consent = False
                self.logger.info(f"selected st.session_state.consent value is: {st.session_state.consent}")                                    
                st.html('''<font color="red"><b>We need your consent before we can proceed</b></font>''')
                st.stop()
                        
    # Genetric parser of the config file
    def parseConfigFile(self, section : str, key : str) -> str:
        config=configparser.ConfigParser()
        config.read('app-config.conf')
        output=config.get(section, key)
        self.logger.info(f"output of {key}: {output}")
        return output
    
    # Show dialogue box with warning to not breach the validation rules
    @st.dialog(" ") 
    def showValidationWarning(self,):
        # Disable the close icon on the top right corner of the page. This should be handled via CSS later instead of hardcoding here
        st.html(
        '''
            <style>
                div[aria-label="dialog"]>button[aria-label="Close"] {
                    display: none;
                }
                #dialogue-header {
                    color: #FF4B4B !important;
                }
                .stHtml {
                    color: #976f07;
                }
            </style>
        '''
        )        
        st.html("""<h2 id="dialogue-header">Please Follow The Below Validation Rules:</h2>
                1. The Input Word Count Should Be >=10  &  <=100<br/>
                2. No Nudity or Sexual Content<br/>
                3. No Violence<br/>
                4. No Curse Words<br/>
                5. No Image<br/>
                6. No Personally Identifiable Information (PII)<br/>""")

    
    # Create helper directories
    def createDirectories(self):
        directoryList=["temp","logs"]        
        for i in directoryList:
            if not os.path.exists(i):
                os.makedirs(i)
                self.logger.info(f"created path {i}")
            else:
                self.logger.info(f"the path {i} already exists")

                