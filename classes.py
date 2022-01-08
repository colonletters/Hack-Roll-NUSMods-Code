from APICall import GetModuleInfo
from main.py import lst
from datetime import timedelta
from itertools import product, groupby, combinations

class Timeslot():
  #holds info for any particular block of time
  
    def __init__(self, data, typeOf):
        self.Type = typeOf
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
  #holds multiply timeslots together and generates 'choices'
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
    def __repr__(self):
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

    def initialisedomain(self):
        allList = []
        biglist = []
        for j in {i.ClassType for i in self.ClassList}:
            allList.append([i for i in self.ClassList if i.ClassType == j])
        for k in allList:
            k = sorted(k, key=lambda x: x.Number)
            biglist.append([tuple(g) for l, g in groupby(k, lambda x:x.Number)])
        self.Domain = list(product(*biglist))

    def cleardomain(self, clearlist):
        "remove from list"
        for a in clearlist:
            try:
                self.Domain.remove(a)
                #(len(self.Domain))
            except:
                #print('uh oh')
                pass



class TimeTable():
    def __init__(self, modlist):
        self.Modlist = []
        for i in modlist:
            buffer = Module(i)
            buffer.initialisedomain()
            self.Modlist.append(buffer)
        print(self.Modlist)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Some code below cannibalized/repurposed from a personal CS50 AI project
        """

        removelist = []
        for module in self.Modlist:
            for node in module.Domain:
                flatlist = [item for sublist in node for item in sublist]
                Days = {i.Day for i in flatlist}
                for day in Days:
                    filteredlist = [i for i in flatlist if i.Day == day]
                    for j, k in combinations(filteredlist, 2):
                        if (k.Start < j.Start < k.End) or (k.Start < j.End < k.End) \
                                and (len(set(j.Weeks).intersection(k.Weeks)) != 0):
                            removelist.append(node)
            module.cleardomain(removelist)

    def clashcheck(self, a, b):
        """
        Checking for timetable clashing between arc a and arc b.
        Clashes occur when: a class has start/end times between another class' start/end time
                            the day of both classes are the same
                            the two classes have at least 1 week in common

        Returns True if there is a clash and False if there is no clash.
        """
        flatlistA = [item for sublist in a for item in sublist]
        flatlistB = [item for sublist in b for item in sublist]
        #Only select days in a where items exist in b (intersection)
        SameDaysA = [i for i in flatlistA if i.Day in {j.Day for j in flatlistB}]
        Days = {i.Day for i in SameDaysA}

        for day in Days:
            daysA = [i for i in SameDaysA if i.Day == day]
            daysB = [i for i in flatlistB if i.Day == day]
            for j in daysA:
                for k in daysB:
                    if ((k.Start < j.Start < k.End) or (k.Start < j.End < k.End) \
                            or (k.Start == j.Start) or (k.End == j.End)) \
                            and (len(set(j.Weeks).intersection(k.Weeks)) != 0):
                        return True
        return False

    def revise(self, x, y):
        """
        Make module `x` arc consistent with module `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        removelist = []
        for i in x.Domain:
            flag = True
            for j in y.Domain:
                #if x clashes for all y, remove x
                if not self.clashcheck(i,j):
                    flag = False
            if flag == True:
                removelist.append(i)
        if len(removelist) == 0:
            return False
        else:
            #print(len(removelist))
            x.cleardomain(removelist)
            return True

    def arcneighbors(self, Module):
        hi = self.Modlist[:]
        hi.remove(Module)
        return hi

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            arcs = list(combinations(self.Modlist,2))
        #print(f'ac3 consistency - total {len(arcs)} intersections')
        while len(arcs) !=0:
            #print(arcs[0])
            x, y = arcs.pop(0)
            if self.revise(x,y):
                if len(x.Domain) == 0:
                    return False
                hi = self.arcneighbors(x)
                hi.remove(y)
                arcs+=list(combinations(hi,2))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., each mod has an arc); return False otherwise.
        """
        if len(assignment) == len(self.Modlist):
            for i in assignment.values():
                if i is None:
                    return False
            print("Assignment Complete!")
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., no clashes); return False otherwise.
        """
        biglist = []
        for arc in assignment.values():
            biglist+=arc
        biglist = [item for sublist in biglist for item in sublist]
        daylist = {i.Day for i in biglist}
        for day in daylist:
            filteredlist = [i for i in biglist if i.Day == day]
            for j, k in combinations(filteredlist, 2):
                if ((k.Start < j.Start < k.End) or (k.Start < j.End < k.End) \
                        or  (k.Start == j.Start) or (k.End == j.End))\
                        and (len(set(j.Weeks).intersection(k.Weeks)) != 0):
                    return False
        return True

    def order_domain_values(self, module, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #print(module)
        #print(module.Domain)
        choicedict = {x:0 for x in module.Domain}
        neighbours = self.arcneighbors(module)
        for arc in module.Domain:
            for neighbour in neighbours:
                if neighbour not in assignment.keys():
                    for narc in neighbour.Domain:
                        if self.clashcheck(arc,narc):
                            choicedict[arc] +=1
        return [x[0] for x in sorted(choicedict.items(), key=lambda x: x[1],reverse=True)]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassignedVar = []
        for i in self.Modlist:
            if i not in assignment.keys():
                unassignedVar.append((i,len(i.Domain)))
        unassignedVar.sort(key=lambda i:i[1])
        return unassignedVar[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        #print(convert_to_nusmods(assignment))
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)
        return None
        
def convert_to_nusmods(assignment):
    if assignment == None:
        return None
    ori = "https://nusmods.com/timetable/sem-2/share?"
    bigdict = {
        "Lecture":"LEC",
        "Tutorial":'TUT',
        "Sectional Teaching":"SEC",
        "Laboratory":"LAB",
        'Packaged Tutorial':"PTUT",
        "Packaged Lecture":"PLEC",
        "Packaged Laboratory":"PLAB"
    }
    first = True
    for i in assignment.keys():
        if first==False:
            ori = ori[:-1]
            ori+='&'
        first=False
        ori+=i.Code
        ori+='='
        for j in assignment[i]:
            j = j[0]
            #print(i)
            #print(j)
            if j.Type == 'Flex' or "Fixed":
                ori+=f"{bigdict[j.ClassType]}:{j.Number},"
    #print(ori)
    return(ori)