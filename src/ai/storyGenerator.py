import streamlit as st
import cohere
import os
from openai import OpenAI
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
import transformers
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from fileutil.fileHelper import FileHelper
import logging
import logging.config


class GenerateStory():

    # Setup logging
    logging.config.fileConfig('logger-config.conf')

    # Create logger
    logger = logging.getLogger('ai_gen')
    
    def __init__(self):
      pass

    # Actual logic arena. Written in pure Python.
    def generate_story(self, story_prompt : str, temperature : str = "0.2" , max_tokens : str = "3000", top_p : str = "") -> str:    
        '''
        llm = LLM(
            model="command-r",
            temperature=0.7
        )  
        '''
        
        # This is no longer in use.
        #search_tool = SerperDevTool(n_results=10)   

        co = cohere.Client(os.getenv("COHERE_API_KEY")) # This is my trial API key
        self.logger.info(f"invoking the command model from cohere")
        self.logger.info(f"temprature value is: {temperature}")
        self.logger.info(f"max_tokens value is: {max_tokens}")
        self.logger.info(f"top_p value is: {top_p}")
        
        response = co.generate(
            model='command',
            prompt="Topic: "+str({story_prompt})+". On the above topic, I want to generate scene by scene ( like scene 1, scene 2 ) images which are strictly needed. All scene should have same background. Provide scenes with same or consistent background ( written in details) from different angles for 3d model. Each scene should be uniquely written",
            #max_tokens=max_tokens,
            temperature=temperature,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        return response.generations[0].text    
        
        
        # Debayan's code.. working but need to avoid OPENAI
        '''    
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {"role": "developer", "content": topic },
            {
                "role": "user",
                "content": "I want to generate scene by scene ( like scene 1, scene 2 ) images which are strictly needed. All scene should have same background. Strictly for Biology student. Provide scenes with same or consistent  back ground ( written in details) from different angles for 3d model. Each scene should be uniquely written"
            }
        ])
        logger.info(topic)
        return completion.choices[0].message.content
        '''
        
        
        # Original Agentic code.. full of hallucinations!!!
        '''
        # Create agent: Screenplay Writer
        screenplay_writer = Agent(
            role="Expert Screenplay Writer",
            goal=f"Research, analyze, and prepare one or more creative scenes from the given {topic}",
            backstory="You're a skilled screenplay writer specialized in preparing "
                    "engaging and compelling movie scenes based on the given story. "
                    "You excel at maintaining the perfect "
                    "balance between descriptive and entertaining writing."
                    "You also keep the consistency on the contexts between the scenes",
            allow_delegation=False,
            verbose=True,
            llm=llm
        )

        

        # Writing Task
        screenplay_writing = Task(
            description=("""
                Using the story provided, create an engaging movie screenplay that:
                1. Transforms the given story into multiple scenes for a movie
                2. Maintains all factual accuracy as well as consistency between the scenes
                3. Includes:
                    - Attention-grabbing introduction
                    - Well-structured body sections with clear headings
                    - Compelling conclusion 
            """),
            expected_output="""A detailed and polished movie screenplay in markdown format that:
                - Engages readers while maintaining accuracy and consistency between the scenes
                - Contains properly structured sections
                - Includes scene title
                - Presents information in an accessible yet informative way
                - Follows proper markdown formatting, use H1 for the title and H3 for the sub-sections""",
            agent=screenplay_writer
        )

        # Create Crew
        crew = Crew(
            agents=[screenplay_writer],
            tasks=[screenplay_writing],
            verbose=True
        )

        return crew.kickoff(inputs={"topic": topic})
        '''
     

    # Summarize the content of the uploaded file
    def summarizeUploadedFile(self, file_path : str) -> str:
        self.logger.info(f"invoked summarization")
        model_name = "allenai/led-large-16384-arxiv"
        self.logger.info(f"downloading model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.logger.info(f"triggering pipeline")
        pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=0)
        fh=FileHelper()
        self.logger.info(f"reading the uploaded file from {file_path}")
        content = fh.readUploadedFile(file_path)
        self.logger.info(f"uploaded content: {content}")
        summarized_text = pipe(
            content, 
            truncation=True, 
            max_length=64, 
            no_repeat_ngram_size=5, 
            num_beams=3, 
            early_stopping=True
            )
        self.logger.info(f"Completed summarization. The summarized text is: {summarized_text}")
        return summarized_text


        
