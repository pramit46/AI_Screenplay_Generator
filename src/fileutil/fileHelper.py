import gc,os,base64
import streamlit as st
import tempfile
from pypdf import PdfReader
import magic
import logging
import logging.config
from generalutil.generalUtil import GeneralUtil

# Dependencies: pip install streamlit python-magic pypdf transformers tempfile python-magic python-magic-bin
### Python Logic and Helper Methods ###

class FileHelper():
    # Setup logging
    logging.config.fileConfig('logger-config.conf')

    # Create logger
    logger = logging.getLogger('ai_gen')
    gu=GeneralUtil()
    
    def __init__(self):
        self.global_temp_file_path=""
        #self.torch.classes.__path__ = [] # add this line to manually set it to empty. 


    # Identify the file type
    def getFileType(self, path_to_file : str) -> str:              
        if(path_to_file is not None or path_to_file != ""):                              
          filetype=magic.from_file(path_to_file)          
          self.logger.info(filetype)
          if("PDF" in filetype or "pdf" in filetype):
              self.logger.info(f"the uploaded file type is pdf")
              return "pdf"
          elif("Word" in filetype):
              self.logger.info(f"the uploaded file type is doc")
              return "doc"
          elif("text" in filetype):
              self.logger.info(f"the uploaded file type is txt")              
              return "txt"  
          else:
              self.logger.info(f"the uploaded file type is not supported/unknown to the application")              
              return "unsupported"    
        else:
            return "No File Path Provided"

    
    # Read the uploaded file    
    def readUploadedFile(self, file_path : str) -> str:        
        content=""           
        fileType=self.getFileType(file_path)
        # Read operation if the file is a PDF file       
        if(fileType=="pdf"):
            if(type(file_path) == str):
                try:
                    self.logger.info(f"reading the stored PDF file")
                    with open(file_path, 'rb') as f:                
                        reader=PdfReader(f)
                        for page in reader.pages:
                            content+=page.extract_text()                                       
                except Exception as e:
                    self.logger.error(f"An Exception occurred while reading the uploaded file from the path: {file_path}")
                    self.logger.error(e)
            
            # This is needed for the first time when the file is 
            # being read for validation without being stored, yet
            # MAY NOT BE NEEDED, ANYMORE since we are reading from stored location now.
            elif(type(file_path)==st.runtime.uploaded_file_manager.UploadedFile): 
                try:
                    self.logger.info(f"reading the uploaded PDF file")
                    content=file_path.getvalue()                    
                except:
                    self.logger.error(f"An Exception occurred while reading the uploaded file from the path: {file_path}")
                    self.logger.error(e)
            else:
                self.logger.warning(f"Unsupported File Type")

        # Read operation if the file is a TXT file
        elif(fileType=="txt"):
            try:
                self.logger.info(f"reading the uploaded TXT file")
                with open(file_path, 'r') as f:
                    for line in f.readlines():
                        content+=line
            except Exception as e:
                self.logger.error(f"An Exception occurred while reading the uploaded file from the path: {file_path}")
                self.logger.error(e)
        
        # Read operation if the file is a DOC file #@Pramit NOT WORKING
        elif(fileType=="doc"):
            try:
                self.logger.info(f"reading the uploaded DOC file")
                with open(file_path, 'r') as f:
                    for line in f.readlines():
                        content+=line
            except Exception as e:
                self.logger.error(f"An Exception occurred while reading the uploaded file from the path: {file_path}")
                self.logger.error(e)                    
        else:
          content="Unsupported File Type. Please upload a file with correct format"
                
        return content


    # Check if the prompt or file content meets validation criteria
    def validateContent(self, uploaded_file : str="", prompt : str="") -> bool:
        validFlag=False  
        # If manual prompt is provided then don't allow pdf input. 
        # Uploaded PDF can be displayed on screen but cannot be used for analysis or generation, 
        # neither to be stored, either
        if(prompt != None and len(prompt)>0):
            # Remove unnecessary leading and trailing whitespaces in order to avoid any confusions
            content=prompt.strip()
            #CheatCode to bypass validation :)
            if(content.startswith("^$")):
                self.logger.warning(f"#GODMODE: Bypassing validation.")
                content=content.removeprefix("^$")
                validFlag=True
            else:
                count=0
                for i in content.split(" "):                
                    count+=1
                self.logger.info(f"the content's word count is: {count}")
                if(count>=int(self.gu.parseConfigFile("CONTENT", "CONTENT_MIN_WORDS")) and count<=int(self.gu.parseConfigFile("CONTENT", "CONTENT_MAX_WORDS"))):
                    validFlag=True
                    st.markdown(f"The input prompt passed the validation criteria")
                else:
                    self.logger.warning(f"the user provided content fails validation")                
                    st.markdown(f"The input prompt does not meet the criteria")
        elif(uploaded_file is not None or uploaded_file != ""):          
            count=0
            content=self.readUploadedFile(uploaded_file)
            # Remove unnecessary leading and trailing whitespaces in order to avoid any confusions
            content=content.strip()
            self.logger.info(f"content:{content}")
            for i in content.split(" "):
                count+=1
            self.logger.info(f"the content's word count is: {count}")
            if(count>=int(self.gu.parseConfigFile("CONTENT", "CONTENT_MIN_WORDS")) and count<=int(self.gu.parseConfigFile("CONTENT", "CONTENT_MAX_WORDS"))):
                validFlag=True         
                st.markdown(f"The uploaded file passed the validation criteria")               
            else:
                self.logger.warning(f"the user provided content fails validation")
                # Remove the file from the temp location for compliance
                os.remove(uploaded_file)
                st.markdown(f"The provided content does not meet the criteria")
        else:
            self.logger.warning(f"no input provided or user provided content fails validation")
        self.logger.info(f"the input prompt: {content}\nhas valid flag value: {validFlag}")
        return validFlag
    

    # This serves same purpose as storeInTempLocation() but with temporary location instead of hardcoded location. 
    # Strictly for testing
    def x(self, uploaded_file : str) -> str:
        file_path = ""
        #tmp = tempfile.TemporaryFile()
        #logger.info(f"tmp:{tmp}")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
            self.logger.info(f"file_path:{file_path}")        
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
        except Exception as e:
            self.logger.error(f"{e}")
        return file_path


    # Store the uploaded file to a temporary location
    def storeUplaodedFileInTempLocation(self, uploaded_file : str) -> str:
        # Initialize file_path variable
        file_path=""
        # First store the file to temp location. We have to store the file first 
        # in order to read and validate it. Otherwise the uploaded file object 
        # will remain as byte object which will hinder the reading hence validation. 
        # Instead ease the life by storing the content in temp file and read from there. 
        # If validation FAILS, then we may have to delete the file from 
        # the temp location for compliance purpose
        try:            
            temp_dir=self.gu.parseConfigFile("FILE", "TEMP_FILE_STORAGE_PATH")                        
            file_path = os.path.join(temp_dir, uploaded_file.name)            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())                                                            
            self.logger.info(f"the file has been temporarily stored at the path: {file_path}")
        except Exception as e:
            self.logger.error(f"an error occurred: {e}")         
        # Set the global file path variable in order to access it from other methods    
        return file_path    


    # Display the uploaded PDF content. @Pramit NOT WORKING.
    def display_uploaded_file(self, uploaded_file : str):        
        # Opening file from file path        
        if(uploaded_file is not None or uploaded_file != "" or uploaded_file != ""):
            fileType=self.getFileType(path_to_file=uploaded_file)
            if(fileType=="pdf"):
                try:
                    st.markdown("### PDF Preview")
                    content=""
                    # open PDF
                    with open(uploaded_file, "rb") as pdf:
                        content = pdf.read()
                    base64_pdf = base64.b64encode(content).decode("utf-8")
                    temp_file=base64_pdf
                    # Embedding PDF in HTML
                    pdf_display = f"""<iframe src="data:application/pdf;base64,{temp_file}" width="400" height="100%" type="application/pdf"
                                  style="height:100vh; width:100%"
                                  >
                                  </iframe>"""
                    self.logger.info(f"the path of the uploaded file is: {uploaded_file}")   
                    self.logger.info(f"finished reading the PDF file. Moving to display the content on the WebUI")         
                    
                    # Displaying File
                    st.markdown(pdf_display, unsafe_allow_html=True)
                except Exception as e:
                    self.logger.error(f"Exception occurred: {e}")
            elif(fileType=="txt"):
                try:
                    st.markdown("### TEXT Preview") 
                    content=""
                    # open PDF
                    with open(uploaded_file, "r", encoding="utf-8") as txt:
                        content = txt.read()                                    
                    self.logger.info(f"the path of the uploaded file is: {uploaded_file}")   
                    self.logger.info(f"finished reading the TXT file. Moving to display the content on the WebUI")                             
                    # Embedding TXT in HTML
                    txt_display = f"""<iframe src="file:///{uploaded_file}" 
                    style="height:100vh; width:100%">
                    </iframe>"""
                    #st.components.v1.html(txt_display, height=600) # Use st.components.v1.html for iframe                   
                    
                    # Displaying File
                    st.html(txt_display, unsafe_allow_html=True)                
                except Exception as e:
                    self.logger.error(f"Exception occurred: {e}")            
            elif(fileType=="doc"):
                #logic to show doc file in iframe
                try:
                    st.markdown("### DOCUMENT Preview")
                    content=""
                    # open DOC
                    with open(uploaded_file, "rb") as doc:
                        content = doc.read()
                    base64_doc = base64.b64encode(content).decode("utf-8")
                    
                    # Embedding DOC in HTML
                    doc_display = f"""<iframe src="data:application/document;base64,{base64_doc}" width="400" height="100%" type="application/document"
                                  style="height:100vh; width:100%"
                                  >
                                  </iframe>"""
                    self.logger.info(f"the path of the uploaded file is: {uploaded_file}")   
                    self.logger.info(f"finished reading the DOC file. Moving to display the content on the WebUI")                 
                    
                    # Displaying File
                    st.markdown(doc_display, unsafe_allow_html=True)
                except Exception as e:
                    self.logger.error(f"Exception occurred: {e}")    
            else:
                self.logger.warning(f"Unsupported log format")
        else:
            self.logger.info(f"Uploaded File is empty/invalid/msy not be uploaded")

        
        
   