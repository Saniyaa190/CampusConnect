import os
from datetime import date, time, timedelta, datetime
from PIL import Image, ImageDraw, ImageFont
from app import create_app
from app.extensions import db
from app.models import User, Event, Registration, Notification, EventAttendance

def generate_banner(app_instance, filename, title_text, bg_color1, bg_color2):
    """Generate professional SVG/JPEG banners for sample events."""
    folder = app_instance.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    
    img = Image.new("RGB", (900, 500), color=bg_color1)
    draw = ImageDraw.Draw(img)
    
    # Decorative shapes & gradient accent
    draw.polygon([(0, 380), (900, 240), (900, 500), (0, 500)], fill=bg_color2)
    draw.ellipse([(700, -80), (980, 200)], fill=bg_color2)
    draw.ellipse([(-60, 260), (220, 540)], fill=bg_color1)
    
    # Title rectangle backdrop
    draw.rounded_rectangle([(40, 40), (860, 180)], radius=15, fill=(15, 23, 42, 180))
    
    # Simple clean text banner
    # Center text simulation
    draw.text((70, 75), title_text[:35], fill="#FFFFFF")
    draw.text((70, 115), "CampusConnect College Event Series", fill="#FDE68A")
    
    img.save(file_path, "JPEG", quality=88)


def seed_database():
    app = create_app()
    with app.app_context():
        print("Resetting database schema...")
        db.drop_all()
        db.create_all()

        print("Generating realistic event banner images...")
        banners = [
            ("banner_hackathon.jpg", "Hackathon 2026: Code The Future", "#1E1B4B", "#4338CA"),
            ("banner_techfest.jpg", "TechFest 2026: Innovation Expo", "#312E81", "#7C3AED"),
            ("banner_codesprint.jpg", "CodeSprint: Algorithmic Duel", "#0F172A", "#2563EB"),
            ("banner_cultural.jpg", "Annual Cultural Fest: Waves 2026", "#831843", "#DB2777"),
            ("banner_robotics.jpg", "Robotics & IoT Hands-on Workshop", "#064E3B", "#059669"),
            ("banner_esummit.jpg", "Entrepreneurship & Startup Summit", "#78350F", "#D97706"),
            ("banner_sports.jpg", "Inter-College Sports Championship", "#14532D", "#16A34A"),
            ("banner_ai.jpg", "AI & Machine Learning Seminar", "#1E293B", "#6366F1"),
            ("banner_cyber.jpg", "CyberSecurity & Ethical Hacking", "#111827", "#DC2626"),
            ("banner_dance.jpg", "Inter-Department Dance Battle", "#701A75", "#C026D3"),
            ("banner_badminton.jpg", "Campus Badminton Cup 2026", "#134E4A", "#0D9488"),
            ("banner_cloud.jpg", "Cloud Computing with AWS & GCP", "#172554", "#3B82F6"),
            ("banner_design.jpg", "UI/UX Design Sprint 2026", "#581C87", "#9333EA"),
            ("banner_quiz.jpg", "Mega Campus Trivia Quiz", "#3B0764", "#A855F7"),
            ("banner_music.jpg", "Acoustic Night & Battle of Bands", "#4C1D95", "#8B5CF6"),
            ("banner_datascience.jpg", "Data Science & Kaggle Bootcamp", "#0F766E", "#14B8A6")
        ]

        for fname, title, c1, c2 in banners:
            generate_banner(app, fname, title, c1, c2)

        print("Creating User Accounts...")
        # 1 Demo Admin
        admin = User(
            name="College Admin",
            email="admin@campusconnect.edu",
            role="admin",
            department="Academic Administration",
            year="Faculty / Staff"
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

        # 3 Demo Organizers
        org1 = User(
            name="Tech & Innovation Club",
            email="techclub@campusconnect.edu",
            role="organizer",
            department="Computer Science & Engineering",
            year="Faculty / Staff"
        )
        org1.set_password("Organizer@123")

        org2 = User(
            name="Cultural & Arts Society",
            email="cultural@campusconnect.edu",
            role="organizer",
            department="Applied Sciences & Humanities",
            year="Faculty / Staff"
        )
        org2.set_password("Organizer@123")

        org3 = User(
            name="Athletics & Sports Board",
            email="sports@campusconnect.edu",
            role="organizer",
            department="Electronics & Communication",
            year="Faculty / Staff"
        )
        org3.set_password("Organizer@123")

        db.session.add_all([org1, org2, org3])
        db.session.flush()

        # 12 Demo Students
        students_data = [
            ("Aarav Sharma", "aarav.sharma@campusconnect.edu", "Computer Science & Engineering", "3rd Year"),
            ("Diya Patel", "diya.patel@campusconnect.edu", "Information Technology", "2nd Year"),
            ("Rohan Verma", "rohan.verma@campusconnect.edu", "Electronics & Communication", "4th Year"),
            ("Ananya Iyer", "ananya.iyer@campusconnect.edu", "Computer Science & Engineering", "1st Year"),
            ("Kabir Singh", "kabir.singh@campusconnect.edu", "Mechanical Engineering", "3rd Year"),
            ("Sneha Gupta", "sneha.gupta@campusconnect.edu", "Civil Engineering", "2nd Year"),
            ("Vikram Malhotra", "vikram.malhotra@campusconnect.edu", "Business Administration (MBA/BBA)", "Postgraduate"),
            ("Pooja Reddy", "pooja.reddy@campusconnect.edu", "Computer Science & Engineering", "4th Year"),
            ("Aditya Nair", "aditya.nair@campusconnect.edu", "Information Technology", "3rd Year"),
            ("Rhea Sen", "rhea.sen@campusconnect.edu", "Electronics & Communication", "2nd Year"),
            ("Ishaan Joshi", "ishaan.joshi@campusconnect.edu", "Electrical Engineering", "1st Year"),
            ("Tanvi Deshmukh", "tanvi.deshmukh@campusconnect.edu", "Computer Science & Engineering", "3rd Year")
        ]

        students = []
        for name, email, dept, year in students_data:
            s = User(
                name=name,
                email=email,
                role="student",
                department=dept,
                year=year
            )
            s.set_password("Student@123")
            students.append(s)
            db.session.add(s)

        db.session.flush()

        print("Creating Sample Events across categories...")
        today = date.today()

        sample_events = [
            {
                "title": "Hackathon 2026: 36-Hour National Code Sprint",
                "category": "Technical",
                "description": "Join the premier collegiate hackathon! Teams of 2 to 4 build impactful software prototypes in Web3, Generative AI, Cloud Infrastructure, and Smart Campus solutions. Mentorship from industry engineers, food, swag, and cash prizes of ₹1,00,000 for winning teams.",
                "event_date": today + timedelta(days=12),
                "start_time": time(9, 0),
                "end_time": time(21, 0),
                "venue": "Campus Innovation Center, Hall A",
                "capacity": 120,
                "registration_deadline": today + timedelta(days=9),
                "eligibility": "Open to all engineering & polytechnic students",
                "contact_email": "hackathon@campusconnect.edu",
                "image": "banner_hackathon.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            {
                "title": "TechFest 2026: Annual Technology Exhibition",
                "category": "Technical",
                "description": "Showcase of final-year hardware and software innovations. Featuring drone demonstrations, autonomous robotics arena, AR/VR displays, and keynote tech leadership panels.",
                "event_date": today + timedelta(days=18),
                "start_time": time(10, 0),
                "end_time": time(18, 0),
                "venue": "Main College Auditorium & Quadrangle",
                "capacity": 250,
                "registration_deadline": today + timedelta(days=15),
                "eligibility": "All college students and faculty members",
                "contact_email": "techfest@campusconnect.edu",
                "image": "banner_techfest.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            {
                "title": "CodeSprint: Speed Algorithm Challenge",
                "category": "Competitions",
                "description": "Test your algorithmic problem solving, dynamic programming, and data structure speed. Live leaderboard powered contest consisting of 6 challenging algorithmic puzzles.",
                "event_date": today + timedelta(days=7),
                "start_time": time(14, 0),
                "end_time": time(17, 30),
                "venue": "Computer Science Lab 301",
                "capacity": 60,
                "registration_deadline": today + timedelta(days=5),
                "eligibility": "Open to all branches",
                "contact_email": "codesprint@campusconnect.edu",
                "image": "banner_codesprint.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            {
                "title": "Annual Cultural Fest: Waves 2026",
                "category": "Cultural",
                "description": "The largest cultural extravaganza of the academic calendar! Live musical performances, pro-nite concerts, art galleries, drama skits, fashion showcase, and carnival food stalls.",
                "event_date": today + timedelta(days=25),
                "start_time": time(16, 0),
                "end_time": time(22, 0),
                "venue": "Campus Central Grounds & Open Amphitheater",
                "capacity": 500,
                "registration_deadline": today + timedelta(days=20),
                "eligibility": "All enrolled college students",
                "contact_email": "culturalfest@campusconnect.edu",
                "image": "banner_cultural.jpg",
                "organizer_id": org2.id,
                "approval_status": "approved"
            },
            {
                "title": "Robotics & Microcontroller Workshop",
                "category": "Workshops",
                "description": "Comprehensive hands-on workshop building ESP32, Arduino, and sensor-driven obstacle avoidance robots. All hardware kits provided for team experimentation during the lab session.",
                "event_date": today + timedelta(days=10),
                "start_time": time(10, 0),
                "end_time": time(16, 0),
                "venue": "Mechatronics Lab, Mechanical Block",
                "capacity": 45,
                "registration_deadline": today + timedelta(days=8),
                "eligibility": "1st to 3rd year students",
                "contact_email": "robotics@campusconnect.edu",
                "image": "banner_robotics.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            {
                "title": "Entrepreneurship Summit: Pitch The Idea",
                "category": "Competitions",
                "description": "Got an innovative startup idea? Pitch in front of venture capitalists, angel investors, and seasoned campus alumni founders. Cash grants and incubation support for top 3 startup pitches.",
                "event_date": today + timedelta(days=21),
                "start_time": time(11, 0),
                "end_time": time(17, 0),
                "venue": "Seminar Hall B, Management Block",
                "capacity": 100,
                "registration_deadline": today + timedelta(days=16),
                "eligibility": "Students of any branch with a business proposal",
                "contact_email": "esummit@campusconnect.edu",
                "image": "banner_esummit.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            {
                "title": "Annual Inter-College Sports Championship",
                "category": "Sports",
                "description": "Multi-sport athletic festival including Football tournament, Basketball, 100m sprint, Relay races, and Volleyball matches. Trophies and certificates for best athletic performance.",
                "event_date": today + timedelta(days=14),
                "start_time": time(8, 30),
                "end_time": time(18, 0),
                "venue": "College Sports Complex & Football Stadium",
                "capacity": 200,
                "registration_deadline": today + timedelta(days=11),
                "eligibility": "All college athletes and fitness enthusiasts",
                "contact_email": "sports@campusconnect.edu",
                "image": "banner_sports.jpg",
                "organizer_id": org3.id,
                "approval_status": "approved"
            },
            {
                "title": "AI and Machine Learning Seminar",
                "category": "Seminars",
                "description": "Distinguished lecture series on Modern LLM architectures, Diffusion Models, and AI Ethics delivered by leading research scientists and industry experts from leading AI labs.",
                "event_date": today + timedelta(days=6),
                "start_time": time(13, 0),
                "end_time": time(16, 0),
                "venue": "Aryabhatta Conference Hall",
                "capacity": 150,
                "registration_deadline": today + timedelta(days=4),
                "eligibility": "All branches and semesters",
                "contact_email": "aiseminar@campusconnect.edu",
                "image": "banner_ai.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            {
                "title": "CyberSecurity Bootcamp: Capture The Flag (CTF)",
                "category": "Competitions",
                "description": "Intense ethical hacking challenges in web vulnerabilities, cryptography, reverse engineering, and digital forensics. Beginners and experienced cybersecurity students welcome.",
                "event_date": today + timedelta(days=15),
                "start_time": time(14, 0),
                "end_time": time(19, 0),
                "venue": "IT Systems Lab 2",
                "capacity": 50,
                "registration_deadline": today + timedelta(days=13),
                "eligibility": "Computer Science & IT students",
                "contact_email": "cyberclub@campusconnect.edu",
                "image": "banner_cyber.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            {
                "title": "Campus Badminton Cup 2026",
                "category": "Sports",
                "description": "Singles and doubles knockout tournament for men and women. Yonex shuttlecocks provided. Matches held under indoor stadium court floodlights.",
                "event_date": today + timedelta(days=9),
                "start_time": time(15, 0),
                "end_time": time(19, 30),
                "venue": "Indoor Badminton Arena",
                "capacity": 32,
                "registration_deadline": today + timedelta(days=6),
                "eligibility": "Open to all students",
                "contact_email": "badminton@campusconnect.edu",
                "image": "banner_badminton.jpg",
                "organizer_id": org3.id,
                "approval_status": "approved"
            },
            {
                "title": "Battle of the Bands & Acoustic Jam",
                "category": "Cultural",
                "description": "Showcase of rock bands, classical fusion, vocal soloists, and beatboxers. Professional sound setup with campus cheering audience.",
                "event_date": today + timedelta(days=22),
                "start_time": time(17, 0),
                "end_time": time(21, 30),
                "venue": "College Amphitheater",
                "capacity": 300,
                "registration_deadline": today + timedelta(days=19),
                "eligibility": "Singers, musicians, and live band performers",
                "contact_email": "musicclub@campusconnect.edu",
                "image": "banner_music.jpg",
                "organizer_id": org2.id,
                "approval_status": "approved"
            },
            {
                "title": "UI/UX Design Sprint & Figma Masterclass",
                "category": "Workshops",
                "description": "Learn modern web design systems, interactive prototyping, user journey mapping, and usability testing using Figma. Includes guided mini project building.",
                "event_date": today + timedelta(days=11),
                "start_time": time(11, 0),
                "end_time": time(15, 0),
                "venue": "Multimedia Center, Block D",
                "capacity": 50,
                "registration_deadline": today + timedelta(days=9),
                "eligibility": "Designers and aspiring developers",
                "contact_email": "design@campusconnect.edu",
                "image": "banner_design.jpg",
                "organizer_id": org2.id,
                "approval_status": "approved"
            },
            {
                "title": "Cloud Computing Architecture with AWS",
                "category": "Workshops",
                "description": "Practical deployment workshop covering EC2, S3, Serverless Lambda functions, and CI/CD pipelines. AWS promotional credits provided to each participant.",
                "event_date": today + timedelta(days=16),
                "start_time": time(10, 0),
                "end_time": time(14, 0),
                "venue": "Cloud Computing Center",
                "capacity": 70,
                "registration_deadline": today + timedelta(days=14),
                "eligibility": "Basic knowledge of Linux commands",
                "contact_email": "cloud@campusconnect.edu",
                "image": "banner_cloud.jpg",
                "organizer_id": org1.id,
                "approval_status": "approved"
            },
            # Pending Event for Admin Review
            {
                "title": "Quantum Computing & Quantum Algorithms Seminar",
                "category": "Seminars",
                "description": "Deep-dive seminar introducing Qiskit, superposition, quantum key distribution, and future cryptography implications with invited university scholars.",
                "event_date": today + timedelta(days=28),
                "start_time": time(14, 0),
                "end_time": time(17, 0),
                "venue": "Physics Research Hall",
                "capacity": 80,
                "registration_deadline": today + timedelta(days=24),
                "eligibility": "Open to all students",
                "contact_email": "quantum@campusconnect.edu",
                "image": "banner_ai.jpg",
                "organizer_id": org1.id,
                "approval_status": "pending"
            },
            # Another Pending Event for Admin Review
            {
                "title": "College Chess Grand Championship 2026",
                "category": "Sports",
                "description": "FIDE rapid rules chess tournament. 5 rounds swiss format with classical time controls. Clocks and boards provided.",
                "event_date": today + timedelta(days=17),
                "start_time": time(9, 30),
                "end_time": time(16, 30),
                "venue": "Student Lounge, Activity Center",
                "capacity": 40,
                "registration_deadline": today + timedelta(days=15),
                "eligibility": "All chess players",
                "contact_email": "chess@campusconnect.edu",
                "image": "banner_sports.jpg",
                "organizer_id": org3.id,
                "approval_status": "pending"
            },
            # Past Event for History & Completed Events check
            {
                "title": "Orientation & Freshers Welcome Fest 2026",
                "category": "Cultural",
                "description": "Campus orientation program for the incoming freshman class, club showcases, senior-junior interaction, and cultural dance showcase.",
                "event_date": today - timedelta(days=14),
                "start_time": time(10, 0),
                "end_time": time(16, 0),
                "venue": "Main College Auditorium",
                "capacity": 400,
                "registration_deadline": today - timedelta(days=18),
                "eligibility": "First year students",
                "contact_email": "orientation@campusconnect.edu",
                "image": "banner_cultural.jpg",
                "organizer_id": org2.id,
                "approval_status": "approved"
            }
        ]

        created_events = []
        for edata in sample_events:
            ev = Event(**edata)
            created_events.append(ev)
            db.session.add(ev)

        db.session.flush()

        print("Creating Sample Registrations & Attendances...")
        # Add diverse registrations for student accounts across the created events
        # Student 0 (Aarav): registered for Hackathon, AI Seminar, Past orientation
        # Student 1 (Diya): registered for Hackathon, CodeSprint, UI/UX
        # Student 2 (Rohan): registered for TechFest, Sports championship, Orientation
        # etc.
        sample_regs = [
            (students[0], created_events[0], "confirmed", "not_attended"), # Aarav -> Hackathon
            (students[0], created_events[7], "confirmed", "not_attended"), # Aarav -> AI Seminar
            (students[0], created_events[15], "confirmed", "attended"),    # Aarav -> Orientation (Past, Attended)
            
            (students[1], created_events[0], "confirmed", "not_attended"), # Diya -> Hackathon
            (students[1], created_events[2], "confirmed", "not_attended"), # Diya -> CodeSprint
            (students[1], created_events[11], "confirmed", "not_attended"),# Diya -> UI/UX
            
            (students[2], created_events[1], "confirmed", "not_attended"), # Rohan -> TechFest
            (students[2], created_events[6], "confirmed", "not_attended"), # Rohan -> Sports
            (students[2], created_events[15], "confirmed", "attended"),    # Rohan -> Orientation
            
            (students[3], created_events[0], "confirmed", "not_attended"), # Ananya -> Hackathon
            (students[3], created_events[4], "confirmed", "not_attended"), # Ananya -> Robotics
            (students[3], created_events[7], "confirmed", "not_attended"), # Ananya -> AI Seminar
            
            (students[4], created_events[4], "confirmed", "not_attended"), # Kabir -> Robotics
            (students[4], created_events[6], "confirmed", "not_attended"), # Kabir -> Sports
            
            (students[5], created_events[3], "confirmed", "not_attended"), # Sneha -> Cultural Fest
            (students[5], created_events[9], "confirmed", "not_attended"), # Sneha -> Badminton
            
            (students[6], created_events[5], "confirmed", "not_attended"), # Vikram -> E-Summit
            (students[6], created_events[7], "confirmed", "not_attended"), # Vikram -> AI Seminar
            
            (students[7], created_events[0], "confirmed", "not_attended"), # Pooja -> Hackathon
            (students[7], created_events[8], "confirmed", "not_attended"), # Pooja -> CyberSecurity
            
            (students[8], created_events[1], "confirmed", "not_attended"), # Aditya -> TechFest
            (students[8], created_events[2], "confirmed", "not_attended"), # Aditya -> CodeSprint
            
            (students[9], created_events[3], "confirmed", "not_attended"), # Rhea -> Cultural Fest
            (students[9], created_events[10], "confirmed", "not_attended"),# Rhea -> Battle of Bands
            
            (students[10], created_events[6], "confirmed", "not_attended"),# Ishaan -> Sports
            (students[11], created_events[0], "confirmed", "not_attended"),# Tanvi -> Hackathon
            (students[11], created_events[12], "confirmed", "not_attended")# Tanvi -> AWS Cloud
        ]

        for student_obj, event_obj, reg_status, att_status in sample_regs:
            reg = Registration(
                student_id=student_obj.id,
                event_id=event_obj.id,
                registration_status=reg_status,
                attendance_status=att_status,
                registration_date=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(reg)
            
            if att_status == "attended":
                att = EventAttendance(
                    event_id=event_obj.id,
                    student_id=student_obj.id,
                    marked_by=event_obj.organizer_id,
                    marked_at=datetime.utcnow() - timedelta(days=14)
                )
                db.session.add(att)

        print("Generating Realistic Notifications...")
        # Notifications for Admin
        db.session.add(Notification(
            user_id=admin.id,
            title="Pending Event Approval Required",
            message="Organizer 'Tech & Innovation Club' submitted 'Quantum Computing & Quantum Algorithms Seminar'. Please review and take action.",
            created_at=datetime.utcnow() - timedelta(hours=2)
        ))
        db.session.add(Notification(
            user_id=admin.id,
            title="Pending Event Approval Required",
            message="Organizer 'Athletics & Sports Board' submitted 'College Chess Grand Championship 2026'. Awaiting review.",
            created_at=datetime.utcnow() - timedelta(hours=4)
        ))

        # Notifications for Organizers
        db.session.add(Notification(
            user_id=org1.id,
            title="Event Approved!",
            message="Your event 'Hackathon 2026: 36-Hour National Code Sprint' has been approved by admin and is now live on the campus catalog.",
            is_read=True,
            created_at=datetime.utcnow() - timedelta(days=1)
        ))
        db.session.add(Notification(
            user_id=org1.id,
            title="New Student Registration",
            message="Aarav Sharma (Computer Science & Engineering, 3rd Year) registered for 'Hackathon 2026'.",
            is_read=False,
            created_at=datetime.utcnow() - timedelta(hours=6)
        ))
        db.session.add(Notification(
            user_id=org2.id,
            title="Event Approved!",
            message="Your event 'Annual Cultural Fest: Waves 2026' has been approved by college administration.",
            is_read=True,
            created_at=datetime.utcnow() - timedelta(days=2)
        ))

        # Notifications for Students
        for s in students[:3]:
            db.session.add(Notification(
                user_id=s.id,
                title="Registration Confirmed!",
                message="You have secured your seat for 'Hackathon 2026'. Don't forget to review the rules and bring your college ID card.",
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=8)
            ))
            db.session.add(Notification(
                user_id=s.id,
                title="Welcome to CampusConnect!",
                message="Explore verified hackathons, cultural festivals, sports cups, and workshops happening on campus.",
                is_read=True,
                created_at=datetime.utcnow() - timedelta(days=5)
            ))

        db.session.commit()
        print("\nDatabase seeded successfully!")
        print("="*60)
        print("DEMO CREDENTIALS:")
        print("1. Admin:")
        print("   Email:    admin@campusconnect.edu")
        print("   Password: Admin@123")
        print("\n2. Organizers:")
        print("   Email:    techclub@campusconnect.edu")
        print("   Password: Organizer@123")
        print("   Email:    cultural@campusconnect.edu")
        print("   Password: Organizer@123")
        print("   Email:    sports@campusconnect.edu")
        print("   Password: Organizer@123")
        print("\n3. Students:")
        print("   Email:    aarav.sharma@campusconnect.edu")
        print("   Password: Student@123")
        print("   Email:    diya.patel@campusconnect.edu")
        print("   Password: Student@123")
        print("="*60)

if __name__ == "__main__":
    seed_database()
