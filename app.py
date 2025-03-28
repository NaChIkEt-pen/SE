import streamlit as st
import requests
import subprocess
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

    # Ask Question Section
    st.header("Ask Questions")
    text_input = st.text_area("Enter your question here")

    if st.button("Send Question"):
        if text_input.strip():
            query = text_input.strip()
            command = f"python3 rag.py '/home/milind/Downloads/VIT Downloads/Software Engineering/CAT 2' --query \"{query}\" --llm claude"

            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                st.success("Question processed successfully!")
                st.text_area("Response:", result.stdout)
            except Exception as e:
                st.error(f"Error executing the script: {e}")
        else:
            st.warning("Please enter a question.")

    attached_file = st.file_uploader("Attach a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

    if st.button("Send File to Ask Question"):
        if attached_file:
            files = {"file": (attached_file.name, attached_file, attached_file.type)}
            response = requests.post(SERVER_URL, files=files)
            if response.status_code == 200:
                st.success("Question sent successfully!")
            else:
                st.error("Failed to send question!")
        else:
            st.warning("Please attach a file.")

# Check Your Attendance Section
elif menu_option == "Check Your Attendance":
    st.title("Check Your Attendance")

    def get_datetime(date_str: str) -> datetime:
        return datetime.strptime(date_str, "%d-%m-%Y")

    def get_day_of_week(date):
        return date.weekday() + 1  

    def is_working_saturday(date):
        return any(date == ws[0] for ws in working_saturdays)

    def get_timetable_for_date(date):
        day = get_day_of_week(date)
        if day == 6 and is_working_saturday(date):
            return timetable[next(ws[1] for ws in working_saturdays if ws[0] == date)]
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

    def calculate_skippable_classes(total, attended, min_percentage=75):
        if total == 0:
            return 0
        min_classes_needed = math.ceil(total * min_percentage / 100)
        return attended - min_classes_needed

    def format_attendance_report(total_classes, attended_classes, date, is_final=False):
        report = f"\n📅 **Attendance as of {date.strftime('%d-%m-%Y')}:**\n\n"
        
        for subject, total in total_classes.items():
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

    semester_start_date = get_datetime("13-12-2024")
    semester_end_date = get_datetime("17-04-2025")
    cat1_start_date = get_datetime("25-01-2025")
    cat1_end_date = get_datetime("02-02-2025")
    cat2_start_date = get_datetime("16-03-2025")
    cat2_end_date = get_datetime("22-03-2025")

    working_saturdays = [
        (get_datetime("14-12-2024"), 1),
        (get_datetime("21-12-2024"), 2),
        (get_datetime("04-01-2025"), 3),
        (get_datetime("11-01-2025"), 4),
    ]

    holidays = [
        get_datetime("25-12-2024"),
        get_datetime("01-01-2025"),
    ]

    misses = [get_datetime("21-12-2024"), get_datetime("11-01-2025")]

    selected_student = "Ishaan"

    timetables = {
        "Ishaan": {
            1: ["L5+L6", "L5+L6", "A2", "F2", "D2", "B2", "G2"],
            2: ["G1", "B2", "G2", "E2", "C2"],
            3: ["C2", "A2", "F2", "D2"],
            4: ["L19+L20", "L19+L20", "G1", "D2", "B2", "G2", "E2"],
            5: ["E2", "C2", "A2", "F2"],
        }
    }

    timetable = timetables.get(selected_student, {})

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

elif menu_option == "Search for PYQ":
    st.title("Search for PYQ")
    st.write("📌 This section is under development.")
