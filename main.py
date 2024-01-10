import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

session = requests.session()

def published_result():
    url = "https://course.cuet.ac.bd/result_published.php"

    payload = ""
    headers = {}

    response = session.get(url, data=payload, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    assert soup.title is not None, 'Title not found'
    if soup.title.text == "Login To Students Portal":
        # st.write('Your password might be incorrect')
        return []
    
    result_table = soup.find(id="dynamic-table")
    trs = result_table.find_all('tr') # type: ignore
    results = []
    for tr in trs[1:]:
        td = tr.find_all('td')
        
        # Course Details
        code = td[0].text
        credit = td[1].text
        term = td[2].text
        sessional = td[3].text
        result = td[4].text
        course_type = td[5].text
        
        if result != 'F':
            results.append([code, credit, term, sessional, result, course_type])
    
    return results


def login(id, password):
    url = "https://course.cuet.ac.bd/index.php"

    payload = f"user_email={id}&user_password={password}&loginuser=Sign%2BIn"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers"
    }

    session.post(url, data=payload, headers=headers)

    return session.cookies


def show_term_details(current_term, results):
    courses = [course for course in results if course[2] == current_term]
    theory = len([course for course in courses if course[3] == 'No'])
    
    total_credit = sum([float(course[1]) for course in courses])
    # Sum of all credit * gpa
    if total_credit:
        _sum = sum([ (float(course[1]) * float(gpa[f'{course[4]}'])) for course in courses])
        current_gpa = round(_sum/total_credit, 2)
    else:
        current_gpa = 0
        
    data = {
        'Term': current_term,
        'Theory Course': theory,
        'Sessional Course': (len(courses)-theory),
        'Credit': total_credit,
        'GPA': current_gpa
    }
    
    return data

def plot_cgpa(df):
    df['GPA'] = df['GPA'].astype(float)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df['Term'], df['GPA'], marker='o', linestyle='-')
    
    ax.set_xlabel('Term')
    ax.set_ylabel('GPA')
    ax.set_title('GPA vs Term')
    ax.tick_params(axis='x', rotation=45)
    ax.set_yticks([0, 1, 2, 3, 4])

    for i, txt in enumerate(df['GPA']):
        ax.annotate(f'{txt:.2f}', (df['Term'][i], df['GPA'][i]), textcoords="offset points", xytext=(0, 5), ha='center')
    
    st.pyplot(fig)


if __name__ == '__main__':
    gpa = {
        'A+': 4.0,
        'A': 3.75,
        'A-': 3.5,
        'B+': 3.25,
        'B': 3.0,
        'B-': 2.75,
        'C+': 2.5,
        'C': 2.25,
        'D': 2.0,
    }
    
    # Notice
    st.write('### Without IICT permission we are unable to operate this platform.')
    st.write('### We are sorry 😐')

    st.write('##### Wish you a good CGPA 😊')
    st.divider()
    
    submitted = False
    st.write('# CUET CGPA Calculator')
    
    with st.form("my_form"):
        id = st.text_input('Your Student Id:', placeholder='1704123', disabled=True)
        password = st.text_input('Your Student Portal Password:', placeholder='********', disabled=True)
        submitted = st.form_submit_button(label="Submit", disabled=True)
    
    
    if submitted:
        st.write('Fetching your result...')
        login(id, password)
        results = published_result()
        
        
        if results:
            all_term = []
            st.write('Published Result:', len(results))
            cgpa, credit = 0, 0
            for level in range(1, 5):
                for term in range(1, 3):
                    current_term = f'Level {level} - Term {term}'
                    data = show_term_details(current_term, results)
                    cgpa += (data['Credit'] * data['GPA'])
                    credit += data['Credit']
                    all_term.append(data)
            
            df = pd.DataFrame(all_term)
            df['GPA'] = df['GPA'].round(2).astype(str)
            df['Credit'] = df['Credit'].round(2).astype(str)
            
            st.table(df)  

            st.write('\nTotal Credit Completed:', credit)
            if credit:
                st.write(f'### CGPA: {round(cgpa/credit, 2)}')
            st.warning('**CUET student portal may not show all the result. So, the result may not be accurate.**')      
                
            # Plot
            plot_cgpa(df)
            st.balloons()
            
        else:
            st.write('Result Not Found. Id or Password might be incorrect.')
        
    st.divider()
    st.write('##### Developed by [Mohammad Salah Uddin](https://www.facebook.com/salahCuetCse) (1704123)')
    st.write('###### [Contact](mailto:mdsalah.connect@gmail.com)\t[Github](https://github.com/md-Salah/)')
    