import requests
from bs4 import BeautifulSoup

session = requests.session()

def published_result():
    url = "https://course.cuet.ac.bd/result_published.php"

    payload = ""
    headers = {}

    response = session.get(url, data=payload, headers=headers)

    # print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup.prettify())
    # print(soup.title)
    if soup.title.text == "Login To Students Portal":
        print('Your password might be incorrect')
        return []
    
    result_table = soup.find(id="dynamic-table")
    trs = result_table.find_all('tr')
    # print(trs)
    results = []
    for tr in trs[1:]:
        td = tr.find_all('td')
        # print(td)
        
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
        # "cookie": "PHPSESSID=dfn5555rvm360rae3gov4dvf02",
        "Content-Type": "application/x-www-form-urlencoded",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers"
    }

    response = session.post(url, data=payload, headers=headers)

    # print(response.headers)
    # print(session.cookies)
    # print(response.text)
    return session.cookies


def show_term_details(current_term, results):
    courses = [course for course in results if course[2] == current_term]
    print(f'\n{current_term}:')
    
    theory = len([course for course in courses if course[3] == 'No'])
    print(f'Theory Course: {theory}')
    print(f'Sessional Course: {(len(courses)-theory)}')
    
    total_credit = sum([float(course[1]) for course in courses])
    print(f'Credit: {total_credit}')
    # Sum of all credit * gpa
    if total_credit:
        _sum = sum([ (float(course[1]) * float(gpa[f'{course[4]}'])) for course in courses])
        print(f'GPA: {(current_gpa := round(_sum/total_credit, 2))}')
    else:
        current_gpa = 0
    
    # print(courses)
    return total_credit, current_gpa
    

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
    
    id = input('Id: ')
    password = input('Password: ') or '85745330'
    
    login(id, password)
    results = published_result()
    
    if results:
        print('Published Result:', len(results))
        cgpa, credit = 0, 0
        for level in range(1, 5):
            for term in range(1, 3):
                current_term = f'Level {level} - Term {term}'
                total_credit, current_gpa = show_term_details(current_term, results)
                cgpa += (total_credit * current_gpa)
                credit += total_credit
                
        print('\nTotal Credit Completed:', credit)
        if credit:
            print(f'CGPA: {round(cgpa/credit, 2)}')
    