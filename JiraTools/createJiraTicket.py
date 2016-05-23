from jira.client import JIRA

import argparse
import re


class JiraParameterError(Exception):
    pass

def parserArgument():
    program = 'getParameter' 
    desc    = "=="
    version = "Version: V0.0 (2016-02-25)"
    parser  = argparse.ArgumentParser(prog=program,description=desc,epilog=version)
    
    parser.add_argument('-parameter',metavar='p',type=str,default="",help="paramter")
    parser.add_argument('-user',metavar='u',type=str,default="xiaowj",help="Jira User ID")
    parser.add_argument('-password',metavar='p',type=str,default="Just for test",help="Jira Password")
    parser.add_argument('-configpath',metavar='c',type=str,default="",help="this is the path of cofig file")
    return parser.parse_args()
  


def get_jira_parameter(args):
    
    item_name={'DESCRIPTION:':'1::','DUEDATE:':'2::','PRIORITY:':'3::','SUMMARY:':'4::','TYPE:':'5::'}
    
    issue_dict_default={
        'project': {'key':'SHFTE'},
        'issuetype': {'name': 'Task'},
        }

    correspond_fields={ 
         'SUMMARY':'summary',
         'DESCRIPTION':'description',
         'PRIORITY':'priority',
         'DUEDATE':'duedate',
         'TYPE':'Type',
        }
    special_fields=['priority']
    
    temp_parameter_str=args.strip('{}')
    
    for k,v in item_name.items():
        temp_parameter_str=temp_parameter_str.replace(k,v)
        
    rules=r',?([0-9]::)'
    temp_paramrelst=re.split(rules,temp_parameter_str)
    
    parameter_values=[]
    parameter_keys=[]
    for key,value in correspond_fields.items():
        if (temp_parameter_str.count(item_name[key+':'])>1):
            raise JiraParameterError("Error: some text you input is the same to the item name")
        parameter_values.append(temp_paramrelst[temp_paramrelst.index(item_name[key+':'])+1])
        parameter_keys.append(value)
            
    param_list=[]
    for i in zip(parameter_keys,parameter_values):
        param_list.append(i)
        
    param_from_user=dict(param_list)
    if ('' in param_from_user.values() ):
        raise JiraParameterError("Error: Invalid Parameter!")
        
    jira_parameters={}
    for k in param_from_user.keys():
        if( k in special_fields):
            jira_parameters.update({k:{'name':param_from_user[k]}})
        elif (k=='Type'):
            labels_and_assignee=get_label_and_assignee(param_from_user[k])
            jira_parameters.update(labels_and_assignee)
        else:
            jira_parameters.update({k:param_from_user[k]})  
    jira_parameters.update(issue_dict_default)   

    return jira_parameters

def get_label_and_assignee(type_param):
    
    confg=["type","label","assignee"]
    label_and_assignee_list=load_label_and_assignee(path)
    type_dict={}
    for sub_label in label_and_assignee_list:
        temp_param=sub_label.split(':')
        if(len(temp_param)!=len(confg)):
            raise JiraParameterError("Error: config file is invalid")
        
        type_dict.update({temp_param[0]:{'labels':temp_param[1].split(';'),'assignee':{'name':temp_param[2]}}})
    
    if (type_param not in type_dict.keys()):
        raise JiraParameterError("Error: Label is Invalid")
       
    return type_dict[type_param]

def load_label_and_assignee(path):
    try:
        f=open(path,'r')
        line=f.readlines()
        f.close()
    except:
        raise JiraParameterError("Error:the assignee and label config file can not open")
    type_1ist=[]
    EMPTY=''
    for sn in line:
        if(EMPTY!=sn.strip('\n')):
            temp=sn.strip()
            type_1ist.extend([temp.strip('\n')])
    return type_1ist
    

def main():
    
    argv=parserArgument()
    global path
    path=argv.configpath
    jira_parameter=get_jira_parameter(argv.parameter)
    jira = JIRA({'server':"http://jira.micron.com/jira/"},basic_auth=(argv.user, argv.password))

    try:
        new_issue=jira.create_issue(fields=jira_parameter)
        print "Jira Ticket is created successfully"
        print "the ticket id is: "+new_issue.key
    except Exception as e:
        print e
if __name__ == '__main__':
    main()