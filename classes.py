from APICall import GetModuleInfo
from main.py import lst
from datetime import timedelta

class Timeslot():
    def __init__(self, data, type):
        self.Type = type
        self.Number = data['classNo']
        self.Start = timedelta(hours = int(data['startTime'][:2]), minutes = int(data['startTime'][2:]))
        self.End = timedelta(hours=int(data['endTime'][:2]), minutes=int(data['endTime'][2:]))
        self.Duration = self.End - self.Start
        self.Day = data['day']
        self.ClassType = data['lessonType']
        self.Size = data['size']
        self.Venue = data['venue']
        self.Weeks = data['weeks']

    def __str__(self):
        return f"{self.Type} {self.ClassType}: {self.Number}\n" \
               f"    {self.Day} {str(self.Start)[:-3]} - {str(self.End)[:-3]}"

    def __repr__(self):
        return self.__str__()

class Module():
    def __init__(self, ModString):
        #API CALL#
        ParseBuffer = GetModuleInfo(ModString)
        if not ParseBuffer:
          raise ValueError(f"Module code {ModString} not in system!")
        try: self.Code = ModString
        except:
            self.Code = "Unknown"
        try: self.Preclusions = ParseBuffer['preclusion']
        except:
            self.Preclusions = "Unknown"
        try: self.Description = ParseBuffer['description']
        except:
            self.Description = "Unknown"
        try: self.Title = ParseBuffer['title']
        except:
            self.Title = "Unknown"
        try: self.Department = ParseBuffer['department']
        except:
            self.Department = "Unknown"
        try: self.Faculty = ParseBuffer['faculty']
        except:
            self.Faculty = "Unknown"
        try: self.Workload = ParseBuffer['workload']
        except:
            self.Workload = "Unknown"
        try: self.Prerequisites = ParseBuffer['prerequisite']
        except:
            self.Prerequisites = "Unknown"
        try: self.Credits = ParseBuffer['moduleCredit']
        except:
            self.Credits = "Unknown"
        try: self.SU = ParseBuffer['attributes']['su']
        except:
            self.SU = "Unknown"
        try: self.PrereqTree = ParseBuffer['prereqTree']
        except:
            self.PrereqTree = "Unknown"
        try: self.RequirementsFor = ParseBuffer['fulfillRequirements']
        except:
            self.RequirementsFor = "Unknown"
        self.ClassList, self.ExamDate, self.ExamDuration = self.ParseTimetable(ParseBuffer['semesterData'])
        try: self.FixedList = [i for i in self.ClassList if i.Type == "Fixed"]
        except:
            self.FixedList = None
        try: self.FlexList = [i for i in self.ClassList if i.Type == "Flex"]
        except:
            self.FlexList = None


    def __str__(self):
        return self.Code
    def PrettyPrint(self):
        NiceString = f"Module: {self.Code} ({self.Title})\n\n" \
                     f"Credits: {self.Credits} \n"\
                     f"Workload: {sum(self.Workload)} hours\n" \
                     f"SU-eligible: {self.SU}\n" \
                     f"Exam Date: {self.ExamDate}"
        return NiceString

    def ParseTimetable(self, AllClasses):
        try:
            sem2 = [i for i in AllClasses if i['semester'] == 2][0]
        except:
            print("Module not offered in Sem 2!")
            return None, None, None
        try: examdate = sem2['examDate']
        except: examdate = None
        try: examduration = sem2['examDuration']
        except:examduration = None
        classTypes = {i['lessonType'] for i in sem2['timetable']}
        classlist = []
        for j in classTypes:
            listcheck = [i for i in sem2['timetable'] if i['lessonType'] == j]
            if len({i['classNo'] for i in listcheck}) == 1:
                for i in listcheck: classlist.append(Timeslot(i, "Fixed"))
            else:
                for i in listcheck: classlist.append(Timeslot(i, "Flex"))
        return classlist, examdate, examduration
        #for now, ignores sem 1

