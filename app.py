import json
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from pathlib import Path
import streamlit_authenticator as stauth

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define user credentials
usernames = ["admin","shrestha"]
names = ["Admin", "Shrestha"]
passwords = ["admin123", "sasha"]

# Correctly format the credentials dictionary
credentials = {
    "usernames": {
        username: {
            "name": name,
            "password": password
        }
        for username, name, password in zip(usernames, names, passwords)
    }
}

# Initialize Authenticate
authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="usernames_dashboard",
    cookie_key="abcdef",
    cookie_expiry_days=30
)

# Streamlit login logic
login_fields = {
    "username": "Username",
    "password": "Password"
}
name, authentication_status, username = authenticator.login(fields=login_fields)

if authentication_status is False:
    st.error("Username/password is incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:
    # This function takes in a string of input text and uses the Gemini-PRO model
    # from the Google Generative AI API to generate a response based on that input.
    # It returns the response as a string.
    def get_gemini_response(input_text):
        # Create a new instance of the Gemini-PRO model from the Google Generative AI API.
        # The 'gemini-pro' string is the model ID.
        model = genai.GenerativeModel('gemini-pro')

        # Use the model to generate content based on the input text.
        # The 'generate_content' method takes in the input text and returns a response object.
        # We're interested in the 'text' attribute of the response object, so we access it using
        # the '.text' property.
        response = model.generate_content(input_text)

        # Return the response as a string.
        return response.text

    def input_pdf_text(uploaded_file):
        """
        This function takes in a file object representing a PDF file and extracts the text
        from all the pages in the PDF. It returns the extracted text as a single string.

        Parameters:
            uploaded_file (file): A file object representing a PDF file.

        Returns:
            str: The extracted text from all the pages in the PDF file.
        """
        # Create a PdfReader object from the uploaded file.
        # The PdfReader class from the PyPDF2 library is used to read PDF files.
        # It takes in a file object as its argument.
        reader = pdf.PdfReader(uploaded_file)
        
        # Initialize an empty string to store the extracted text.
        # This string will be populated with the text extracted from each page in the PDF.
        text = ""
        
        # Iterate over each page in the PDF.
        # The 'pages' attribute of the PdfReader object returns an iterator that yields each page in the PDF.
        for page in reader.pages:
            # Extract the text from the current page and append it to the text string.
            # The 'extract_text' method of the Page object from the PyPDF2 library is used to extract the text from a single page.
            # It returns a string containing the extracted text.
            text += page.extract_text()
        
        # Return the extracted text as a single string.
        # This string will be used as input to the Google Generative AI API to generate a response.
        return text

    def load_history():
        """
        This function loads the chat history from a JSON file.
        If the file does not exist, it returns an empty list.

        Returns:
            list: A list of tuples representing the chat history.
                  Each tuple contains the company name, job role, and response dictionary.
                  The response dictionary contains the JD Match percentage, missing keywords, and profile summary.
        """
        # Check if the file exists
        # We're using the 'os.path.exists()' function to check if the 'chat_history.json' file exists.
        # This function returns 'True' if the file exists and 'False' otherwise.
        if os.path.exists("chat_history.json"):
            # If the file exists, we open it and read its contents.
            # We're using a 'with' statement to open the file. This ensures that the file is properly closed after it is no longer needed.
            with open("chat_history.json", "r") as file:
                # We're using the 'json.load()' function to parse the JSON data from the file and return it as a Python object.
                # The 'json.load()' function takes in a file object as its argument and reads the contents of the file.
                # It expects the contents of the file to be in JSON format and returns a Python object that represents the data in the file.
                # In this case, we're returning the contents of the 'chat_history.json' file as a Python object.
                return json.load(file)
        # If the file does not exist, we return an empty list.
        # This indicates that there is no chat history to load.
        return []

    def save_history(history):
        """
        This function saves the chat history to a JSON file.
        
        Args:
            history (list): A list of tuples representing the chat history.
                            Each tuple contains the company name, job role, and response dictionary.
                            The response dictionary contains the JD Match percentage, missing keywords, and profile summary.
                            
        Returns:
            None
        """
        
        # Open the 'chat_history.json' file in write mode and create a file object.
        # We're using the 'open()' function with the 'w' mode to open the file in write mode.
        # The 'with' statement is used to ensure that the file is properly closed after it is no longer needed.
        # This ensures that the file is properly closed after it is no longer needed.
        with open("chat_history.json", "w") as file:
            # Use the 'json.dump()' function to serialize the chat history Python object into a JSON string.
            # The 'json.dump()' function takes in two arguments: the Python object to serialize (in this case, the 'history' list)
            # and the file object to write the serialized JSON string to (in this case, the 'file' object).
            # The serialized JSON string is then written to the file object.
            json.dump(history, file)

    def display_percentage_circle(percentage):
        # Calculate the radius and circumference of the circle
        radius = 50  # The radius of the circle
        circumference = 2 * 3.14159 * radius  # The circumference of the circle
        
        # Calculate the progress of the circle based on the percentage
        progress = int(circumference * (percentage / 100))  # The progress of the circle
        
        # Determine the color of the circle based on the percentage
        if percentage < 10:
            color = "#e74c3c"  # Red
        elif percentage < 50:
            color = "#f39c12"  # Orange
        elif percentage < 90:
            color = "#2ecc71"  # Green
        else:
            color = "#3498db"  # Blue
        
        # Generate the HTML code for the circle and percentage text
        html_code = f"""
            <svg width="120" height="120">  # The SVG element with a width and height of 120 pixels
            <circle cx="60" cy="60" r="50" stroke="#ccc" stroke-width="10" fill="transparent"/>  # The background circle
            <circle cx="60" cy="60" r="50" stroke="{color}" stroke-width="10" fill="transparent"  # The progress circle
                stroke-dasharray="{circumference}" stroke-dashoffset="{circumference - progress}"/>  # The progress of the circle
            <text x="50%" y="50%" text-anchor="middle" alignment-baseline="middle" font-size="20" fill="{color}">{percentage}%</text>  # The percentage text
            </svg>
        """
        
        # Return the generated HTML code
        return html_code

    input_prompt_template = """
    Hey Act Like a skilled or very experienced ATS(Application Tracking System)
    with a deep understanding of tech field, software engineering, data science, data analyst,
    and big data engineer. Your task is to evaluate the resume based on the given job description.
    You must consider the job market is very competitive and you should provide 
    best assistance for improving the resumes. Assign the percentage matching based 
    on the JD and
    the missing keywords with high accuracy.
    resume: {resume_text}
    company_name: {company_name}
    job_role: {job_role}

    I want the response in one single string having the structure
    {{"JD Match":"%", "MissingKeywords":[], "Profile Summary":""}}
    """

    # Streamlit app
    st.title("Application Tracking System (ATS)")
    st.subheader("Improve your Resume's ATS")
    company_name = st.text_input("Enter Company Name")
    job_role = st.text_input("Enter Job Role")
    jd = st.text_area("Paste the Job Description")
    st.subheader("Upload Your Resume")
    uploaded_file = st.file_uploader("PDF file only", type="pdf", help="Please Upload Your Resume in PDF file")
    submit = st.button("Submit")

    # Load history
    if 'history' not in st.session_state:
        st.session_state.history = load_history()

    # Sidebar for chat history
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome, {name}")
    st.sidebar.text("Developed By: Shrestha Raj")
    st.sidebar.subheader("Chat History")
    for i, (company_name_hist, job_role_hist, response_dict) in enumerate(st.session_state.history):
        if st.sidebar.button(f"{company_name_hist} - {job_role_hist}", key=f"history_button_{i}"):
            # Display the selected chat history
            st.subheader("Job Description Match:")
            st.write(f"**{response_dict['JD Match']}**")
            
            # Display percentage circle below the Job Description Match heading
            if 'JD Match' in response_dict and response_dict['JD Match']:
                try:
                    progress_percent = float(response_dict['JD Match'].strip('%'))
                    st.subheader("Job Description Match Progress:")
                    st.markdown(display_percentage_circle(progress_percent), unsafe_allow_html=True)
                except ValueError:
                    st.error("Error: JD Match percentage format is invalid.")
            
            st.subheader("Missing Keywords:")
            st.write(", ".join(response_dict["MissingKeywords"]))
            
            st.subheader("Profile Summary:")
            st.write(response_dict["Profile Summary"])

    if submit:
        if uploaded_file is not None:
            resume_text = input_pdf_text(uploaded_file)
            input_prompt = input_prompt_template.format(resume_text=resume_text, company_name=company_name, job_role=job_role)
            response = get_gemini_response(input_prompt)
            
            try:
                response_dict = json.loads(response)
            except json.JSONDecodeError:
                st.error("Error: Invalid response format from the generative AI.")
                response_dict = {"JD Match": "Error", "MissingKeywords": [], "Profile Summary": ""}
            
            # Add the current chat to the history
            st.session_state.history.append((company_name, job_role, response_dict))
            save_history(st.session_state.history)
            
            # Display the response
            if 'JD Match' in response_dict and response_dict['JD Match']:
                st.subheader("Job Description Match:")
                st.write(f"**{response_dict['JD Match']}**")
                
                # Display dynamic progress circle for JD Match below the Job Description Match heading
                try:
                    progress_percent = float(response_dict['JD Match'].strip('%'))
                    st.subheader("Job Description Match Progress:")
                    st.markdown(display_percentage_circle(progress_percent), unsafe_allow_html=True)
                except ValueError:
                    st.error("Error: JD Match percentage format is invalid.")

                st.subheader("Missing Keywords:")
                st.write(", ".join(response_dict["MissingKeywords"]))
                
                st.subheader("Profile Summary:")
                st.write(response_dict["Profile Summary"])
                
            else:
                st.error("Error: No valid response received from the generative AI.")
