# Timetable System Project Specification

## Project Overview
Let's lay out the groundwork for a comprehensive timetable management system for a Chinese K-12 school to replace their current manual, spreadsheet-based scheduling system. The system should handle complex scheduling constraints across multiple departments with different educational tracks.

## School Structure
- **Primary School (PS)**: Grades 1-6
- **Junior High (JH)**: Grades 7-9 (compulsory education)
- **Senior High (SH)**: Grades 10-12
  - **International Track**: British A Level system, IGCSE compressed to 1 year (Grade 10)
  - **National Track**: Gaokao-focused curriculum

## Technical Requirements

### Platform & Technology
- **Language Options**: Python or JavaScript/TypeScript
  - Research constraint solver libraries (Google OR-Tools mentioned as potential option)
  - Choose based on best available timetabling/constraint solving libraries
- **Deployment**: Easy local network hosting or purely local execution
- **OS Support**: Windows, Mac, Linux (minimum Linux support required)
- **Interface**: Web-based with intuitive GUI for schedule generation, requirement editing, and adjustments

### Architecture Considerations
- Complete or partial replacement for current spreadsheet system
- MVP focus on JH-SH departments initially
- Single semester planning scope
- Export capability: PDF format preferred (avoid spreadsheet export to prevent manual editing)

## Scheduling Complexity & Constraints

### Class Structure
- **坐班 (Fixed Classroom)**: Students stay in homeroom, teachers rotate - primary model
- **走班 (Student Mobile)**: Students move for specific subjects - secondary model
- **Period Structure**:
  - JH/SH: 9 periods/day, 40-minute periods starting 8:00 AM
  - PS: Shorter day, mix of 30/40-minute periods
  - Different schedules for Monday (flag ceremony, study hours) and Friday (homeroom meeting)
  - Study hours: Monday 7:20 AM and 6:30-9:00 PM

### Teacher Constraints
- **Workload Limits**: 
  - Contractual maximum: 24 periods/week
  - Practical ideal: ≤15 periods/week (especially for JH-SH cross-teachers)
- **Shift Assignments**: Morning shift, evening shift, foreign teacher shift
  - Foreign teachers: Cannot start before 8:30 AM or finish after 5:30 PM
  - Evening/morning study supervisors: Avoid consecutive late-early scheduling
- **Cross-Department Teaching**: 
  - Some teachers work JH-SH
  - PE/Art/Music teachers cross ALL departments (PS-JH-SH) - major scheduling challenge

### Student & Class Constraints
- **Class Size**: Maximum 24 students per class/homeroom
- **Homeroom Assignment**: Tied to homeroom teacher, default classroom location
- **Group Splitting**: Some classes split into ability groups requiring simultaneous different subjects
- **Student-Mobile Classes**: Default to keeping homeroom groups together when possible

### Campus Layout
- Multiple buildings (college-style campus)
- **SH International**: 5 rooms, 5th floor Building 9
- **JH**: 4 rooms each on 3 floors, Building 19  
- **PS**: Buildings 4-5, 5-8 rooms per floor across 5 floors
- Special rooms: Labs, computer rooms, offices (MVP will ignore room scheduling)

## Functional Requirements

### Core Features (MVP)
1. **Schedule Generation**: Complete timetable satisfying graduation requirements and constraints
2. **Constraint Management**: Input/edit teacher limitations, course requirements, fixed events
3. **Conflict Resolution**: Handle impossible scenarios with error messages and suggestions
4. **Schedule Adjustment**: Easy modification system (ideally drag-and-drop GUI)
5. **Export**: PDF generation with print-friendly formatting

### Success Criteria Priority
1. **Graduation Requirements**: All curriculum requirements met
2. **Constraint Satisfaction**: Teacher limits, room capacity, timing restrictions
3. **Teacher Satisfaction**: Avoid problematic distributions (e.g., all periods one day, none for two days)
4. **Minimal Conflicts**: Optimize for smooth operation

### User Experience
- **Primary Users**: Scheduling team (MVP)
- **Future Users**: Teachers (schedule access/printing)
- **Interface**: Intuitive GUI for non-technical users
- **Adjustment Capability**: Easy constraint modification and schedule tweaking

## Data Structure Reference
System should handle data similar to the provided YAML structure:
- Teachers with IDs and constraints
- Courses with teacher assignments and period requirements
- Classes with course allocations
- Fixed events and time-specific constraints
- Teacher workload limits and availability

## Implementation Timeline
- **Deadline**: 1 month from project start
- **Rollout Strategy**: Limited scope deployment (JH-SH focus)
- **Scope**: Single semester planning initially

## Key Technical Challenges
1. **Multi-department Scheduling**: Especially PE/Art/Music across PS-JH-SH with different period lengths
2. **Constraint Solver Selection**: Research and implement appropriate algorithm/library
3. **User Interface Design**: Balance power with simplicity for non-technical users
4. **Schedule Optimization**: Balance hard constraints with teacher satisfaction
5. **Real-time Adjustment**: Efficient constraint modification and re-solving

## Git Repository Structure Recommendations
- Clear separation of constraint solver engine, data models, and UI components
- Configuration files for school-specific parameters
- Documentation for constraint definition and system operation
- Test data and scenarios for development/testing
- Export templates and styling

## Success Metrics
- Complete schedule generation without manual intervention
- All graduation requirements satisfied
- Teacher workload constraints respected
- Intuitive user adoption by scheduling team
- Significant time savings over current spreadsheet method
