
from fajira.JiraInterface import CJiraPython
import argparse
import Lib_FAReport as FR
from bs4 import BeautifulSoup
from jiraQueryWeb import JiraQueryWeb
import pytz, datetime



TABLE_TITLE = ['TYPE','KEY','SUMMARY','PRIORITY','STATUS']
JIRAurl     = "http://jira.micron.com/jira/browse/"


time_start              = "{} 11:30:00".format(datetime.date.today())
time_end                = "{} 13:30:00".format(datetime.date.today())

resttime_start          = datetime.datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
resttime_end            = datetime.datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")

time_start   = "{} 9:00:00".format(datetime.date.today())
time_end     = "{} 18:00:00".format(datetime.date.today())

workday_start= datetime.datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
workday_end  = datetime.datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")

WORK_TIME               = 420#the 7 hours work time

class JiraQueryError(Exception):
    pass
def parserArgument():
    program = 'pyjira.py' 
    desc    = "=="
    version = "Version: V0.0 (12/22/2015)"
   

    parser  = argparse.ArgumentParser(prog=program,description=desc,epilog=version)
    parser.add_argument('-user',metavar='u',type=str,default="xiaowj",help="Jira User ID")
    parser.add_argument('-password',metavar='p',type=str,default="Just for test",help="Jira Password")
    parser.add_argument('-member',metavar='m',type=str,default="chenchengc:xiaowj:yangmin:mmxu:zhangyh:zhzhou",help="Team Member")

    return parser.parse_args()

def login(user,pswd):
    jengine = CJiraPython(user,pswd)
    return jengine

def getJQL(crew):
    return "created > startOfDay('-90d') and issuetype IN ('Task','Sub-task') and status NOT IN ('Closed','Resolved','Verified','Validated')and assignee={} order by status ".format(crew)

def jiraQuery(jObj,qrule):
    qRst=[]
    
    for tic in jObj.query(qrule):
        qRst.append(tic.getTicket().getTicket())
    
    for item in qRst:
        for x in item.keys():
            if (isinstance(item[x],dict)):
                (k,v),=item[x].items()
                item[x]=str(v)
            elif (isinstance(item[x],list)):
                for idx in xrange(len(item[x])):
                    if(isinstance(item[x][idx],unicode)):
                        item[x][idx]=str(item[x][idx])
                    if(isinstance(item[x][idx], dict)):
                        (k,v),=item[x][idx].items()
                        item[x][idx]=str(v)
                item[x]=','.join(item[x])
                
                
    time_revied_lst     = updateJiraTimezone(qRst)
    sorted_qRst         = sortTask(time_revied_lst)            
    #get the id
    issueID=[]
    for qryslt in sorted_qRst:
        issueID.append(str(qryslt['issuekey']))
    
    return sorted_qRst, issueID

def sortTask(tasklst):
    
    STATUS_ORDER={"In Progress":0 ,"Triaged":1,"Open":2,"Blocked":3} 
    tasklst.sort(key=lambda val: STATUS_ORDER[val['status']])
    
    new_tasklst     = []
    PRIORITY_ORDER={"P1":0,"P2":1,"P3":2,"P4":3,"P5":4,"NONE":5} 
    for st in STATUS_ORDER:
        templst     = []   
        for subtask in tasklst:
            if(subtask["status"]==st):
                templst.append(subtask)
        templst.sort(key=lambda val: PRIORITY_ORDER[val['priority']])
        new_tasklst.extend(templst)
        
    return new_tasklst

def getJiraLink(issuekey,count=None):
    
    urlAdd      = {}
    for key in issuekey:
        templink=JIRAurl+key
        urlAdd.update({key:dict([['link',templink]])})
        if (count!=None):
            count-=1
            if(count==0):
                break
            
    return urlAdd

def updateJiraTimezone(querylst):
    server_timezone =pytz.timezone ("America/Boise")
    local_timezone=pytz.timezone ("Asia/Shanghai")
    for ans in querylst:
        ans['updated']=ans['updated'].split('.')[0].replace('T',' ')
        naive = datetime.datetime.strptime (ans['updated'], "%Y-%m-%d %H:%M:%S")
        local_dt = server_timezone.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone (local_timezone)
        ans['updated']=utc_dt.strftime("%Y-%m-%d %H:%M:%S")
        
    return querylst
 
def getHTMLSource(queryResult):
    tr      = FR.CJiraQueryReport("JiraTicket Query Result")
    for data in queryResult:
        tr.setTicketInfo(**data)
    htmlRst = tr.generate() 
    return htmlRst
     
def getHTMLStyle(tableSourceList,timelinelist):
    htmlcodeObj         = JiraQueryWeb()
    tableCssSource      = htmlcodeObj["tableCSS"]

    timelineCssSource   = htmlcodeObj["timelineCSS"] 

    HTMLHeadPart        = htmlcodeObj["HTML_head"]   

    HTMLEndPart         = htmlcodeObj["HTML_end"]
    
    WHOLE_TIMELINE_HEAD = htmlcodeObj["whole_timeline_head"]
    
    WHOLE_TIMELINE_END  = htmlcodeObj["whole_timeline_end"]

    cssfp1=open(r'style.css','w+')
    cssfp1.write(tableCssSource)
    cssfp1.close()
    
    cssfp2=open(r'timeline.css','w+')
    cssfp2.write(timelineCssSource)
    cssfp2.close()
    
    tableCode='\n'.join(tableSourceList)
    timelineCode='\n'.join(timelinelist)
    finaHTMLCode='\n'.join([HTMLHeadPart,tableCode,WHOLE_TIMELINE_HEAD,timelineCode,WHOLE_TIMELINE_END,HTMLEndPart])
    f=open(r'JiraTaskTimeline.html','w+');
    f.write(finaHTMLCode)
    f.close()
    
def getTableStyle(sourcecode,issueID,assignee):
    
    tableEnd='''
      </table>
</div>
    '''
    
    title=''''''
    for titleItem in TABLE_TITLE:
        temp="      <td>{}</td>\n".format(titleItem)
        title+=temp

    tableHead='''
<div class="table">
  <table class="flatTable">
    <tr class="titleTr">
      <td class="titleTd">ASSIGNEE:{}</td>
      <td colspan="42"></td>
  
    </tr>
    <tr class="headingTr">
{}
    </tr>    
    '''.format(assignee,title)
    
    tableContent=dealTableContent(sourcecode,issueID)

    return '\n'.join([tableHead,tableContent,tableEnd])

def dealTableContent(htcode,issueID):
    
    urlAdd       = getJiraLink(issueID)

    soup         = BeautifulSoup(htcode,"html.parser")
    parseLst     = soup.tbody.contents
    newTableCode=''''''
    url_idx=0
    for trTag in parseLst:
        tempParseLst    = []
         
        if (trTag!=u'\n'):
            for tdTag in trTag:
                if(tdTag != u'\n'):

                    tempParseLst.append(str(tdTag))
                     
            new_soup= BeautifulSoup(tempParseLst[1],"html.parser")
            #add the href
            newTag  = new_soup.new_tag("a",href=urlAdd[issueID[url_idx]]['link'])
            new_soup.td.string.wrap(newTag)
            tempParseLst[1]=str(new_soup.contents[0])
            
            tempParseLst.insert(0, '<tr>')
            tempParseLst.append('</tr>')
            url_idx+=1
        #generate the code which contain the href
        newTableCode+=('\n'.join(tempParseLst)+'\n')
            
    return newTableCode 

def bubbleSort(alist):
    exchanges = True
    passnum = len(alist)-1
    while passnum > 0 and exchanges:
        exchanges = False
        for i in range(passnum):
            if alist[i][1]['updated']>alist[i+1][1]['updated']:
                exchanges = True
                temp = alist[i]
                alist[i] = alist[i+1]
                alist[i+1] = temp
        passnum = passnum-1
        
    return alist
def dealTimelineContent(taskList,taskIDLst,taskOwner):
    htmlcodeObj         = JiraQueryWeb()
    ONE_TIMELINE_HEAD   = htmlcodeObj["one_timeline_head"]
    ONE_TIMELINE_END    = htmlcodeObj["one_timeline_end"]
    
    ONE_NORM_BAR_HEAD            ='''
          <div  style="display:block;overflow: hidden;margin-bottom: 1em;">    
    '''          
    
    ONE_NORM_BAR_END             ='''
          </div>    
    '''

    ONE_HIDDEN_BAR_HEAD            ='''
          <div  class="read-more-target" style="display:block;overflow: hidden;margin-bottom: 1em;">    
    '''          
    
    ONE_HIDDEN_BAR_END             ='''
          </div>    
    '''
    OWNER_HTML              = '''
            <span class="graph-legend" ><div id="wrap">{}</div></span>   
    ''' .format(taskOwner)
    
    HIDDEN_PART_HEAD        ='''
          <!-- the hidden part start--> 
          <div >
            <input type="checkbox" class="read-more-state" id="{}">
            <div  class="read-more-wrap">    
    '''.format(taskOwner)
    
    HIDDEN_PART_END        ='''
            </div>
            <label for="{}" class="read-more-trigger"></label>
          </div>    
    '''.format(taskOwner)
    
    
   
    ONE_MINUTE_WIDTH        = 0.208             
    ONE_ROW_MAX_LIST        = 3
    MAX_BAR_SHOW            = 3
    OPEN_TRI_BLOCK          = 6
    Inprogress              = [] #the ele in list is a tuple
    Open_and_Triaged        = [] 
    Blocked                 = [] 

    content                 = []
    bars                    = []
    Inprogress_bars         = []
    op_tri_bars             = []
    blked_bars              = []
    
    global WORK_TIME
    global workday_start
    global workday_end
    global resttime_start
    global resttime_end
    
    taskNecessaryInfoList   = getTaskInfo(taskList,taskIDLst,WORK_TIME)
    
    

    for info in taskNecessaryInfoList:
        if ('In Progress' == info[1]['status']):
                Inprogress.append(info)
           
        elif ('Blocked' == info[1]['status']):   
            Blocked.append(info)
            
        else:
            Open_and_Triaged.append(info)
    
    #sort by updated
    Inprogress=bubbleSort(Inprogress)
      
    left_start_time = workday_start
          
    if (taskNecessaryInfoList==[]):

        taskHTML            = (ONE_NORM_BAR_HEAD+ONE_NORM_BAR_END)*3
        content.append(taskHTML)
        
    else:
        if(Inprogress != []):
            previous_task=[x for x in Inprogress if x[1]['updated']<workday_start]
            if(previous_task !=[]):
                pre_tempbar=[]
                for previous_sub in previous_task:
                    subHTML= timelineAssign(rest_start_time=left_start_time,one_taskinfo=previous_sub)

                    left_start_time         = subHTML[0][2]
                    pre_tempbar.extend(subHTML)
                    
                    if (left_start_time==workday_end):
                        break
                    if (left_start_time!=workday_end and  previous_task.index(previous_sub)==(len(previous_task)-1)):
                        break
                bars.append(pre_tempbar)
                    
            else:
                bars.append([])
                
            today_task      = [x for x in Inprogress if x[1]['updated']>workday_start]
            
            to_tempbar      = []
            
            if(today_task !=[]):
                lefttask=list(today_task)
                
                while(lefttask!=[]):
                    left_start_time = workday_start
                    dellist         = []
                    for idx in range(len(lefttask)):
            
                        if(lefttask[idx][1]['updated']>left_start_time):
                            subHTML    = timelineAssign(one_taskinfo=lefttask[idx],rest_start_time=left_start_time)
                            left_start_time         = subHTML[0][2]
                            to_tempbar.extend(subHTML)
                            dellist.append(lefttask[idx])
                                
                        if (left_start_time==workday_end and idx!=len(lefttask)-1):
                            bars.append(to_tempbar)
                            to_tempbar=[]
                            break
                        if (idx==len(lefttask)-1):
                            bars.append(to_tempbar)
                            to_tempbar=[]
                            break
                    for i in dellist:
                        if (lefttask==[]):
                            break
                        lefttask.remove(i)
    
                
        for sub_bar in bars:
            previous_task_end_time=workday_start
            for idx in range(0,len(sub_bar)+1):
                if(idx!=len(sub_bar)):
                    if(sub_bar[idx]==[]):
                        now_start_time= workday_end 
                        
                    elif(sub_bar[idx][1]<workday_start and idx==0):
                        now_start_time= workday_start
                        
                    elif(sub_bar[idx][1]<workday_start and idx!=0):
                        now_start_time=previous_task_end_time
                    
                    else:
                        now_start_time=sub_bar[idx][1]
                
                    
    #                 if(sub_bar[idx]!=[] and idx !=len(sub_bar)-1):
                    if(now_start_time<resttime_start or previous_task_end_time>resttime_end):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)
                        
                    if(now_start_time>resttime_end and previous_task_end_time<resttime_start):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)-120
                    
                    if(now_start_time>resttime_start and now_start_time< resttime_end):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)-240

                    if(previous_task_end_time>resttime_start and previous_task_end_time< resttime_end):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)-120
                        
                    subHTML= timelineAssign(rest_start_time=time_lag)
                    sub_bar[idx][0]=subHTML+sub_bar[idx][0]
                    previous_task_end_time= sub_bar[idx][2]
                else:
                    now_start_time= workday_end
                    if(now_start_time<resttime_start or previous_task_end_time>resttime_end):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)
                        
                    if(now_start_time>resttime_end and previous_task_end_time<resttime_start):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)-120
                    
                    if(now_start_time>resttime_start and now_start_time< resttime_end):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)-240

                    if(previous_task_end_time>resttime_start and previous_task_end_time< resttime_end):
                        time_lag=int((now_start_time-previous_task_end_time).total_seconds()/60)-120
                    subHTML= timelineAssign(rest_start_time=time_lag)
                    sub_bar[idx-1][0]=sub_bar[idx-1][0]+subHTML
                    
            temptemp=[]
            for idx in range(0,len(sub_bar)):
                temptemp.append(sub_bar[idx][0])
            Inprogress_bars.append('\n'.join(temptemp))           
            
        
        if(Open_and_Triaged!=[]):
            temp=[]
            for op_tri in Open_and_Triaged:
                subHTML = timelineAssign(one_taskinfo=op_tri)
                temp.append(subHTML)
            
            for i in range(0,len(temp),3):
                subHTML= timelineAssign(rest_start_time=(OPEN_TRI_BLOCK-len(temp[i:i+3])*2)/ONE_MINUTE_WIDTH)
                temp0='\n'.join(temp[i:i+3])+'\n'+subHTML
                op_tri_bars.append(temp0)
                   
        if (Blocked!=[]):
            temp=[]
            for blked in Blocked:
                subHTML = timelineAssign(one_taskinfo=blked)
                temp.append(subHTML)
                
            for i in range(0,len(temp),ONE_ROW_MAX_LIST):
                temp0='\n'.join(temp[i:i+ONE_ROW_MAX_LIST])
                blked_bars.append(temp0)
                
        loop_counts=        max(len(Inprogress_bars),len(op_tri_bars),len(blked_bars))
        

                
        for i in range(0,loop_counts):
            if (i>MAX_BAR_SHOW-1):
                temp=ONE_HIDDEN_BAR_HEAD+'{}'+ONE_HIDDEN_BAR_END
            else:
                temp=ONE_NORM_BAR_HEAD+'{}'+ONE_NORM_BAR_END
            if (i==MAX_BAR_SHOW):
                temp=HIDDEN_PART_HEAD+temp
                
            if (i==loop_counts-1 and i>=MAX_BAR_SHOW):
                temp=temp+HIDDEN_PART_END
                
            if(i>len(op_tri_bars)-1):
                subHTML= timelineAssign(rest_start_time=OPEN_TRI_BLOCK/ONE_MINUTE_WIDTH)
                op_tri_bars.append(subHTML)
            if(i>len(Inprogress_bars)-1):
                subHTML= timelineAssign(rest_start_time=WORK_TIME)
                Inprogress_bars.append(subHTML)
                
            if(i>len(blked_bars)-1):
                content.append(temp.format(op_tri_bars[i]+Inprogress_bars[i]))   
            else: 
                content.append(temp.format(op_tri_bars[i]+Inprogress_bars[i]+blked_bars[i]))
            
           
            
            
               
    return ONE_TIMELINE_HEAD+OWNER_HTML+"".join(content)+ONE_TIMELINE_END
            
             
def timelineAssign(one_taskinfo=None,rest_start_time=None,reason=''):
    
    STATUS={
    "Open"                : '''
            <div class="graph-bar-fragment open" data-value="{}" style="width: 2%" onclick="location.href='{link}'" ></div>
    ''',
    "Triaged"             : '''
            <div class="graph-bar-fragment triaged" data-value="{}" style="width: 2%" onclick="location.href='{link}'" ></div>    
    ''',
    "Blocked"             : '''
            <div class="graph-bar-fragment block" data-value="{key_and_reason}" style="width: 2%" onclick="location.href='{link}'" ></div>    
    ''',
    "In Progress"         : '''
            <div class="graph-bar-fragment inprogress" data-value="{summary}" style="width: {width}%" onclick="location.href='{link}'" >{key}</div>    
    ''',


    }
    
    IDEL                 = '''
            <div class="graph-bar-fragment empty" data-value="IDLE" style="width:{}%"></div>  
    '''
    In_Progress_remind   = '''
            <div class=\"graph-bar-fragment inprogress\" data-value=\"{summary}(Update Requried)\" style=\"width: {width}%\" onclick=\"location.href='{link}'\" >{key}</div>    
    '''
    

    ONE_MINUTE_WIDTH     = 0.208
    

    global workday_start
    global workday_end
    global resttime_start
    global resttime_end
    global WORK_TIME
    
    if(one_taskinfo!=None):
        if (one_taskinfo[1]['status']=="In Progress"):
            
            if (rest_start_time<resttime_end):
                gap=int((workday_end-rest_start_time).total_seconds()/60)-120

            else:
                gap=int((workday_end-rest_start_time).total_seconds()/60)
                
            if( one_taskinfo[1]['today_end_time']<workday_end and one_taskinfo[1]['today_end_time']>workday_start):
                #
                if(one_taskinfo[1]['TaskTime']>gap):
                    tempHTML=STATUS[one_taskinfo[1]['status']].format(key=one_taskinfo[0],width=rest_start_time*ONE_MINUTE_WIDTH,**one_taskinfo[1])
                    free_start=workday_end                    
                else:
                    #this means today-build-and-today-end task
                    tempHTML=STATUS[one_taskinfo[1]['status']].format(key=one_taskinfo[0],width=one_taskinfo[1]['TaskTime']*ONE_MINUTE_WIDTH,**one_taskinfo[1])
                    if(one_taskinfo[1]['updated']<workday_start):
                        free_start= rest_start_time+datetime.timedelta(minutes=one_taskinfo[1]['TaskTime'])
                        if(free_start>resttime_start and free_start<resttime_end):
                            free_start=resttime_start+datetime.timedelta(minutes=int((free_start-resttime_start).total_seconds()/60))
                    else:   
                        free_start=one_taskinfo[1]['today_end_time']
                    
                
            elif(one_taskinfo[1]['today_end_time']<workday_start):
                
                if (gap>one_taskinfo[1]['TaskTime']):
                    tempHTML=In_Progress_remind.format(key=one_taskinfo[0],width=one_taskinfo[1]['TaskTime']*ONE_MINUTE_WIDTH,**one_taskinfo[1])
                    free_start=rest_start_time+datetime.timedelta(minutes=one_taskinfo[1]['TaskTime'])
                    if(rest_start_time<resttime_start and free_start>resttime_end):
                        free_start=free_start+datetime.timedelta(minutes=int((resttime_end-resttime_start).total_seconds()/60));
                else:
                    tempHTML=In_Progress_remind.format(key=one_taskinfo[0],width=gap*ONE_MINUTE_WIDTH,**one_taskinfo[1])
                    free_start=workday_end
                
                if(free_start>resttime_start and free_start<resttime_end):
                    temp=datetime.timedelta(minutes=int((free_start-resttime_start).total_seconds()/60))
                    free_start=resttime_end+temp   
                    
                
                    

            elif( one_taskinfo[1]['today_end_time']>workday_end):
                if(one_taskinfo[1]['updated']<workday_start):
                    tempHTML=STATUS[one_taskinfo[1]['status']].format(key=one_taskinfo[0],width=gap*ONE_MINUTE_WIDTH,**one_taskinfo[1])
                elif(one_taskinfo[1]['updated']<resttime_start):
                    tempHTML=STATUS[one_taskinfo[1]['status']].format(key=one_taskinfo[0],width=(int((workday_end-one_taskinfo[1]['updated']).total_seconds()/60)-120)*ONE_MINUTE_WIDTH,**one_taskinfo[1])
                else:
                    tempHTML=STATUS[one_taskinfo[1]['status']].format(key=one_taskinfo[0],width=int((workday_end-one_taskinfo[1]['updated']).total_seconds()/60)*ONE_MINUTE_WIDTH,**one_taskinfo[1])
                                       
                       
                free_start=workday_end
            
            return [[tempHTML,one_taskinfo[1]['updated'],free_start,]]
        
        elif (one_taskinfo[1]['status']=="Open" or one_taskinfo[1]['status']=="Triaged"):
            
            tempHTML=STATUS[one_taskinfo[1]['status']].format(one_taskinfo[0],**one_taskinfo[1])
            return tempHTML
     
    #     if (one_taskinfo[1]['status']=="Blocked" and reason !=None):
    #         
    #         tempHTML=STATUS[one_taskinfo[1]['status']].format(key_and_reason=one_taskinfo[0]+'||'+'reason',*one_taskinfo)
    #         return tempHTML,None,None
    #     else:
    #         raise JiraQueryError("Error: Invalid Parameters!")
        
        elif (one_taskinfo[1]['status']=="Blocked" ):
            
            tempHTML=STATUS[one_taskinfo[1]['status']].format(key_and_reason=one_taskinfo[0],**one_taskinfo[1])
            return tempHTML
        
    else:
        tempHTML=IDEL.format(rest_start_time*ONE_MINUTE_WIDTH)
        return tempHTML
 
      
def getTaskInfo(taskList,taskIDLst,count=None):

    global resttime_start
    global resttime_end
    taskTime                = []    
    
    href                    = getJiraLink(taskIDLst)
    task_rest_time          = 60    #the default time if task does not have task time
    
    today_end_time          = resttime_start
    
    for subtask in taskList:
        
        if (subtask['timeestimate']=='None' and subtask['status']!='In Progress' ):
            task_rest_time=None
        elif(subtask['timeestimate']=='None' and subtask['status']=='In Progress' ):
            task_rest_time          = 60
        else:
            task_rest_time=int(subtask['timeestimate'])/60
            if(task_rest_time>420):
                task_rest_time=420
        if(task_rest_time!=None):       
            task_duration       = datetime.timedelta(minutes=task_rest_time)
            task_starttime      = datetime.datetime.strptime(subtask['updated'], "%Y-%m-%d %H:%M:%S")
                
            if (task_starttime>resttime_start and task_starttime<resttime_end):
                subtask['updated']  = resttime_end.strftime("%Y-%m-%d %H:%M:%S")
                
            today_end_time      = datetime.datetime.strptime(subtask['updated'], "%Y-%m-%d %H:%M:%S")+task_duration
                
            if (today_end_time>resttime_start and today_end_time<resttime_end):
                today_end_time  = resttime_end+datetime.timedelta(minutes=int((today_end_time-resttime_start).total_seconds()/60))
                    
            elif(task_starttime<resttime_start and today_end_time>resttime_end):
                today_end_time  = today_end_time+datetime.timedelta(minutes=int((resttime_end-resttime_start).total_seconds()/60))
                
        
    
        matching_task_time      = dict([['TaskTime',task_rest_time]])
        
        taskkey                 = str(subtask['issuekey'])
        
        matching_task_time.update(href[taskkey])
        matching_task_time.update({'status':subtask['status']})
        matching_task_time.update({'updated':datetime.datetime.strptime(subtask['updated'], "%Y-%m-%d %H:%M:%S")})
        matching_task_time.update({'summary':subtask['summary']})
        matching_task_time.update({'today_end_time':today_end_time})
        taskTime.append([taskkey,matching_task_time])

    return taskTime    
    
def jiraTimeline(jObj,owner):
    timelineJQL             = getJQL(owner)
    timelineQrst,timelineID = jiraQuery(jObj,timelineJQL)
    oneTaskContent          = dealTimelineContent(timelineQrst,timelineID,owner)  
 
    return oneTaskContent

def jiraTable(jObj,user):
    tableJQL            = getJQL(user)
    queryResult,issueID = jiraQuery(jObj,tableJQL)
    htmlCode            = getHTMLSource(queryResult)
    oneCrewContent      = getTableStyle(htmlCode,issueID,user)
    
    return oneCrewContent
    
def main():
    argv                = parserArgument()
    jiraLogin           = login(argv.user,argv.password)
    wholeTableCode      = []
    wholeTimelineCode   = []
    
    table               = jiraTable(jiraLogin, argv.user)
    
    wholeTableCode.append(table)

    CREWS=argv.member.split(':')
    
    for one_crew in CREWS:
        timeline        = jiraTimeline(jiraLogin,one_crew)
        wholeTimelineCode.append(timeline)

    getHTMLStyle(wholeTableCode,wholeTimelineCode)
    print datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
if __name__=='__main__':
    main()


