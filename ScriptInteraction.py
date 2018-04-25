import requests
import json
import xmltodict


#Chargement du fichier de configuration Conf.json
fichier_configuration = open("Conf.json", "r")
contenu_conf = fichier_configuration.read()
fichier_configuration.close()
load_contenu_conf = json.loads(contenu_conf)
url = load_contenu_conf['url']
querystring = load_contenu_conf['querystring']
url_get_projects = load_contenu_conf['url_get_projects']
url_Select_Project = load_contenu_conf['url_Select_Project']


#Chargement du fichier FormatDataImport qui contient la liste des projects à affecter à une équipe en question
fichier_import_data = open("FormatDataImport.json")
contenu_fichier_import_data = fichier_import_data.read()
fichier_import_data.close()
payload_import_data = contenu_fichier_import_data

headers = {
    'Content-Type': "application/json",
    'Authorization': "Basic YWRtaW46YWRtaW4=",
    'Cache-Control': "no-cache",
    'Postman-Token': "c8b013db-72ae-4363-9be3-40e9eb7435d2"
    }

#récupérer la liste des projets existants
response_get_projects = requests.get(url_get_projects, headers=headers)
list_all_projects = xmltodict.parse(response_get_projects.text)
list_all_projects_json = json.dumps(list_all_projects)
list_all_projects_json_load = json.loads(list_all_projects_json)
list_import_data_load = json.loads(contenu_fichier_import_data)

listProjetsExistant = []
print("---------------------------------")
print("|la liste des projets existants:")
print("---------------------------------")
for key in list_all_projects_json_load['Projects']['Project']:
    print("Id = "+key['@Id']+" | Name = "+key['@Name'])
    listProjetsExistant.append(key['@Name'])

print("--------------------------------")
print("la liste des projets à affectés:")
print("--------------------------------")

for item in list_import_data_load['teamProjects']:
    print("Name = "+item['project']['name'])
print("------------------------------")
print("      tester l'existance!")
print("------------------------------")

#Vérification de l'éxistance d'un projet
for item in list_import_data_load['teamProjects']:
    if item['project']['name'] in listProjetsExistant:
        print("le projet num ==> " + item['project']['name'] + " existe déjà il faut l'affecté")
    else:
        #si le projet n'existe pas on le crée
        print("le projet num ==> " + item['project']['name']+" n'existe pas il faut le créer puis affecté")
        newproject = {
            "Name": item['project']['name']
        }
        response_Insert_Project = requests.post(url_get_projects, data=json.dumps(newproject), headers=headers)
        print(response_Insert_Project.text)

        ObjectJsonNewProjectsInserted = json.dumps(response_Insert_Project.text)
#la récupération des id des projets créés
Response_projects=[]
for item in list_import_data_load['teamProjects']:
    querybyname = "'"+item['project']['name']+"'"
    select_url = url_Select_Project+querybyname
    getObjectsById = requests.get(select_url, headers=headers)
    selected_project = xmltodict.parse(getObjectsById.text)
    selected_project_json = json.dumps(selected_project)
    selected_project_json_load = json.loads(selected_project_json)
    Response_projects.append(selected_project_json_load['Projects']['Project']['@Id'])
print(Response_projects)

print("//////////////////////////////////////////////////")
print("Construction du fichier .json de l'affectation")
print("//////////////////////////////////////////////////")

#l'affectation des projets
for item in Response_projects:
    playlist = {}
    playlist["id"] = list_import_data_load['id']
    playlist["teamProjects"] = []
    playlist["teamProjects"].append("projet")
    playlist["teamProjects"][0] = {}
    playlist["teamProjects"][0]["project"] = {}
    playlist["teamProjects"][0]["project"]["id"] = item
    playlist["teamProjects"][0]["isFullProjectAccess"] = True
    payload_project = json.dumps(playlist)
    print(payload_project)
    response = requests.request("POST", url, data=payload_project, headers=headers, params=querystring)
    print(response.text)