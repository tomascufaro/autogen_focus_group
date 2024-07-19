import os
import json
import streamlit as st
from typing import Optional, Dict, Any
from autogen import GroupChat, Agent, AssistantAgent, UserProxyAgent, config_list_from_json, GroupChatManager
from streamlit_extras.stylable_container import stylable_container


# Setup LLM model and API keys
os.environ["OAI_CONFIG_LIST"] = json.dumps([
    {
        'model': 'gpt-3.5-turbo',
        'api_key': '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',
    }
])

# Setting configurations for autogen
config_list = config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": {
            "gpt-3.5-turbo"
        }
    }
)

# Define the LLM configuration settings
llm_config = {
    "cache_seed": None,
    "temperature": 0.5,
    "config_list": config_list,
}

summary_agent_prompt = """
    You are an expert reasearcher in behaviour science and are tasked with summarising a reasearch panel. Please provide a structured summary of the key findings, including pain points, preferences, and suggestions for improvement.
    This should be in the format based on the following format:

    ```
    Reasearch Study: <<Title>>

    Subjects:
    <<Overview of the subjects and number, any other key information>>

    Summary:
    <<Summary of the study, include detailed analysis as an export>>

    Pain Points:
    - <<List of Pain Points - Be as clear and prescriptive as required. I expect detailed response that can be used by the brand directly to make changes. Give a short paragraph per pain point.>>

    Suggestions/Actions:
    - <<List of Adctions - Be as clear and prescriptive as required. I expect detailed response that can be used by the brand directly to make changes. Give a short paragraph per reccomendation.>>
    ```
    """


class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)

class TrackableGroupChatManager(GroupChatManager):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


def generate_notice(role: str = "researcher", base_notice: Optional[str] = None) -> str:
    """
    Generates a notice message based on the role.

    Parameters:
        role (str): The role of the agent.
        base_notice (Optional[str]): The base notice message.

    Returns:
        str: The generated notice message.
    """
    if base_notice is None:
        base_notice = (
            'You are part of a research panel to gather relevant information of a new product that our client is launching. We appreciate your collaboration.'
        )

    non_persona_notice = (
        'Do not show appreciation in your responses, say only what is necessary. '
        'If "Thank you" or "You\'re welcome" are said in the conversation, then say TERMINATE '
        'to indicate the conversation is finished and this is your last message.'
    )

    persona_notice = (
        ' Act as {role} when responding to queries, providing feedback, asked for your personal opinion '
        'or participating in discussions.'
    )

    if role.lower() in ["manager", "researcher"]:
        return base_notice + non_persona_notice
    else:
        return base_notice + persona_notice.format(role=role)


def custom_speaker_selection(last_speaker: Optional[Agent], group_chat: GroupChat) -> Optional[Agent]:
    """
    Custom function to ensure the Researcher interacts with each participant 2-3 times.
    Alternates between the Researcher and participants, tracking interactions.
    """
    # Define participants and initialize or update their interaction counters
    if not hasattr(group_chat, 'interaction_counters'):
        group_chat.interaction_counters = {agent.name: 0 for agent in group_chat.agents if agent.name != "Researcher"}
    # Define a maximum number of interactions per participant
    max_interactions = 6
    # If the last speaker was the Researcher, find the next participant who has spoken the least
    if last_speaker and last_speaker.name == "Researcher":
        next_participant = min(group_chat.interaction_counters, key=group_chat.interaction_counters.get)
        if group_chat.interaction_counters[next_participant] < max_interactions:
            group_chat.interaction_counters[next_participant] += 1
            return next((agent for agent in group_chat.agents if agent.name == next_participant), None)
        else:
            return None  # End the conversation if all participants have reached the maximum interactions
    else:
        # If the last speaker was a participant, return the Researcher for the next turn
        return next((agent for agent in group_chat.agents if agent.name == "Researcher"), None)
    

# Create the research assistant panel
def create_research_panel() -> None:
    consumer_profiles = [
        {
            "name": "Emily_Johnson",
            "role": "teenager",
            "system_message": """You are Emily Johnson, a 17-year-old high school student living in Los Angeles, California. 
                                You are tech-savvy and follow the latest fashion trends. Your annual allowance is $1,200. 
                                Provide feedback on how the products align with current youth trends and your personal style."""+ generate_notice("Emily_Johnson"),
            "human_input_mode":'NEVER'
        },
        {
            "name": "Michael_Thompson",
            "role": "young_adult",
            "system_message": """You are Michael Thompson, a 28-year-old software engineer living in Austin, Texas. 
                                You value affordable yet stylish clothing and have an annual salary of $85,000. 
                                Provide insights into how the products fit into your professional and casual wardrobe."""+ generate_notice("Michael_Thompson"),
            "human_input_mode":'NEVER'
        },
        {
            "name": "Sarah_Williams",
            "role": "parent",
            "system_message": """You are Sarah Williams, a 35-year-old mother of two living in Chicago, Illinois. 
            You work as a marketing manager with an annual salary of $70,000. You are looking for durable, affordable, and stylish clothing for your family. 
            Share your thoughts on the product's quality, affordability, and suitability for family needs."""+ generate_notice("Sarah_Williams"),
            "human_input_mode":'NEVER'
        },
        {
            "name": "Robert_Brown",
            "role": "senior",
            "system_message": """You are Robert Brown, a 65-year-old retired teacher living in Miami, Florida. 
                                You have an annual pension income of $50,000. You value comfort and classic styles.
                                Provide feedback on the comfort, quality, and style of the products and how they meet your needs."""+ generate_notice("Robert_Brown"),
            "human_input_mode":'NEVER'
        },
        {
            "name": "Researcher",
            "role": "Researcher",
            "system_message": """Researcher. You are a top product reasearcher with a Phd in behavioural psychology and have worked in the research and 
                                insights industry for the last 20 years with top creative, media and business consultancies. Your role is to ask questions about products and 
                                gather insights from individual customers like Emily. Frame questions to uncover customer preferences, challenges, and feedback. 
                                Before you start the task breakdown the list of panelists and the order you want them to speak, avoid the panelists speaking with each other and creating comfirmation bias.
                                If the session is terminating at the end, please provide a summary of the outcomes of the reasearch study in clear concise notes not at the start.""" + generate_notice("Researcher"),
            "human_input_mode":'NEVER'
        }
    ]
    assistant_agents = []
    for profile in consumer_profiles:
        agent = TrackableAssistantAgent(
            name=profile["name"],
            llm_config=llm_config,
            system_message=profile["system_message"],
            human_input_mode=profile["human_input_mode"]  # Ensure the agent asks for human input
        )
        assistant_agents.append(agent)
    for agent in assistant_agents:
        print(f"Created agent: {agent.name}")
    return assistant_agents


# Adding the Researcher and Customer Persona agents to the group chat
def create_group_chat(agents:list, custom_selection):
    groupchat = GroupChat(
        agents=agents,
        speaker_selection_method = custom_selection,
        messages=[],
        max_round=30)
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = TrackableUserProxyAgent(
        name="user_proxy",
        code_execution_config={"last_n_messages": 2, "work_dir": "groupchat", 'use_docker':False},
        system_message="A human admin.",
        human_input_mode="NEVER"
    )
        # Initialise the manager
    manager = TrackableGroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        system_message="You are a reasearch manager agent that can manage a group chat of multiple agents made up of a reasearcher agent and many people made up of a panel. You will limit the discussion between the panelists and help the researcher in asking the questions. Please ask the researcher first on how they want to conduct the panel." + generate_notice(),
        is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
    )
    return groupchat, user_proxy, manager


def summarization_agent(summary_prompt:str=summary_agent_prompt):
    # Get response from the groupchat for user prompt
    
    # Generate system prompt for the summary agent
    summary_agent = TrackableAssistantAgent(
        name="SummaryAgent",
        llm_config=llm_config,
        system_message=summary_prompt + generate_notice(),
    )
    summary_proxy = TrackableUserProxyAgent(
        name="summary_proxy",
        code_execution_config={"last_n_messages": 2, "work_dir": "groupchat", 'use_docker':False},
        system_message="A human admin.",
        human_input_mode="TERMINATE"
    )
    return summary_agent, summary_proxy


# Example usage
if __name__ == "__main__":
    # Create the research panel
    assistant_agents = create_research_panel()    
    #create group chat
    groupchat, user_proxy, manager = create_group_chat(assistant_agents, custom_speaker_selection)

        # Initiate the chat
    # start the reasearch simulation by giving instruction to the manager
    user_proxy.initiate_chat(
        manager,
        message="""
    Gather customer insights on a costumer interest in a big clothes brand. Identify pain points, preferences, and suggestions for improvement from different customer personas. Could you all please give your own personal oponions before sharing more with the group and discussing. As a reasearcher your job is to ensure that you gather unbiased information from the participants and provide a summary of the outcomes of this study back to the super market brand.
    """)


    #create summary workflow
    messages = [msg["content"] for msg in groupchat.messages if msg['name'] != 'Researcher']
    user_prompt = "Here is the transcript of the study ```{customer_insights}```".format(customer_insights="\n>>>\n".join(messages))
    summary_agent, summary_proxy = summarization_agent()

    # Initiate the summarize workflow
    summary_proxy.initiate_chat(
        summary_agent,
        message=user_prompt,
        )

    # Create the summary agent
    print(f"Created summary agent: {summary_agent.name}")
