# 🚀 Quick Start Guide

## Academic Management System (BIMA) - Get Started in 5 Minutes

---

## ⚡ Fast Setup

### **1. Prerequisites Check**
```bash
python --version        # Should be 3.8+
pip --version          # Should be present
mysql --version        # Should be 5.7+
```

### **2. Install Dependencies**
```bash
cd "v:\MCA 3rd sem\CMP\Mini-Project"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### **3. Configure Database**
```bash
# Create .env file with these credentials:
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=SriVishnu@143
DB_NAME=bima
SECRET_KEY=your-secret-key

# Import database schema:
mysql -u root -p bima < schema_academic.sql
```

### **4. Run Application**
```bash
python app.py
```

✅ **Application Running at:** http://127.0.0.1:5000

---

## 👤 Test Accounts

### **Admin Login**
- **ID:** admin_id
- **Password:** admin_password
*(Set during initial setup)*

### **Test Student**
- **ID:** SBIMAMCA007
- **Password:** Test@123

### **Test Teacher**
- **ID:** T12345
- **Password:** Teacher@123

---

## 📱 Key Features Quick Tour

### **Student Features**
1. 📊 **Dashboard** - View total marks and grades
   - Route: `/student_dashboard`
   
2. 📈 **Performance** - Track marks across semesters
   - Route: `/student_performance`
   
3. 📥 **Download Reports** - PDF & Excel exports
   - PDF: `/report_pdf/<student_id>`
   - Excel: `/report_excel/<student_id>`

4. 🔐 **Forgot Password** - OTP-verified reset
   - Route: `/forgot_password`

### **Teacher Features**
1. 👥 **Manage Marks** - Input student marks
   - Route: `/add_marks`
   
2. 📊 **View Students** - Assigned class students
   - Route: `/students`
   
3. 📥 **Download Reports** - PDF & Excel
   - Route: `/teacher_report/<teacher_id>`

### **Admin Features**
1. 🏛️ **System Management** - Users, subjects, classes
2. 📊 **Analytics** - System-wide insights
3. 📥 **Bulk Exports** - Student list exports

---

## 🔑 Common Tasks

### **Register a New Student**
```
1. Admin Dashboard → Add Student
2. Fill form with details
3. Upload photo
4. Select subjects
5. System generates Student ID
6. Share credentials with student
```

### **Enter Marks for Students**
```
1. Teacher Login → Add Marks
2. Select subject and exam
3. Enter marks for each student
4. Submit
```

### **Reset Forgotten Password**
```
1. Login Page → Forgot Password
2. Enter registered phone number
3. Copy OTP shown on page
4. Enter OTP
5. Set new password
6. Login with new password
```

### **Download Performance Report**
```
1. Student Dashboard → Download PDF/Excel
OR
2. Admin Views Student → Download PDF/Excel
```

---

## ⚙️ Configuration Tips

### **Change Database**
Edit `app.py` line 40-46:
```python
def get_db():
    return mysql.connector.connect(
        host="YOUR_HOST",
        user="YOUR_USER",
        password="YOUR_PASSWORD",
        database="YOUR_DB",
        port=3306,
    )
```

### **Change Port**
Edit `app.py` last line:
```python
app.run(debug=True, port=8000)  # Change 8000 to your port
```

### **Enable/Disable Debug**
```python
app.run(debug=False)  # Set False for production
```

---

## 🐛 Common Issues & Fixes

### **Error: "Port 5000 already in use"**
```bash
# Kill process on Windows
taskkill /PID <PID> /F

# Or run on different port
# Edit app.py: app.run(port=5001)
```

### **Error: "MySQL Connection Failed"**
```
1. Check MySQL is running: mysql -u root -p
2. Verify credentials in .env
3. Verify database exists: SHOW DATABASES;
```

### **Error: "OTP not showing"**
```
1. Check you're on /verify_otp page
2. Verify server is running (see console)
3. OTP shown in blue box on page
```

### **Error: "No module named X"**
```bash
pip install -r requirements.txt
```

---

## 📊 Verify Installation

Run this checklist:

```
✅ Python installed (3.8+)
✅ Dependencies installed: pip list | grep Flask
✅ MySQL running: mysql -u root -p
✅ Database created: SHOW DATABASES; (shows 'bima')
✅ Schema imported: SHOW TABLES; (shows 12+ tables)
✅ .env file exists with correct credentials
✅ app.py runs without errors
✅ http://127.0.0.1:5000 opens in browser
✅ Can access Login page
✅ Can register as student
✅ Can login with credentials
```

---

## 📁 File Structure Overview

```
Mini-Project/
├── app.py                  # Main application (3100+ lines)
├── requirements.txt        # Dependencies to install
├── schema_academic.sql    # Database schema (import this)
├── .env                   # Configuration (create this)
├── README.md              # Full documentation
├── CODE_REVIEW_REPORT.md  # Quality report
├── static/                # CSS, JS, uploads
└── templates/             # HTML pages
```

---

## 🎯 Next Steps

1. ✅ **Complete Setup** - Follow installation steps above
2. 📚 **Read Full Documentation** - See README.md for complete guide
3. 🧪 **Test Features** - Try login, marks, exports
4. 🔐 **Test Password Reset** - Verify OTP flow
5. 📥 **Test Exports** - Download PDF and Excel
6. 📖 **Review Code** - Check CODE_REVIEW_REPORT.md
7. 🚀 **Deploy** - Ready for production!

---

## 📞 Need Help?

1. **Check Troubleshooting** - README.md → Troubleshooting section
2. **Check Logs** - Look at console output when app runs
3. **Read Code Comments** - app.py has inline documentation
4. **Check Database** - Verify tables exist: `SHOW TABLES;`

---

## ✅ You're Ready!

Your Academic Management System is now set up and ready to use!

**Next:** Open your browser and navigate to:
```
http://127.0.0.1:5000
```

**Enjoy!** 🎉

---

*For detailed information, see README.md*
*For code quality details, see CODE_REVIEW_REPORT.md*
