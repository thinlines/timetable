# School Timetabling System

## Project Overview

This is a timetabling system designed for an international A-Level school with grades 10-12. The system automates the complex process of scheduling courses, teachers, and students while respecting various constraints and preferences.

## School Context

**Academic Structure:**
- International A-Level curriculum (students need 5 A-grades to matriculate)
- Grades 10-12 (approximately 30-40 students total in college-prep program)
- 10-15 teachers, mix of international and local staff
- 5-day week schedule with 9 periods per day (8 on Friday)
- 18-21 weeks per term

**Daily Schedule:**
- Morning study hour: 7:30-7:55 AM
- 9 regular periods: 40 minutes each with 10-minute breaks
- Special events: Monday flag ceremony (8:50 AM), Friday homeroom meeting (4:00-4:30 PM)
- Lunch break: 11:40-1:30 PM
- Evening study hours: 6:30-9:00 PM
- Friday ends one period early

**Key Constraints:**
- Students grouped by homeroom by default, split only when necessary
- Teachers have 24-period weekly limit (most use much less)
- International teachers cannot teach first or last periods
- Class size maximum: 24 students
- Electives typically scheduled in last two periods (4:10-5:40 PM)
- Some courses benefit from consecutive 90-minute double periods

## Database Schema

Refer to schema.SQL for a description of the database schema.

### Core Tables

**students**
- Basic student information
- Links to homeroom
- Grade level (10, 11, 12)

**teachers**
- Teacher information with international flag
- Department associations (JSONB)
- Period preferences and availability (JSONB)
- Contractual hour limits

**courses**
- Course details with periods per week requirement
- Mandatory/elective flags
- Grade level eligibility (JSONB)
- Facility requirements

**homerooms**
- Physical homeroom spaces
- Grade level association
- Capacity limits

**facilities**
- Labs, gyms, courts, fields
- Capacity and splitting capabilities
- Facility type categorization

### Scheduling Tables

**time_periods**
- Defines the weekly schedule structure
- Handles Monday's different pattern and Friday's early dismissal
- Special event periods (ceremonies, meetings)

**class_sections**
- Groups students into teachable class sizes
- Links courses to specific sections

**scheduled_classes**
- The actual timetable: links sections, teachers, facilities, and time slots
- Handles consecutive period requirements
- Semester-specific scheduling

**class_enrollments**
- Student enrollment in specific scheduled classes

### Association Tables

**teacher_courses** - Which teachers can teach which courses
**student_courses** - Which courses each student is taking
**study_hour_assignments** - Study hall supervision assignments

## Design Principles

### Simplicity Over Complexity
- **Uniform Course Treatment**: Different course levels (e.g., "Chemistry A" vs "Chemistry B") are separate course entities rather than variants of one course
- **No Special A/B Logic**: The scheduling algorithm treats all courses identically
- **Standard Relational Design**: Avoids complex hierarchies or special-case logic

### Constraint Satisfaction Approach
The timetabling problem is essentially a constraint satisfaction problem (CSP) with:

**Hard Constraints:**
- Teacher availability and hour limits
- Facility capacity and conflicts  
- Student course requirements
- International teacher time restrictions

**Soft Constraints (Preferences):**
- Keep homeroom classmates together
- Teacher preferred time slots
- Consecutive periods for specific courses
- Elective scheduling in preferred slots

### Flexible Data Model
- **JSONB Usage**: For arrays and structured data (teacher departments, grade levels, preferences)
- **Semester Support**: All scheduling tables are semester-aware
- **Extensible Constraints**: Generic constraint storage for future requirements

## Technical Stack

**Database**: PostgreSQL with JSONB for structured data
**Application**: Python-based (framework TBD - likely Flask/FastAPI for web, tkinter/PyQt for desktop)
**Algorithm**: Constraint satisfaction with optimization libraries (likely OR-Tools or similar)

## Current Development Status

✅ **Completed:**
- Database schema design and validation
- Sample data structure with real school data
- Core entity relationships established

🔄 **In Progress:**
- Data population scripts
- Basic application architecture planning

📋 **Planned:**
- Constraint satisfaction algorithm implementation  
- Web interface development
- Report generation (individual schedules, master timetable)
- Export capabilities (CSV, PDF, HTML)

## Key Stakeholders

**Primary Users:**
- Scheduling administrator (main user)
- Teachers (schedule viewing)
- Students (schedule viewing)

**Export Requirements:**
- Individual teacher schedules
- Individual student schedules  
- Master administrative timetable
- Multiple formats: spreadsheet, CSV, HTML, PDF

## Sample Data Context

The system includes real sample data representing:
- 13 teachers (mix of international/local, various departments)
- ~18 courses across subjects like Chemistry, Physics, Math, English, Chinese, Art, PE
- Variable course loads (1-6 periods per week)
- Grade-specific course requirements
- Specialized facilities (labs, gym, courts, field)

## Scheduling Complexity

**Teacher Switching Pattern**: Some leveled courses require teachers to alternate between student groups across periods to ensure all students receive required instruction.

**Facility Management**: Limited specialized spaces (5 small rooms, labs, gym, outdoor facilities) require careful coordination.

**Mixed Grade Classes**: Some courses can accommodate multiple grade levels, adding flexibility but complexity to grouping.

**International Constraints**: Approximately 40% of teachers are international with specific availability restrictions.

This system replaces a manual spreadsheet-based scheduling process and aims to optimize both educational outcomes and administrative efficiency while maintaining the flexibility needed for a small international school environment.