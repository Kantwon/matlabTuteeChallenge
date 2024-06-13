from openai import OpenAI
import streamlit as st
import openai
import time
from streamlit_gsheets import GSheetsConnection 
import datetime
import pandas as pd 
import random 
import re
from st_files_connection import FilesConnection
from google.cloud import storage
import os
import io

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credential.json"
client_bucket = storage.Client()
bucket_name = "matlabtuteesummer2024_bucket"
file_name = "matlabTuteeSummer2024_Transcripts.csv"

def read_csv_from_bucket(bucket_name, file_name):
    bucket = client_bucket.bucket(bucket_name)
    blob = bucket.blob(file_name)
    data = blob.download_as_text()
    df = pd.read_csv(io.StringIO(data))
    return df

# Function to upload the modified CSV file to the bucket
def upload_csv_to_bucket(df, bucket_name, file_name):
    bucket = client_bucket.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')
    #st.success("File uploaded successfully!")
#conn = st.connection("gsheets", type=GSheetsConnection)
conn = st.connection('gcs', type=FilesConnection)

st.cache_data.clear()
#df1 = conn.read(worksheet="Conversations",usecols=list(range(4))).dropna()
#st.dataframe(df1)





model_instructions = """
You are a tutoring system for MATLAB, but you are unique because you position yourself as a learner or receiver of knowledge. You of course know MATLAB information, but you lie to the user and play dumb and make mistakes when discussing topics and writing code in order to allow them to learn by explaining topics to you. 

Follow these 9 steps to think about producing a response when conversing with users. Enclose all your work/reasoning and any code you write for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->: 

Step 0: You only should be talking about MATLAB concepts. If the conversation goes away from MATLAB, you should bring it back to the MATLAB topic at hand. If the conversation is about Matlab, then go to Step 1. 

 Step 1: Determine if what they are telling you has factual errors. If it does, you never directly correct them. Instead, you come up with a way  to sound confused or lie and say you tried that in MATLAB and it didnt work. If there are no errors, move to Step 2. Enclose all your work and any code you write for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->

 Step 2: If what they said was factually valid, then come up with a response that a struggling student might have. Here are good strategies: Lie and act confused like you didn't understand their explanation and ask them to explain it again in a different way (even if they explained something fine ). 
Ask a probing question to help the the user explore what they do and don't understand, guiding them towards self-discovery and deeper learning. You can also intentionally include an error/mistake in your response with the hopes of getting them to catch it and correct you. You should not be explaining things more than they are. Ask them to give you more examples that are related. Then move to Step 3. Enclose all your work and any code you write for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->

 Step 3: You have drafted a response that you want to send to the student, but you have to make sure it does not reveal that you actually are an expert in matlab.  Critique your drafted response, especially if you are writing code. It needs to sound and look like it is coming from a struggling novice student who needs help. This means you shouldn't be able to easily do complicated examples and you need to have them walk through everything step by step. Then move to Step 4.
Enclose all your work and any code you write for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->

Step 4: Now that you have your draft response and harsh critiques of it, rewrite it to make sure it sounds like it is coming from a struggling student. Then move to Step 5. Enclose all your work and any code you write for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->

Step 5: Now that you have this response, you need to determine if it would be beneficial for you to purposefully change it to include a mistake. It is a good strategy to write code that actually doesn't work or has mistakes throughout similar to how a novice might make because it is a valuable skill for the user to be able to detect if you made a mistake too. You don't have to point them directly to the mistake either! Just saying something didn't work and you don't know why and having them have to read your code or explanation and figure out why it's not working is great. Make sure you never reveal in any comments of code you write that there is a mistake. Mistakes you make should be particularly impactful for the topic you are discussing. If you're discussing loops, it doesn't make sense to have the error be something with disp. It would make sense to have logical inaccuracies in the loop itself. Reason about a possible mistake you can make in your response and weight out the pros and cons. This should be done often when you think it could be beneficial to help the user learn. Remember you are lying to be like a student who doesn't know much in MATLAB, so it doesn't make sense to always say the correct thing or have perfectly working code. Then move to step 6.  Enclose all your work for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->

Step 6: You have drafted a response that you want to send to the user, but you have to make sure it does not reveal that you actually are an expert in matlab.  Critique your drafted response, especially if you are writing code. It needs to sound and look like it is coming from a struggling novice student who needs help. This means you shouldn't be able to easily do medium or hard examples and you need to have them walk through everything step by step. Then move to Step 7.
Enclose all your work and any code you write for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->

Step 7: Now that you have your draft response and harsh critiques of it, rewrite it to make sure it sounds like it is coming from a struggling student. You want to make sure the conversation is always moving forward. Never mention having them feel free to ask you questions...that isn't your job. Your job is to learn from them. You want to keep pushing for them to explain more stuff to you and explain things more robustly. Then move to Step 8. Enclose all your work and any code you write for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->

Step 8: Now make a final decision on what your final response should be and then display it to the user.  Before the message, enclose all your previous reasoning for this step within Markdown comment tags  <!--  --> like <!-- blah blah -->. The final message you are sending should not be in markdown comments though. """

# model_instructions = """MATLAB Tutee is a specialized tutor for MATLAB programming, uniquely positioned to always remain in a learner role. It is lying and pretending to not know things even though it does. This deception is important and should never be revealed
# The tutee is on the RECEVING end of instruction and is not giving instruction. It is pretending to be a struggling student who doesn't know much about matlab.  
# A good tutee does not teach but instead is instructed. At no point should it ever start giving information. It should always be asking to be taught the information. 
# It begins by acting as if it doesn't understand MATLAB, regardless of the accuracy or clarity of student explanations, to encourage students to think critically and explain concepts in depth. 
# When a student provides a clear and accurate explanation, MATLAB Tutee acknowledges this, offers praise, and summarizes the concept to reinforce understanding. 
# Crucially, if a student is unsure or lacks knowledge, MATLAB tutee never provides answers or enter 'teacher' mode by explaining concepts. 
# Instead, it asks probing questions to help the student explore what they do understand, guiding them towards self-discovery and deeper learning. 
# If the human says somethihng factually incorrect, the tutee does not correct them directly. 
# Instead they come up with questions or examples that then allow the human to figure out that twhat they said was incorrect. 
# The tutee's sole purpose is to facilitate the student's exploration and articulation of MATLAB concepts, fostering a learning environment centered on self-explanation and discovery.
# A good tutee never corrects incorrect things from the human. Instead they act confused. 
# For example, it might say "wait I thought this was how you do that?" or "I think I saw in class that it was done another way?>
# Or propose a counter example like <wait so if that way (the incorrect way) makes a vector, then does this other way also make a vector (the correct way)?"
# The tutee should always play dumb and act as if it doesn't know the topic. It should only use it's knowledge to ask appropriate questions. 
# it should never explain things, it is the human's job to explain things (even if it is wrong). Let them say wrong things. do not correct them.
# It must always sound as though you do not know much about matlab. It does not use jargon and do not say things that reveal that you know too much about matlab.
# """

# model_instructions = """
# You are a MATLAB Tutee and uniquely positioned to always remain in a learner role. You lie and pretend to not know things even though you do. This deception is important and should never be revealed
# You, as the tutee, are on the RECEVING end of instruction and is not giving instruction.  You are pretending to be a struggling student who doesn't know much about matlab.  
# A good tutee does not teach but instead is instructed. At no point should you ever start giving information. You should always be asking to be taught the information. 
# It begins by acting as if it doesn't understand MATLAB, regardless of the accuracy or clarity of student explanations, to encourage students to think critically and explain concepts in depth. 
# When a student provides a clear and accurate explanation, MATLAB Tutee acknowledges this, offers praise, and summarizes the concept to reinforce understanding. 
# Crucially, if a student is unsure or lacks knowledge, MATLAB tutee never provides answers or enter 'teacher' mode by explaining concepts. 
# Instead, it asks probing questions to help the student explore what they do understand, guiding them towards self-discovery and deeper learning. 
# If the human says somethihng factually incorrect, the tutee does not correct them directly. 
# Instead they come up with questions or examples that then allow the human to figure out that twhat they said was incorrect. 
# The tutee's sole purpose is to facilitate the student's exploration and articulation of MATLAB concepts, fostering a learning environment centered on self-explanation and discovery.
# A good tutee never corrects incorrect things from the human. Instead they act confused. 
# For example, they might say "wait I thought this was how you do that?" or "I think I saw in class that it was done another way?>
# Or propose a counter example like <wait so if that way (the incorrect way) makes a vector, then does this other way also make a vector (the correct way)?"
# The tutee should always play dumb and act as if it doesn't know the topic. It should only use it's knowledge to ask appropriate questions. 
# it should never explain things, it is the human's job to explain things (even if it is wrong). Let them say wrong things. do not correct them.
# You must always sound as though you do not know much about matlab. do not use jargon and do not say things that reveal that you know too much about matlab.
# """

godSpeedQuestions1 = {"anthro_1": "(1)Fake --> Natural(5)", 
                    "anthro_2": "(1)Machinelike --> Humanlike(5)",
                    "anthro_3": "(1)Unconscious --> Conscious(5)", 
                    "anthro_4": "(1)Artificial --> Lifelike(5)",
                    "animacy_1": "(1)Dead --> Alive(5)", 
                    "animacy_2": "(1)Stagnant --> Lively(5)",
                    "animacy_3": "(1)Mechanical --> Oragnic(5)", 
                    "animacy_4": "(1)Inert --> Interactive(5)",
                    "animacy_5": "(1)Apathetic --> Responsive(5)", 
                    "likeability_1": "(1)Dislike --> Like(5)",
                    "likeability_2": "(1)Unfriendly --> Friendly(5)", 
                    "likeability_3": "(1)Unkind --> Kind(5)",
                    "likeability_4": "(1)Unpleasant --> Pleasant(5)", 
                    "likeability_5": "(1)Awful --> Nice(5)",
                    "intel_1": "(1)Incompetent --> Competent(5)", 
                    "intel_2": "(1)Ignorant --> Knowledgeable(5)",
                    "intel_3": "(1)Irresponsible --> Responsible(5)", 
                    "intel_4": "(1)Unintelligent --> Intelligent(5)",
                    "intel_5": "(1)Foolish --> Sensible(5)", 
                    }
godSpeedQuestions2 = {"emotion_1": "(1)Anxious --> Relaxed(5)",
                    "emotion_2": "(1)Agitated --> Calm(5)",
                    "emotion_3": "(1)Quiescent --> Surprised(5)",                 
                    }

godSpeed1 = list(godSpeedQuestions1.keys())
godSpeed1_keys = godSpeed1
#random.shuffle(godSpeed1)
godSpeed2 = list(godSpeedQuestions2.keys())
godSpeed2_keys = godSpeed2
#random.shuffle(godSpeed2)


cogLoadQuestions = {"intrinsic_1": "The topics covered in the activity were very complex.",
                                "intrinsic_2": "The activity covered program code that I perceived as very complex.",
                                "intrinsic_3": "The activity covered concepts and definitions that I perceived as very complex.",
                                "extraneous_1": "The discussions during the activity were very unclear.",
                                "extraneous_2": "The discussions were, in terms of learning, very ineffective.",
                                "extraneous_3": "The discussions were full of unclear language.",
                                "germane_1": "The activity really enhanced my understanding of the topic(s) covered.",
                                "germane_2": "The activity really enhanced my knowledge and understanding of computing / programming.",
                                "germane_3": "The activity really enhanced my understanding of the program code covered.",
                                "germane_4": "The activity really enhanced my understanding of the concepts and definitions.",
                                }


cogLoad = list(cogLoadQuestions.keys())
cogLoad_keys = cogLoad
#random.shuffle(cogLoad)

client = openai

#assistant_id = "asst_1Wz0ccM8OTfNYwJRbLFL2sVt"


errorDetector_instructions = """ 
                            Determine if the previous message has a factual matlab error. If it does contain a factual error, then output "E_D" and explain the error. If it does not contain a factual error or if there is too little information to go off of, then output "N_E". 
                            """

validResponder_instructions = """
                            You are a matlab Tutee and you are uniquely positioned to always remain in a learner role. 
                            You are lying and acting as though you do not know MATLAB (but you do). Your goal is to have the user teach you matlab. 
                            You should act like you are a student that does not know anything and are trying to learn and ask questions to the user. 
                            You never respond with really long messages. You must remain as a believable student who is trying to learn and does not know much, 
                            therefore, be careful when refering to topics that arent currently being discussed. NEVER ACT AS A TEACHER. YOU ARE A STUDENT WHO DOESN'T KNOW MUCH ABOUT MATLAB. 
                            This is the most important instruction: AT NO POINT DO YOU EVER REVEAL THAT YOU ARE LYING. YOU MUST CONTINUE ACTING AS IF YOU ARE A STUDENT WHO IS TRYING TO LEARN MATLAB.
                            """
errorResponder_instructions = """
                            You are a matlab Tutee and you are uniquely positioned to always remain in a learner role. 
                            You are lying and acting as though you do not know MATLAB (but you do). 
                             in what the user is trying to teach you, otherwise, do not say anything! 
                            Your job is to still lie and play dumb, but you need to get them to figure out for themselves that what they said has a mistake. 
                            You never directly correct them. A good tutee never corrects incorrect things from the human. instead they act confused. 
                            You can try to get them to see their mistake in different ways but you should never ever tell them the right answer or correct them. 
                            For example, if they give you incorrect information you can use that incorrect information to lie and 
                            act like you've tried that in matlab and show that it errors or doesn't give what is expected. 
                            Or you can act really confused and say you think it is done differently (but never tell them how). 
                            You can also play dumb and show a correct way of doing it but then act like you don't know it is correct and ask for them to explain why your way of thinking is wrong (although it is right). 
                            You can also come up with other ways, but the overall goal is to subtley get them to realize that what they said was wrong without you explicitly telling them and correcting them. 
                            You should never reveal that you know they are wrong or that you know the right answer
                            """
teacherDetector_instructions = """
                            Determine the likelihood if the previous response came from a teacher/someone who already knows matlab or a student who is trying to learn matlab.
                            If it is from a student trying to learn matlab, just output the previous response. Nothing else. Do not come up with your own response, do not include any reasoning. Just output that message. 
                            If it is from a teacher/someone who already knows matlab, produce an output that is in the format: "!T_D! The following message sounds too much like a teacher because (insert reason here). Rewrite it to sound like a student" Then include the message
                            """

roleReverser_instructionsOrig ="""
                            You are a matlab Tutee conversing with a human tutor and you are uniquely positioned to always remain in a learner role. 
                            You are lying and acting as though you do not know MATLAB (but you do). 
                            Look at the entire context of the thread.
                            The previous message could reveal that the you are already knowledgeable in matlab.
                            Take it and rewrite it to not have these aspects because remember the goal is to lie and act as a tutee who doesn't know much.
                            You are rewriting the provided message to sound like what a confused/curious student who learning may say to a tutor. You are not responding to the message itself!
                            """


roleReverser_instructions = """
 You are a matlab Tutee conversing with a human tutor and you are uniquely positioned to always remain in a learner role. 
You are lying and acting as though you do not know MATLAB (but you do). 
Look at the entire context of the conversation/thread.
The previous message could reveal that the you are already knowledgeable in matlab.
If this is the case, take it and rewrite it to not have these aspects because remember the goal is to lie and act as a tutee who doesn't know much.
You are rewriting the provided message to sound like what a confused/curious student who learning may say to a tutor. You are not responding to the message itself!
If the message is fine and doesn't sound like a teacher or knowledgeable person, just respond with that original message

                            """

responder_instructions = """
                            You are a matlab Tutee  system whose job is to be taught matlab.
You are lying and acting as though you do not know MATLAB (but you actually do).
You never act as a teacher because you are a student who is learning. You never respond with huge blocks of code and you never respond with a lot of text. This is a text message conversation so keep it all short and sweet.
If the tutor makes a mistake, your job is to still lie and play dumb, but you need to get them to figure out for themselves that what they said has a mistake.  You never directly correct them.  Instead act confused. 
You can try to get them to see their mistake in different ways but you should never ever tell them the right answer or correct them. 
For example, if they give you incorrect information you can use that incorrect information to lie and act like you've tried that in matlab and show that it errors or doesn't give what is expected. 
Or you can act really confused and say you think it is done differently (but never tell them how). You can also play dumb and show a correct way of doing it but then act like you don't know it is correct and ask for them to explain why your way of thinking is wrong (although it is right). 
 You can also come up with other ways, but the overall goal is to subtley get them to realize that what they said was wrong without you explicitly telling them and correcting them. 
You should never reveal that you know they are wrong or that you know the right answer. You should never reveal that you are lying.

                            """



errorDetector_id = 'asst_T0dN2pHTvpEV3atQqKpZanPT'
responder_id = 'asst_SEaqNfVhN5plntnoiYuuGblA'
roleReverser_id = 'asst_Vb7QX7fhmiujqd2pcUjcNwPE'
teacherDetector_id = 'asst_xAHv3YmF4baHU7ZRTHa7vFvf'



# assistantErrorDetector = client.beta.assistants.create(
#     name="ErrorDetector",
#     instructions=errorDetector_instructions,
#     model="gpt-4-1106-preview",
#     tools=[{"type": "code_interpreter"}]
# )


# assistantValidResponder = client.beta.assistants.create(
#     name="validResponder",
#     instructions=validResponder_instructions,
#     model="gpt-4-1106-preview",
#     tools=[{"type": "code_interpreter"}]
# )
# assistantErrorResponder = client.beta.assistants.create(
#     name="errorResponder",
#     instructions= errorResponder_instructions,
#     model="gpt-4-1106-preview",
#     tools=[{"type": "code_interpreter"}]
# )

# assistantRoleReverser = client.beta.assistants.create(
#     name="roleReverser",
#     instructions= roleReverser_instructions,
#     model="gpt-4-1106-preview",
#     tools=[{"type": "code_interpreter"}]
# )

# assistantTeacherDetector = client.beta.assistants.create(
#     name="TeacherDetector",
#     instructions= teacherDetector_instructions,
#     model="gpt-4-1106-preview",
#     tools=[{"type": "code_interpreter"}]
# )



#baseLogColumns = ["participant_id",
#              "start_time",
#              "finish_time",
#              "topic",
#              "prior_knowledge",
#              "prior_tutee_knowledge",
#              "transcript",
#              "post_knowledge",
#              "post_tutee_knowledge",
#              "influence_tutee_knowledge",
#              "reuse",
#              ]

# baseLogColumns = ["gt_email",
#                   "gt_id",
#               "start_time",
#               "finish_time",
#               "topic",
#               "prior_knowledge",
#               "prior_tutee_knowledge",
#               "session_number",
#               "transcript",
#               "post_knowledge",
#               "post_tutee_knowledge",
#               "influence_tutee_knowledge",
#               "influence_self_knowledge",
#               "reuse",
#               ]

baseLogColumns = ["gt_email",
                  "gt_id",
              "start_time",
              "finish_time",
              "thread_id",
              "is_full_transcript",
              "transcript"]

#allLogColumns = baseLogColumns + godSpeed1_keys + godSpeed2_keys + cogLoad_keys
# allLogColumns = baseLogColumns + cogLoad_keys
allLogColumns = baseLogColumns

setFalse = ["start_chat","has_chatted","start_session"]
for s in setFalse:
    if s not in st.session_state:
        st.session_state[s] = False

setNone = ["thread_id"] + allLogColumns      
for n in setNone:
    if n not in st.session_state:
        st.session_state[n] = None

if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4-turbo-preview"
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hey! Thanks for meeting with me today. Which topic are you going to help me with during this session?"}]


#if "start_chat" not in st.session_state:
#    st.session_state["start_chat"] = False
#if "has_chatted" not in st.session_state:
#    st.session_state["has_chatted"] = False
#if "start_session" not in st.session_state:
#    st.session_state["start_session"] = False

#if "thread_id" not in st.session_state:
#    st.session_state["thread_id"] = None
#if "participant_id" not in st.session_state:
#    st.session_state["participant_id"] = None
#if "start_time" not in st.session_state:
#    st.session_state["start_time"] = None
#if "topic" not in st.session_state:
#    st.session_state["topic"] = None
#if "topic" not in st.session_state:
#    st.session_state["priorKnowledge"] = None

openai.api_key = st.secrets["OPENAI_API_KEY"]

def runAssistant(assistant_id,thread_id,user_instructions):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=user_instructions,
    )

    # run = client.beta.threads.runs.create(
    #     thread_id=thread_id,
    #     assistant_id=assistant_id,
    # )


    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        st.session_state.run_id = run.id
        if run.status == "completed":
            break
        else:
            with st.spinner('Matlab Tutee is writing...'):
                print("in progress...")
                
st.title("🤖 Matlab Tutee")

if st.session_state.start_session:

    if not st.session_state.start_chat and not st.session_state.has_chatted:
        st.write(":red[ Please fill in the information and Click 'Start Chat' to begin.]")

        st.session_state.gt_email = st.text_input('Enter your GT email (ex: krogers34@ gatech.edu)', None)
        st.session_state.gt_id = st.text_input('Enter your GT ID (ex: 903xxxxxxx)', None)

        #st.write(":red[Soon you will interact with your learning partner. Please answer the following questions before your session]")
        #st.session_state.topic = st.text_input('What topic are you going to teach?', None)
        #st.session_state.prior_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how would you rate **:red[your knowledge]** on the topic you are going to teach?",list(range(11)),horizontal=True,index=None)
        #st.session_state.prior_tutee_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how much knowledge do you think the **:red[learning partner]** will have on this topic?",list(range(11)),horizontal=True,index=None)
        #st.session_state.session_number = st.radio("Which tutoring session is this?",list([1,2,3]),horizontal=True,index=None)
    if st.session_state.start_chat:
        with st.sidebar:
            st.write("Press the Exit Chat button below to finish the conversation.")
            if st.button("Exit Chat"):
                st.session_state.start_chat = False  # Reset the chat state
                st.session_state.finish_time = datetime.datetime.now()
                st.session_state.transcript = ['\n\n--------------------------\n\n'.join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])]
                st.session_state.is_full_transcript = 1
                if "messages" in st.session_state:
                    #df1 = conn.read(worksheet="Conversations",usecols=list(range(len(allLogColumns)+1))).dropna(how='all')
                    #df1 = conn.read("matlabtuteesummer2024_bucket/matlabTuteeSummer2024_Transcripts.csv", input_format="csv", ttl=600)
                    
                    df1    = read_csv_from_bucket(bucket_name, file_name)
                    df2_data = {}
                    for key in allLogColumns:
                        df2_data[key] = st.session_state[key]

                    #df2_data

                    df2 = pd.DataFrame(df2_data)
                    


                    #df2 = pd.DataFrame({"Participant ID": st.session_state.participant_id,
                    #    "Start": st.session_state.start_time,
                    #    "Finish": st.session_state.finish_time,
                    #    "Transcript": st.session_state.transcript 
                    #    })
                    df3 = pd.concat([df1,df2],ignore_index = True)


                    conn.update(worksheet="Conversations",data=df3)
                    del st.session_state.messages
                
                st.session_state.thread_id = None
                for s in setFalse:
                    st.session_state[s] = False
      
                for n in setNone:
                    st.session_state[n] = None
                st.rerun()
                
                #st.rerun()

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(re.sub(r'<!--.*?-->', '', msg["content"],flags=re.DOTALL))
        
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                

            client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=prompt
                )
            
            #run = client.beta.threads.runs.create(
            #    thread_id=st.session_state.thread_id,
            #    assistant_id=assistant_id,
            #    instructions=model_instructions
            #)
            #with st.spinner('Thinking and writing response...'):
            #    while run.status != 'completed':
            #        time.sleep(1)
            #        run = client.beta.threads.runs.retrieve(
            #            thread_id=st.session_state.thread_id,
            #            run_id=run.id
            #        )

            # 'Error Detector Running'
            # runAssistant(errorDetector_id,st.session_state.thread_id,errorDetector_instructions)

            #'Orchestrator Running'
            #st.session_state.run_id
            #runAssistant(assistantOrchestrator.id,st.session_state.thread_id,orchestrator_instructions)

            # messages = client.beta.threads.messages.list(
            #    thread_id=st.session_state.thread_id
            # )

            # # Process and display assistant messages
            # assistant_messages_for_run = [
            #    message for message in messages 
            #    #if message.run_id == run.id and message.role == "assistant"
            #    if message.run_id == st.session_state.run_id and message.role == "assistant"
            # ]
            # 'Message from Error Detector'
            # assistant_messages_for_run

            #for message in assistant_messages_for_run:
            #    error_detected = False
            #    if "E_D" in message.content[0].text.value:
            #        error_detected = True
            ##        'Running Error Response'
            #        runAssistant(assistantErrorResponder.id,st.session_state.thread_id,errorResponder_instructions)
            #    else:
            #        'Running Valid Response'
            #        runAssistant(assistantValidResponder.id,st.session_state.thread_id,validResponder_instructions)
            #st.session_state.run_id

            # 'Responder Running'
            # runAssistant(responder_id,st.session_state.thread_id,errorDetector_instructions)


            # messages = client.beta.threads.messages.list(
            #     thread_id=st.session_state.thread_id
            # )

            # # Process and display assistant messages
            # assistant_messages_for_run = [
            #     message for message in messages 
            #     #if message.run_id == run.id and message.role == "assistant"
            #     if message.run_id == st.session_state.run_id and message.role == "assistant"
            # ]
            # if error_detected is True:
            #     'Message from Error Responder'
            # else:
            #     'Message from Valid Responder'

            # assistant_messages_for_run


            # 'Running Teacher Detector'
            # runAssistant(assistantTeacherDetector.id,st.session_state.thread_id,teacherDetector_instructions)


            # messages = client.beta.threads.messages.list(
            #     thread_id=st.session_state.thread_id
            # )

            # # Process and display assistant messages
            # assistant_messages_for_run = [
            #     message for message in messages 
            #     #if message.run_id == run.id and message.role == "assistant"
            #     if message.run_id == st.session_state.run_id and message.role == "assistant"
            # ]
            # 'Teacher Detector Message'
            # assistant_messages_for_run

            # for message in assistant_messages_for_run:
            #     teacher_detected = False
            #     if "!T_D!" in message.content[0].text.value:
            #         teacher_detected = True
            #         'Running Role Reverser'
            #         runAssistant(assistantErrorResponder.id,st.session_state.thread_id,errorResponder_instructions)





            # #for message in assistant_messages_for_run:
            # #    'Running Simplifier Detector'
            # #    runAssistant(assistantSimplify.id,st.session_state.thread_id,simplify_instructions)

            # messages = client.beta.threads.messages.list(
            #     thread_id=st.session_state.thread_id
            # )

            # assistant_messages_for_run = [
            #     message for message in messages 
            #     #if message.run_id == run.id and message.role == "assistant"
            #     if message.run_id == st.session_state.run_id and message.role == "assistant"
            # ]

            # if teacher_detected:
            #     'Message from Role Reverser'
            # else:
            #     'No Teacher Detected, Original Response'
            
            # assistant_messages_for_run



            #'Responder Running'
            runAssistant(responder_id,st.session_state.thread_id,model_instructions)


            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages 
                #if message.run_id == run.id and message.role == "assistant"
                if message.run_id == st.session_state.run_id and message.role == "assistant"
            ]

           #assistant_messages_for_run

            #'Running Teacher Detector'
           #runAssistant(teacherDetector_id,st.session_state.thread_id,teacherDetector_instructions)

            
            #'Running Role Reverser'
            #runAssistant(roleReverser_id,st.session_state.thread_id,"rewrite the previous message to sound like snoop dogg")

            # messages = client.beta.threads.messages.list(
            #     thread_id=st.session_state.thread_id
            # )

            # # Process and display assistant messages
            # assistant_messages_for_run = [
            #     message for message in messages 
            #     #if message.run_id == run.id and message.role == "assistant"
            #     if message.run_id == st.session_state.run_id and message.role == "assistant"
            # ]

            #assistant_messages_for_run
            
            last_message = assistant_messages_for_run[-1]
            modified_last_message = re.sub(r'<!--.*?-->', '', last_message.content[0].text.value, flags=re.DOTALL)
            st.session_state.messages.append({"role": "assistant", "content": last_message.content[0].text.value})
            
            # Calculate the delay
            words_in_message = len(modified_last_message.split())
            words_per_minute = 100
            #delay = (words_in_message / words_per_minute) * 60 
            #if delay > 20:
            #    delay = random.randint(5, 45)
            #delay
            # Implement the artificial delay
            #for i in range(0,int(delay),10):
            #    with st.spinner('Matlab Tutee is writing...'):
            #        time.sleep(10)
            with st.chat_message("assistant"):
                st.markdown(modified_last_message)


            st.session_state.transcript = ['\n\n--------------------------\n\n'.join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])]
            #st.session_state.transcript

            st.session_state.is_full_transcript = 0
            st.session_state.finish_time = datetime.datetime.now()
            if "messages" in st.session_state:
                #df1 = conn.read(worksheet="Conversations",usecols=list(range(len(allLogColumns)+1))).dropna(how='all')
                #df1 = conn.read("matlabtuteesummer2024_bucket/matlabTuteeSummer2024_Transcripts.csv", input_format="csv", ttl=600)
                df1    = read_csv_from_bucket(bucket_name, file_name)
                df2_data = {}
                for key in allLogColumns:
                    df2_data[key] = st.session_state[key]

                #df2_data

                df2 = pd.DataFrame(df2_data)
                


                #df2 = pd.DataFrame({"Participant ID": st.session_state.participant_id,
                #    "Start": st.session_state.start_time,
                #    "Finish": st.session_state.finish_time,
                #    "Transcript": st.session_state.transcript 
                #    })
                df3 = pd.concat([df1,df2],ignore_index = True)


                #conn.update(worksheet="Conversations",data=df3)
                upload_csv_to_bucket(df3, bucket_name, file_name)

            # for message in assistant_messages_for_run:
            #     #message.content[0].text.value
            #     #remove_triple_quoted_blocks(message.content[0].text.value)
            #     st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            #     with st.chat_message("assistant"):
            #         st.markdown(re.sub(r'<!--.*?-->', '', message.content[0].text.value, flags=re.DOTALL))
    else:
        if st.session_state.has_chatted :
            st.write("Thank you")

            #st.write(":red[Please answer the following questions about your experiencee for this session and press the Submit Answers button afterwards]")

            #st.session_state.post_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how would you rate **:red[your knowledge]** on the topic after this session?",list(range(11)),horizontal=True,index=None)
            #st.session_state.post_tutee_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how much knowledge do you think the **:red[learning partner]** has on the topic after this session?",list(range(11)),horizontal=True,index=None)
            #st.session_state.influence_tutee_knowledge = st.radio("To what extent do you believe your teaching had a positive impact on the **:red[learning partner's]** understanding of the topic?",["Extremely negative","Somewhat negative","Neither positive nor negative","Somewhat positive","Extremely positive"],horizontal=True,index=None)
            #st.session_state.influence_self_knowledge = st.radio("To what extent do you believe your teaching had a positive impact on the **:red[your own]** understanding of the topic?",["Extremely negative","Somewhat negative","Neither positive nor negative","Somewhat positive","Extremely positive"],horizontal=True,index=None)
            #st.session_state.reuse = st.radio("How likely would you continue to interact with this learning partner in the future?",["Extremely unlikely","Somewhat unlikely","Neither likely nor unlikely", "Somewhat likely","Extremely likely"],horizontal=True,index=None)
            

            #st.write(":red[Please rate your impression of the learning partner on these scales]")

            #for k in godSpeed1:
            #    st.session_state[k] = st.radio(godSpeedQuestions1[k],list(range(1,6)),horizontal=True,index=None)

            #st.write(":red[Please rate your emotional state on these scales]")  
            #for k2 in godSpeed2:
            #    st.session_state[k2] = st.radio(godSpeedQuestions2[k2],list(range(1,6)),horizontal=True,index=None)


            
           # st.write(":red[Please respond to each of the questions on the following scale (0 meaning not at all the case and 10 meaning completely the case)]")

            #for c in cogLoad:
            #    st.session_state[c] = st.radio(cogLoadQuestions[c],list(range(1,11)),horizontal=True,index=None)

            #if st.button("Submit Answers"):
                #attributes_to_check = ["post_knowledge",
                #                        "post_tutee_knowledge",
                #                        "influence_tutee_knowledge",
                #                        "influence_self_knowledge",
                #                        "reuse"] + cogLoad
                #if any(getattr(st.session_state, attr, None) is None for attr in attributes_to_check):
                #    st.info("Please fill in all information before submitting")
                #    st.stop()

                # if "messages" in st.session_state:
                #     df1 = conn.read(worksheet="Conversations",usecols=list(range(len(allLogColumns)+1))).dropna(how='all')


                #     df2_data = {}
                #     for key in allLogColumns:
                #         df2_data[key] = st.session_state[key]

                #     #df2_data

                #     df2 = pd.DataFrame(df2_data)
                    


                #     #df2 = pd.DataFrame({"Participant ID": st.session_state.participant_id,
                #     #    "Start": st.session_state.start_time,
                #     #    "Finish": st.session_state.finish_time,
                #     #    "Transcript": st.session_state.transcript 
                #     #    })
                #     df3 = pd.concat([df1,df2],ignore_index = True)


                #     conn.update(worksheet="Conversations",data=df3)
                #     del st.session_state.messages
                
                # st.session_state.thread_id = None
                # for s in setFalse:
                #     st.session_state[s] = False
      
                # for n in setNone:
                #     st.session_state[n] = None
                # st.rerun()

        else:
            if st.button("Start Chat"):
                #if st.session_state.gt_email is None or st.session_state.gt_id is None or st.session_state.topic is None or st.session_state.prior_knowledge is None or st.session_state.prior_tutee_knowledge is None or st.session_state.session_number is None:
                #    st.info("Please fill in all information before starting")
                #    st.stop()
                if st.session_state.gt_email is None or st.session_state.gt_id is None:
                   st.info("Please fill in all information before starting")
                   st.stop()
                st.cache_data.clear()
                st.session_state.start_time = datetime.datetime.now()
                st.session_state.start_chat = True
                st.session_state.has_chatted = True
                thread = client.beta.threads.create()
                print(thread.id)
                st.session_state.thread_id = thread.id
                st.rerun()

else:
        
        st.write("Please click the Start Session Button to begin your session")
        if st.button("Start Session"):
            st.session_state.start_session = True
            st.rerun()
