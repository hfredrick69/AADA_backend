from database import SessionLocal
from models import ExternshipStatus

# 🔧 Change this line to the desired status:
new_status = "Completed"  # Options: "Not Started", "In Progress", "Completed"

# Connect to DB
db = SessionLocal()

# Update or insert status for student_id=1
status = db.query(ExternshipStatus).filter_by(student_id=1).first()
if status:
    status.status = new_status
    print(f"Updated student 1 to '{new_status}'")
else:
    status = ExternshipStatus(student_id=1, status=new_status)
    db.add(status)
    print(f"Inserted new status '{new_status}' for student 1")

db.commit()
db.close()
