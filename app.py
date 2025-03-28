import streamlit as st
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import math

# Placeholder for server URL (Replace with actual URL)
SERVER_URL = "http://localhost:3000/upload"

st.set_page_config(page_title="Student Portal", layout="wide")

# Sidebar Menu
st.sidebar.title("Navigation")
menu_option = st.sidebar.radio("Go to", ["Ask Questions", "Check Your Attendance", "Search for PYQ"])

# Ask Questions Section
if menu_option == "Ask Questions":
    # File Upload Section
    st.header("Upload Files")
    uploaded_files = st.file_uploader("Choose multiple files", accept_multiple_files=True)

    if st.button("Send Files"):
        if uploaded_files:
            files = [("files", (file.name, file, file.type)) for file in uploaded_files]
            response = requests.post(SERVER_URL, files=files)
            if response.status_code == 200:
                st.success("Files sent successfully!")
            else:
                st.error("Failed to send files!")
        else:
            st.warning("Please upload at least one file.")

    # Text Input Section with File Upload (Ask Question)
    st.header("Ask Questions")
    text_input = st.text_area("Enter your question here")
    if st.button("Send Question"):
        if text_input.strip():
            data = {"text": text_input}
            response = requests.post(SERVER_URL, data=data, files=files)
            if response.status_code == 200:
                st.success("Question sent successfully!")
            else:
                st.error("Failed to send question!")
        else:
            st.warning("Please enter a question")
    attached_file = st.file_uploader("Attach a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

    
    if st.button("Send File to Ask Question"):
        if attached_file:
            files = {"file": (attached_file.name, attached_file, attached_file.type)} if attached_file else None
            response = requests.post(SERVER_URL, files=files)
            if response.status_code == 200:
                st.success("Question sent successfully!")
            else:
                st.error("Failed to send question!")
        else:
            st.warning("Please attach a file.")

# Check Your Attendance Section (Placeholder)
elif menu_option == "Check Your Attendance":
    st.title("Check Your Attendance")
    # st.write("📌 This section is under development. You can add your attendance checking code here.")
    import streamlit as st
    from datetime import datetime, timedelta
    from collections import defaultdict
    import math

    # Function Definitions (Use your existing functions here)
    def get_datetime(date_str: str) -> datetime:
        return datetime.strptime(date_str, "%d-%m-%Y")

    def get_day_of_week(date):
        return date.weekday() + 1  # 1 for Monday, 2 for Tuesday, etc.

    def is_working_saturday(date):
        return any(date == ws[0] for ws in working_satudays)

    def get_timetable_for_date(date):
        day = get_day_of_week(date)
        if day == 6 and is_working_saturday(date):
            return timetable[next(ws[1] for ws in working_satudays if ws[0] == date)]
        elif day <= 5:
            return timetable[day]
        return []

    def calculate_attendance(start_date, end_date):
        total_classes = defaultdict(int)
        attended_classes = defaultdict(int)
        current_date = start_date

        while current_date <= end_date:
            if current_date not in holidays and not (cat1_start_date <= current_date <= cat1_end_date) and not (cat2_start_date <= current_date <= cat2_end_date):
                classes = get_timetable_for_date(current_date)
                for subject in classes:
                    total_classes[subject] += 1
                    if current_date not in misses:
                        attended_classes[subject] += 1
            
            current_date += timedelta(days=1)
        
        return total_classes, attended_classes

    def is_lab_subject(subject):
        return ('+' in subject and subject.startswith('L')) or 'lab' in subject.lower()

    def calculate_skippable_classes(total, attended, min_percentage=75):
        if total == 0:
            return 0
        min_classes_needed = math.ceil(total * min_percentage / 100)
        return attended - min_classes_needed

    def format_attendance_report(total_classes, attended_classes, date, is_final=False):
        report = f"\n📅 **Attendance as of {date.strftime('%d-%m-%Y')}:**\n\n"
        
        for subject, total in total_classes.items():
            if not is_final and is_lab_subject(subject):
                continue
                
            attended = attended_classes[subject]
            percentage = (attended / total) * 100 if total > 0 else 0
            skippable = calculate_skippable_classes(total, attended)
            
            attendance_str = f"🔹 **{subject}**: {attended}/{total} (**{percentage:.2f}%**)"
            
            if skippable < 0:
                attendance_str += f" ⚠️ **WARNING: DEBARRED** (Need {abs(skippable)} more classes for 75%)"
            else:
                attendance_str += f" ✅ ({skippable} classes can be skipped)"
            
            report += attendance_str + "\n\n"
        
        return report

    # Semester Details
    semester_start_date = get_datetime("13-12-2024")
    semester_end_date = get_datetime("17-04-2025")
    cat1_start_date = get_datetime("25-01-2025")
    cat1_end_date = get_datetime("02-02-2025")
    cat2_start_date = get_datetime("16-03-2025")
    cat2_end_date = get_datetime("22-03-2025")

    working_satudays = [
        (get_datetime("14-12-2024"), 1),
        (get_datetime("21-12-2024"), 2),
        (get_datetime("04-01-2025"), 3),
        (get_datetime("11-01-2025"), 4),
        (get_datetime("25-01-2025"), 5),
        (get_datetime("15-02-2025"), 1),
        (get_datetime("01-03-2025"), 2),
        (get_datetime("08-03-2025"), 3),
        (get_datetime("29-03-2025"), 4),
        (get_datetime("05-04-2025"), 5),
        (get_datetime("12-04-2025"), 2),
    ]

    holidays = [
        *[get_datetime(f"{day}-12-2024") for day in range(22, 32)], 
        get_datetime("01-01-2025"),
        *[get_datetime(f"{day}-01-2025") for day in range(14, 18)],
        get_datetime("11-02-2025"),
        get_datetime("20-02-2025"), get_datetime("21-02-2025"), 
        get_datetime("22-02-2025"), get_datetime("23-02-2025"),
        get_datetime("14-03-2025"),
        get_datetime("31-03-2025"),
    ]

    misses = [
        get_datetime("21-12-2024"),
        get_datetime("11-01-2025"),
        get_datetime("13-01-2025"),
        get_datetime("20-01-2025"),
    ]

    # Streamlit UI
    st.title("Student Attendance Tracker")

    # Select Student
    # student_names = ["Ishaan", "Kevin", "Essu", "Singh", "Milind"]
    selected_student = "Ishaan"
    # selected_student = st.selectbox("", student_names)

    # Student Timetables
    timetables = {
        "Ishaan": {
            1: ["L5+L6", "L5+L6", "A2", "F2", "D2", "B2", "G2"],
            2: ["G1", "B2", "G2", "E2", "C2"],
            3: ["C2", "A2", "F2", "D2"],
            4: ["L19+L20", "L19+L20", "G1", "D2", "B2", "G2", "E2"],
            5: ["E2", "C2", "A2", "F2"],
        },
        "Kevin": {
            1: ["A1", "D1", "G1", "L33+L34", "L33+L34"],
            2: ["B1", "G1", "E1", "C1", "L39+L40", "L39+L40"],
            3: ["C1", "A1", "L43+L44", "L43+L44"],
            4: ["D1", "B1", "G1", "E1", "L51+L52", "L51+L52"],
            5: ["E1", "C1"],
        },
    }

    timetable = timetables.get(selected_student, {})

    # Attendance Calculation
    if st.button("Check Attendance"):
        total_classes_cat1, attended_classes_cat1 = calculate_attendance(semester_start_date, cat1_start_date - timedelta(days=1))
        total_classes_cat2, attended_classes_cat2 = calculate_attendance(semester_start_date, cat2_start_date - timedelta(days=1))
        total_classes_final, attended_classes_final = calculate_attendance(semester_start_date, semester_end_date)

        st.subheader("📊 Attendance Summary")
        st.markdown("### 📅 Before CAT1:")
        st.markdown(format_attendance_report(total_classes_cat1, attended_classes_cat1, cat1_start_date - timedelta(days=1)))

        st.markdown("### 📅 Before CAT2:")
        st.markdown(format_attendance_report(total_classes_cat2, attended_classes_cat2, cat2_start_date - timedelta(days=1)))

        st.markdown("### 📅 Final Attendance:")
        st.markdown(format_attendance_report(total_classes_final, attended_classes_final, semester_end_date, is_final=True))

# Search for PYQ Section (Placeholder)
elif menu_option == "Search for PYQ":
    st.title("Search for PYQ")
    st.write("📌 This section is under development. You can add your PYQ searching code here.")
