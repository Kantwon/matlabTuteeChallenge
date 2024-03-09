from openai import OpenAI
import streamlit as st
import openai
import time
from streamlit_gsheets import GSheetsConnection 
import datetime
import pandas as pd 
import random 



conn = st.connection("gsheets", type=GSheetsConnection)
st.cache_data.clear()
#df1 = conn.read(worksheet="Conversations",usecols=list(range(4))).dropna()
#st.dataframe(df1)

model_instructions = """MATLAB Tutee is a specialized tutor for MATLAB programming, uniquely positioned to always remain in a learner role. 
Starting the conversation, it should ask the human what they would like to teach it today. The tutee is on the RECEVING end of instruction and is not ggiving instruction. 
A good tutee does not teach but instead is instructed. At no point shoudl it ever start giving information. It should always be asking to be taught the information. 
It begins by acting as if it doesn't understand MATLAB, regardless of the accuracy or clarity of student explanations, to encourage students to think critically and explain concepts in depth. 
When a student provides a clear and accurate explanation, MATLAB Tutee acknowledges this, offers praise, and summarizes the concept to reinforce understanding. 
Crucially, if a student is unsure or lacks knowledge, MATLAB tutee never provides answers or enter 'teacher' mode by explaining concepts. 
Instead, it asks probing questions to help the student explore what they do understand, guiding them towards self-discovery and deeper learning. 
If the human says somethihng factually incorrect, the tutee does not correct them directly. 
Instead they come up with questions or examples that then allow the human to figgure out that twhat they said was incorrect. 
The tutee's sole purpose is to facilitate the student's exploration and articulation of MATLAB concepts, fostering a learning environment centered on self-explanation and discovery.
A good tutee never corrects incorrect things from the human. instead they act confused. 
For example, they might say "wait I thought this was how you do that?" or "I think I saw in class that it was done another way?>
Or propose a counter example like <wait so if that way (the incorrect way) makes a vector, then does this other way also make a vector (the correct way)?"
The tutee should always play dumb and act as if it doesn't know the topic. It should only use it's knowledge to ask appropriate questions. 
it should never explain things, it is the human's job to explain things (even if it is wrong). Let them say wrong things. do not correct them.  """

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



assistant_id = "asst_1Wz0ccM8OTfNYwJRbLFL2sVt"

client = openai

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

baseLogColumns = ["gt_email",
                  "gt_id",
              "start_time",
              "finish_time",
              "topic",
              "prior_knowledge",
              "prior_tutee_knowledge",
              "session_number",
              "transcript",
              "post_knowledge",
              "post_tutee_knowledge",
              "influence_tutee_knowledge",
              "influence_self_knowledge",
              "reuse",
              ]

#allLogColumns = baseLogColumns + godSpeed1_keys + godSpeed2_keys + cogLoad_keys
allLogColumns = baseLogColumns + cogLoad_keys

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
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm your Matlab Mentee here to learn Matlab topics from you. What would you like to teach me?"}]


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


if st.session_state.start_session:

    if not st.session_state.start_chat and not st.session_state.has_chatted:
        st.write(":red[Please enter your information below and answer the following questions. Then, click 'Start Chat' to begin.]")

        st.session_state.gt_email = st.text_input('Enter your GT email (ex: krogers34@ gatech.edu)', None)
        st.session_state.gt_id = st.text_input('Enter your GT ID (ex: 903xxxxxxx)', None)

        st.write(":red[Soon you will interact with your learning partner. Please answer the following questions before your session]")
        st.session_state.topic = st.text_input('What topic are you going to teach?', None)
        st.session_state.prior_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how would you rate **:red[your knowledge]** on the topic you are going to teach?",list(range(11)),horizontal=True,index=None)
        st.session_state.prior_tutee_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how much knowledge do you think the **:red[learning partner]** will have on this topic?",list(range(11)),horizontal=True,index=None)
        st.session_state.session_number = st.radio("Which tutoring session is this?",list([1,2,3]),horizontal=True,index=None)
    if st.session_state.start_chat:

        if st.button("Exit Chat"):
            st.session_state.start_chat = False  # Reset the chat state
            st.session_state.finish_time = datetime.datetime.now()
            st.session_state.transcript = [' '.join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])]
            st.rerun()

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
        
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            client.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=prompt
                )
            
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions=model_instructions
            )
            with st.spinner('Thinking and writing response...'):
                while run.status != 'completed':
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages 
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.markdown(message.content[0].text.value)
    else:
        if st.session_state.has_chatted :
            st.write(":red[Please answer the following questions about your experiencee for this session and press the Submit Answers button afterwards]")

            st.session_state.post_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how would you rate **:red[your knowledge]** on the topic after this session?",list(range(11)),horizontal=True,index=None)
            st.session_state.post_tutee_knowledge = st.radio("From 0 (no knowledge) to 10 (expert knowledge), how much knowledge do you think the **:red[learning partner]** has on the topic after this session?",list(range(11)),horizontal=True,index=None)
            st.session_state.influence_tutee_knowledge = st.radio("To what extent do you believe your teaching had a positive impact on the **:red[learning partner's]** understanding of the topic?",["Extremely negative","Somewhat negative","Neither positive nor negative","Somewhat positive","Extremely positive"],horizontal=True,index=None)
            st.session_state.influence_self_knowledge = st.radio("To what extent do you believe your teaching had a positive impact on the **:red[your own]** understanding of the topic?",["Extremely negative","Somewhat negative","Neither positive nor negative","Somewhat positive","Extremely positive"],horizontal=True,index=None)
            st.session_state.reuse = st.radio("How likely would you continue to interact with this learning partner in the future?",["Extremely unlikely","Somewhat unlikely","Neither likely nor unlikely", "Somewhat likely","Extremely likely"],horizontal=True,index=None)
            

            #st.write(":red[Please rate your impression of the learning partner on these scales]")

            #for k in godSpeed1:
            #    st.session_state[k] = st.radio(godSpeedQuestions1[k],list(range(1,6)),horizontal=True,index=None)

            #st.write(":red[Please rate your emotional state on these scales]")  
            #for k2 in godSpeed2:
            #    st.session_state[k2] = st.radio(godSpeedQuestions2[k2],list(range(1,6)),horizontal=True,index=None)


            
            st.write(":red[Please respond to each of the questions on the following scale (0 meaning not at all the case and 10 meaning completely the case)]")

            for c in cogLoad:
                st.session_state[c] = st.radio(cogLoadQuestions[c],list(range(1,11)),horizontal=True,index=None)

            if st.button("Submit Answers"):
                attributes_to_check = ["post_knowledge",
                                        "post_tutee_knowledge",
                                        "influence_tutee_knowledge",
                                        "influence_self_knowledge",
                                        "reuse"] + cogLoad
                if any(getattr(st.session_state, attr, None) is None for attr in attributes_to_check):
                    st.info("Please fill in all information before submitting")
                    st.stop()

                if "messages" in st.session_state:
                    df1 = conn.read(worksheet="Conversations",usecols=list(range(len(allLogColumns)+1))).dropna(how='all')


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



        else:
            if st.button("Start Chat"):
                if st.session_state.gt_email is None or st.session_state.gt_id is None or st.session_state.topic is None or st.session_state.prior_knowledge is None or st.session_state.prior_tutee_knowledge is None or st.session_state.session_number is None:
                    st.info("Please fill in all information before starting")
                    st.stop()
                st.cache_data.clear()
                st.session_state.start_time = datetime.datetime.now()
                st.session_state.start_chat = True
                st.session_state.has_chatted = True
                thread = client.beta.threads.create()
                st.session_state.thread_id = thread.id
                st.rerun()

else:
        st.write("Please click the Start Session Button to begin your session")
        if st.button("Start Session"):
            st.session_state.start_session = True
            st.rerun()
