import streamlit as st
import requests

# Set the FastAPI endpoint
API_ENDPOINT = st.secrets["api_endpoint"]
AUTH_TOKEN = st.secrets["auth_token"]
ANKER_URL = "https://uni-tuebingen.de/de/257900"

# Streamlit Interface
def main():
    st.title("AI Guidelines Guru v0.1")

    st.markdown(f"""
    Dieses Tool wurde im Rahmen des Projekts [**ANKER**]({ANKER_URL}) am Internationalen Zentrum für Ethik in den Wissenschaften an der Universität Tübingen entwickelt und steht zur Zeit als Prototyp zur Verfügung.
    
    ### Funktionen
    - Durchsucht den Inhalt von über **200 Ethikrichtlinien und -frameworks**.
    - Bietet eine automatisch generierte Volltextantwort auf gestellte Fragen.
    - Stellt die relevantesten Quellen mit Metadaten bereit.
    
    ### Hinweise
    - Fragen müssen in der aktuellen Version **in englischer Sprache** formuliert werden.
    - Klicken Sie auf **"View Snippet"** unter den Quellen, um die ausgewählten Textausschnitte einzusehen. 
    - Textausschnitte sind aktuell für den prototypischen Anwendungsfall absichtlich kurz gehalten.
    - **Confidence Level:** Testweise enthält jede Antwort eine Einschätzung darüber, wie gut die gefundenen Textausschnitte die Antwort stützen:
        - **High:** Die Dokumente enthalten die Informationen explizit und umfassend.
        - **Medium:** Informationen sind unvollständig oder erfordern logische Schlussfolgerungen.
        - **Low:** Der Kontext ist unzureichend oder unpassend.
    """, unsafe_allow_html=True)

    
    # Input field for the search query
    query = st.text_input("Enter your search query here:")
    
    # Search button
    if st.button("Search"):
        if query:
            # Display the loading spinner
            with st.spinner("Searching..."):
                # Send the query to the FastAPI backend
                headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
                payload = {"question": query}
                response = requests.post(API_ENDPOINT, json=payload, headers=headers)
                
                # Check the response status
                if response.status_code == 200:
                    results = response.json()
                    print(results)
                    display_results(results)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
        else:
            st.warning("Please enter a search query.")


# def display_results(results):
#     # Display each result
#     st.subheader(f"Answer")
#     st.write(results["result"]["answer"])
#     context = results["result"]["context"]
#     for i, source in enumerate(context):
#         metadata = source["metadata"]
#         st.write(f"**Source {i}: {metadata['document_name']}** \nURL:{metadata['document_url'] if 'document_url' in metadata else 'N/A'} \t Page:{metadata['page'] if 'page' in metadata else 'N/A'}")
#         st.write("---")

def display_results(results):
    st.divider()
    
    # Use columns for layout: answer on the left, sources on the right
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Answer")
        st.info(results["answer"])
    
    with col2:
        st.subheader("Sources")
        if results["answer"] == "The answer is not available.":
            st.write("No sources found.")
        else:
            context = results["documents"]
            for i, source in enumerate(context):
                metadata = source["metadata"]
                pub_year = metadata.get('year_of_publication') or 'N/A'
                document_url = metadata.get('document_url', 'N/A')

                with st.container(border=True):
                    st.markdown(f"**Source {i + 1}:** {metadata['document_name']}")
                    st.markdown(f"**Institution:** {metadata['institution']}")
                    st.markdown(f"**Year:** {pub_year}")
                    
                    if document_url != 'N/A':
                        st.markdown(f"**URL:** [Link]({document_url})")
                    else:
                        st.markdown("**URL:** N/A")
                        
                    st.markdown(f"**Page:** {metadata.get('page', 'N/A')}")
                    
                    # Using popover for the source snippet to replace the hover help
                    with st.popover("View Snippet"):
                        st.caption("Relevant excerpt from the document:")
                        st.write(source["page_content"])
                


if __name__ == "__main__":
    main()