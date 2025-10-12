# 🏆 Sports Team Management

A web-based system designed to help manage sports teams, players, and matches efficiently.  
This project simplifies organizing players, creating teams, scheduling matches, and tracking results — providing coaches and administrators with an all-in-one management platform.

---

## 🚀 Features (Planned)
- Coach registration and profile management  
- Team creation and management  
- Match scheduling and results tracking  
- Admin and coach dashboards  
- Authentication (login/logout system)

---

## 🛠 Tech Stack

**Backend:** Python (Django)  
**Frontend:** HTML, CSS  
**Database:** Supabase  
**Version Control:** Git & GitHub  
**Deployment (Planned):** Heroku / Vercel / AWS  

---

## 👨‍💻 Team Members

| Name | Role | CIT-U Email |
|------|------|--------------|
| **Frances Lghe Unabia** | Developer | frances.unabia@cit.edu |
| **Riggy Maryl Yungco** | Developer | riggy.yungco@cit.edu |
| **Serge Ylan Soldano** | Developer | serge.soldano@cit.edu |
| **Christian Kyle Tapales** | Product Owner | christiankyle.tapales@cit.edu |
| **Jhon Nichole Brosas Tampos** | Scrum Master | jhonnichole.tampos@cit.edu |
| **Arcelyn Silvano Tequillo** | Business Analyst | arcelyn.tequillo@cit.edu |

---

## ⚙️ Setup & Run Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/christian-tapales/CSIT327-G8-SportsTeamManagement.git
cd CSIT327-G8-SportsTeamManagement

### 2️⃣ Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Mac/Linux

### 3️⃣ Install project dependencies
pip install -r requirements.txt

### 4️⃣ Create a .env file (if not yet existing)
# Add your Supabase or PostgreSQL credentials, e.g.:
DATABASE_URL=postgresql://username:password@host:port/dbname
SECRET_KEY=your_django_secret_key

### 5️⃣ Apply database migrations
python manage.py migrate

### 6️⃣ Run the development server
python manage.py runserver

### 7️⃣ Open your browser and go to:
http://127.0.0.1:8000/