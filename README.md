**Chordloid**
Chordloid is a cloud-based chord finder web application built using Flask, PostgreSQL, Docker, and AWS services.

Users can search for musical chords, view the notes that make up each chord, and save custom chord progressions using user accounts.

**Features:**
- User registration and login
- Password hashing using bcrypt
- Chord note generation
- Piano roll visualization
- Saved chord progressions
- Delete saved progressions
- PostgreSQL database integration
- Dockerized Flask backend
- AWS deployment support

**Technologies Used:**

Frontend:
- HTML
- CSS
- JavaScript
- 
Backend:
- Flask
- Python

Database:
- PostgreSQL (AWS RDS)
  
Cloud/Deployment
- AWS EC2
- AWS RDS
- AWS S3
- Docker


**How It Works:**

Users create an account or log in.
The frontend sends requests to the Flask backend.
Flask processes the request and queries the PostgreSQL database.
The backend returns the chord data to the frontend.
Notes are displayed visually on the piano roll.
Users can save chords into custom progressions.

**Database Tables:**

The application uses several PostgreSQL tables:
- users
- chords
- chord_notes
- progressions
- progression_chords
  
These tables store user accounts, chord data, and saved progressions.

**Running Locally**
1. Clone the repository
git clone <repo-url>
cd <repo-name>

2. Create a virtual environment
python -m venv venv

Activate it:
macOS/Linux
source venv/bin/activate

Windows
venv\Scripts\activate


3. Install dependencies
pip install -r requirements.txt


4. Configure environment variables
Create a .env file:
DB_HOST=your-host
DB_NAME=your-db-name
DB_USER=your-user
DB_PASSWORD=your-password
DB_PORT=5432


5. Initialize the database
python db_init.py


6. Run the application
python app.py

The app should now be running at:
http://127.0.0.1:5000

**Docker**
To build the Docker container:
docker build -t chordloid .

To run the container:
docker run -p 5000:5000 chordloid

**Future Improvements**
Audio playback for chords
Better mobile responsiveness
Expanded chord library
Improved progression editing
Rate limiting

**Authors**
Diego Mariscal
Maxwell Juanengo
