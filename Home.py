import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import demographics_dict as dd
import json
from typing import List, Dict
import os 

os.environ['AUTOGEN_USE_DOCKER'] = '0'
# Set up the page configuration and styling
st.set_page_config(page_title="Virtual Focus Group", page_icon=":tada:", layout="wide")

# Define a stylized container for the UI elements with customized CSS
with stylable_container(
        key="container_with_border",
        css_styles="""
            {
                border: 2px solid rgba(49, 51, 63, 0.2);
                background-color: lightteal;
                border-radius: 25px;
                padding: calc(1em - 1px);
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
                text-align: center;
            }
            """,
    ):
    # Display header and sub-header
    st.markdown("<h1 style='text-align: center; color: black;'>Build Your Personas</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: grey;'>Select the number of Personas to create, add details, then click Submit Personas.<br><br></h4>", unsafe_allow_html=True)

# Function to save personas data to a JSON file
def save_personas(personas: List[Dict[str, str]]) -> None:
    """Save a list of persona dictionaries to a JSON file."""
    persona_data = {}
    for i, persona in enumerate(personas):
        persona_name = f"Persona {i + 1}"
        persona_data[persona_name] = persona
    with open('docs/personas.json', 'w') as file:
        json.dump(persona_data, file, indent=4)

def main() -> None:
    """Main function to render the Streamlit UI components and handle interactions."""
    col1, col2, col3, col4 = st.columns([.5, 1, .5, .5])
    with col1:
        num_personas = st.slider("Number of Personas to Create: ", min_value=1, max_value=5, step=1, value=1)
    with col2:
        st.empty()
    with stylable_container(
        key="interior_container",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            }
            """,
    ):
        columns = st.columns(num_personas)
        personas = []  # Create an empty list to store the personas
        for persona_id in range(num_personas):
            with columns[persona_id]:
                persona = {
                    "Name": st.text_input(f"Name (Persona {persona_id + 1})", key=f"name_{persona_id}"),
                    "Age": st.selectbox(f"Age (Persona {persona_id + 1})", dd.age_groups, key=f"age_{persona_id}"),
                    "Gender": st.selectbox(f"Gender (Persona {persona_id + 1})", dd.gender_groups, key=f"gender_{persona_id}"),
                    "Location": st.selectbox(f"Geographic Location (Persona {persona_id + 1})", dd.geographic_location, key=f"location_{persona_id}"),
                    "Education": st.selectbox(f"Education Level (Persona {persona_id + 1})", dd.education_levels, key=f"education_{persona_id}"),
                    "Employment": st.selectbox(f"Employment Status (Persona {persona_id + 1})", dd.employment_status, key=f"employment_{persona_id}"),
                    "Income": st.selectbox(f"Income Level (Persona {persona_id + 1})", dd.income_levels, key=f"income_{persona_id}"),
                    "Marital Status": st.selectbox(f"Marital Status (Persona {persona_id + 1})", dd.marital_status, key=f"marital_{persona_id}"),
                    "Children": st.selectbox(f"Number of Children (Persona {persona_id + 1})", dd.number_of_children, key=f"children_{persona_id}"),
                    "Occupation": st.selectbox(f"Occupation (Persona {persona_id + 1})", dd.occupation, key=f"job_{persona_id}"),
                    "Hobbies": st.multiselect(f"Hobbies (Persona {persona_id + 1})", dd.hobbies, key=f"hobby_{persona_id}"),
                    "Backstory": st.text_area(f"Key Traits and Miscellaneous Data:  (Persona {persona_id + 1})", key=f"backstory_{persona_id}")
                }
                personas.append(persona)
    with col3:
        with stylable_container(
            key="green_button",
            css_styles="""
                button {
                    background-color: teal;
                    color: white;
                    box-shadow: 2px 0 7px 0 grey;
                    margin-top: 20px;
                }
                """,
        ):
            if st.button("Submit Personas", key=f"submit_{persona_id}"):
                save_personas(personas)
                st.success(f"Personas {persona_id - 2} - {num_personas} saved successfully!")
    with col4:
        with stylable_container(
            key="green_button",
            css_styles="""
                button {
                    background-color: teal;
                    color: white;
                    box-shadow: 2px 0 7px 0 grey;
                }
                """,
        ):
            launch_focus_group = st.button("Launch Focus Group", key="launch_focus_group")
            if launch_focus_group:
                st.switch_page("pages/1 Run_Virtual_Focus_Group.py")

if __name__ == "__main__":
    main()
