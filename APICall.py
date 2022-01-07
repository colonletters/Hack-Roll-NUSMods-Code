import requests


# NUS mods database
db = requests.get("https://api.nusmods.com/v2/2021-2022/moduleList.json")

# gets all module codes to a list
lst = [i.get('moduleCode') for i in db.json()]

def GetModuleInfo(ModCode):
  #ModCode is a string
  return requests.get(f"https://api.nusmods.com/v2/2021-2022/modules/{ModCode}").json()
