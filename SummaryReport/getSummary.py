#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: anchen
# @Date:   2016-03-22 17:29:29
# @Last Modified by:   anchen
# @Last Modified time: 2016-05-23 15:38:18
import os
import win32com.client as WIN32
from operator import itemgetter
import argparse
import time
class Excel(object):
    _app='Excel'
    _MaxColumn=1024
    _MaxRow=65536
    __SCRIPTNAME_LOCATION=(9,5)
    def __init__(self,filename):
        self.filename=filename
        self.excel=WIN32.gencache.EnsureDispatch('%s.Application' %Excel._app)
        self.Visible=1
        self.xlBook = self.excel.Workbooks.Open(self.filename)
    def save(self):
        self.xlBook.Save()
    def close(self):
        self.xlBook.Close(SaveChanges=0)
        del self.excel

    def worksheet(self,sheetName):
        self.worksheet=self.xlBook.Worksheets(sheetName)

    def changeColor(self,row,col,color):
        self.excel.Cells(row,col).Font.ColorIndex=int(color)

    def setFontColorByRGB(self,row,col,color):
        self.excel.Cells(row,col).Font.Color=int(color)

    def setCellColor(self,row,col,color):
        self.excel.Cells(row,col).Interior.ColorIndex=int(color)

    def setCellColorByRGB(self,row,col,color):
        self.excel.Cells(row,col).Interior.Color=int(color)

    def rgbToInt(self,rgb):
        colorInt = rgb[0] + (rgb[1] * 256) + (rgb[2] * 256 * 256)
        return colorInt

    def setFontBold(self,row,col,yes):
        self.excel.Cells(row,col).Font.Bold=yes

    def setCellFormat(self,row,col,cellColor,fontColor,fontBold=True):
        self.setCellColorByRGB(row,col,self.rgbToInt(cellColor))
        self.changeColor(row,col,fontColor)
        self.setFontBold(row,col,fontBold)

    def getLastColumn(self,row):
        self._nextCol=self.worksheet.Cells(row,Excel._MaxColumn).End(WIN32.constants.xlToLeft).Column
        self._Address=self.worksheet.Cells(row,Excel._MaxColumn).End(WIN32.constants.xlToLeft).Address
        return self._nextCol

    def getRangeByCells(self, (cell_start_row, cell_start_col), (cell_end_row, cell_end_col)):
        """Get a range defined by cell start and cell end e.g. (1,1) A1 and (7,2) B7"""
        return self.worksheet.Range(self.worksheet.Cells(cell_start_row, cell_start_col), 
            self.worksheet.Cells(cell_end_row, cell_end_col))

    def borderRange(self, range1):
        range1.Borders(WIN32.constants.xlEdgeLeft).LineStyle = WIN32.constants.xlContinuous
        range1.Borders(WIN32.constants.xlEdgeTop).LineStyle = WIN32.constants.xlContinuous
        range1.Borders(WIN32.constants.xlEdgeBottom).LineStyle = WIN32.constants.xlContinuous
        range1.Borders(WIN32.constants.xlEdgeRight).LineStyle = WIN32.constants.xlContinuous
        range1.Borders(WIN32.constants.xlInsideVertical).LineStyle = WIN32.constants.xlContinuous
        range1.Borders(WIN32.constants.xlInsideHorizontal).LineStyle = WIN32.constants.xlContinuous

    def getLastRow(self,column):
        self._nextRow=self.worksheet.Cells(Excel._MaxRow,column).End(WIN32.constants.xlUp).Row
        return self._nextRow

    def getColRangeList(self,colNo,start,end):
        RANGE=xrange(start,end+1)
        self.valueList=[]
        for i in RANGE:
            self.valueList.append(self.worksheet.Cells(i,colNo).Value)
        return self.valueList

    def insertRow(self,row,addNo):
        for i in xrange(addNo+1):
            self.worksheet.Range(self.worksheet.Cells(row,1), self.worksheet.Cells(row,1)).EntireRow.Insert(-4161)


    def getRowRangeList(self,RowNo,start,end):
        RANGE=xrange(start,end+1)
        self.valueList=[]
        for i in RANGE:
            self.valueList.append(self.worksheet.Cells(RowNo,i).Value)
        return self.valueList

    def setValue(self,rowIdx,colIdx,value):
        self.worksheet.Cells(rowIdx,colIdx).Value=value

    def findValue(self,matchValue,rangex,idx,search_in_row=True):
        self.pos=0
        if search_in_row==True:
            self.__sumMatch=0
            for i in rangex:
                if  self.worksheet.Cells(idx,i).Value==matchValue:
                    self.__sumMatch+=1
                    self.pos=i

            if self.__sumMatch>1:
                raise Exception,"more than one is the same!"
            elif self.pos==0:
                print "NO MATCH!"
                return None
            else:
                return (idx,self.pos)

        else:
            self.__sumMatch=0
            for i in rangex:
                if  self.worksheet.Cells(i,idx).Value==matchValue:
                    self.__sumMatch+=1
                    self.pos=i
            if self.__sumMatch>1:
                raise Exception,"more than one is the same!"
            elif self.pos==0:
                print "NO MATCH!"
                return None
            else:
                return (self.pos,idx)

    def getValue(self,coords):
        return self.worksheet.Cells(coords[0],coords[1]).Value

    def count_T_and_F(self,valuelist):
        self.FAIL=0
        self.PASS=0
        self.countIdx=0
        for substatus in valuelist:
            self.countIdx+=1
            if (None!=substatus):
                if ("PASS" in substatus.upper()):
                    self.PASS+=1
                    continue
                if ('-' in substatus or "ERROR" in substatus.upper()):
                    self.FAIL+=1
                    continue

        return self.PASS,self.FAIL


class ResultInfo(Excel):
    __resultPOSTION=['number','scriptname','status','logPostion','startTime','endTime','other1','other2','machineName','slotName','JiraID']

    def __init__(self,filename,sheetName):
        super(ResultInfo, self).__init__(filename)
        self.worksheet(sheetName)

    def __getPostion(self,name):
        return ResultInfo.__resultPOSTION.index(name)

    def getScriptname(self):
        return self.getColRangeList(self.__getPostion('scriptname')+1,1,self.getLastRow(self.__getPostion('scriptname')))
       

    def getDuration(self):
        self.duration=[]
        self.startTimeLst=self.getColRangeList(self.__getPostion('startTime')+1,1,self.getLastRow(self.__getPostion('scriptname')))
        self.endTimeLst=self.getColRangeList(self.__getPostion('endTime')+1,1,self.getLastRow(self.__getPostion('scriptname')))
        for x in zip(self.startTimeLst,self.endTimeLst):
            if None not in x:
                self.duration.append(x[1]-x[0])
            else:
                self.duration.append(None)
        return self.duration

    def getStatus(self):
        self.statusList=self.getColRangeList(self.__getPostion('status')+1,1,self.getLastRow(self.__getPostion('scriptname')))
        for idx in xrange(len(self.statusList)):
            if self.statusList[idx]==None:
                continue
            if("ERROR" in self.statusList[idx] or "error" in self.statusList[idx] or "fail" in self.statusList[idx] or "FAIL" in self.statusList[idx]):
                self.statusList[idx]=self.getValue((idx+1,self.getLastColumn(idx+1)))
        return self.statusList




def CycleInfo(cycleNameLst,filename,cycleSheetName,RELATION_BETWEEN_CYCLECSVTILTLE_AND_EXCEL_ROW,NOT_RUN_POSITION_IN_EXCEL,ACTUAL_RUN_POSITION_EXCEL):
    cycleCSV=Excel(filename)
    cycleCSV.worksheet(cycleSheetName)
    try:
        INFOlst=[]
        ROWNOlst=[]
        for cycleName in cycleNameLst:
            temp=RELATION_BETWEEN_CYCLECSVTILTLE_AND_EXCEL_ROW
            CYCLENAMEPOS=1
            lastRow=cycleCSV.getLastRow(CYCLENAMEPOS)
            print cycleName
            coords=cycleCSV.findValue(cycleName,range(1,lastRow+1),CYCLENAMEPOS,False)
            cycleInfoList=cycleCSV.getRowRangeList(coords[0],1,cycleCSV.getLastColumn(coords[0]))       
            usefulList=[]
            if (len(temp)!=len(cycleInfoList)):
                print "WARNING!!! data of '{0}' is wrong!!!,'{0}' has been ignored!!!".format(cycleInfoList[0].upper())
                continue
            passedcnt=None
            failedcnt=None
            totalcnt=None
            for idx in xrange(len(temp)):
                if None in temp[idx]:
                    continue
                elif temp[idx][0]=="passrate":
                    usefulList.append({'content':cycleInfoList[idx]*100.0/10000 ,'rowNo':temp[idx][1]})
                elif temp[idx][0]=="finishrate":
                    usefulList.append({'content':cycleInfoList[idx]*100.0/10000 ,'rowNo':temp[idx][1]})    
                else:
                    usefulList.append({'content':cycleInfoList[idx],'rowNo':temp[idx][1]})       
                    if temp[idx][0]=='passedcnt':
                        passedcnt=cycleInfoList[idx]
                    if temp[idx][0]=='failedcnt':
                        failedcnt=cycleInfoList[idx] 
                    if temp[idx][0]=='totalcnt':
                        totalcnt=cycleInfoList[idx]
 
            usefulList.append({'content':passedcnt+failedcnt,'rowNo':ACTUAL_RUN_POSITION_EXCEL})
            usefulList.append({'content':totalcnt-passedcnt-failedcnt,'rowNo':NOT_RUN_POSITION_IN_EXCEL})
            row_by_rowNo=sorted(usefulList,key=itemgetter('rowNo'))     
            infolst=[]
            rowNOList=[]
            for x in row_by_rowNo:
                infolst.append(x['content'])
                rowNOList.append(x['rowNo'])

            INFOlst.append(infolst)
            ROWNOlst.append(rowNOList)
    finally:
        cycleCSV.close()
        
    return INFOlst,ROWNOlst

def oneCycleResultInfo(pathLst,filename):
    CycleInfoLst=[]
    
    for path in pathLst:
        oneCycleInfo=ResultInfo(path,filename)
        try:
            print os.path.splitdrive(path)[1]
            
            oneCycleInfoTupe=zip(oneCycleInfo.getScriptname(),oneCycleInfo.getStatus(),oneCycleInfo.getDuration())
#             finalReturn=[]
#             for tuple1 in oneCycleInfoTupe:
#                 if (None == tuple1[2] and '-' not in tuple1[1] ):
#                     continue
#                 else:
#                     finalReturn.append(tuple1)
            
        finally:
            oneCycleInfo.close()
        CycleInfoLst.append(oneCycleInfoTupe)    
#         CycleInfoLst.append(finalReturn)
    return CycleInfoLst

def addIntoXlsx(path,sheetName,cycleInfoList,outlineRowNumber,oneCycleResult,outLineTitle):
    

    ScriptColLoc=5
    DuratimeLoc=4
    
    summaryfile=Excel(path)
    summaryfile.worksheet(sheetName)
    
    ERRORColor=3        #red
    CellColor=(0,112,192)#blue
    TitleColor=2        #white

    try:
        for i in xrange(len(cycleInfoList)):
            ScriptAdd=1
            print i+1
            cycleName=cycleInfoList[i][0]
            #find the row of the start
            ScriptLastRow=summaryfile.getLastRow(ScriptColLoc)  

            titlePos=summaryfile.findValue("ScriptName",xrange(1,ScriptLastRow+1),ScriptColLoc,False)   

            lastColPostion=summaryfile.getLastColumn(titlePos[0])
            #find cycle
            alreadyExist=None
            operationCol=None
            if(titlePos[0]!=len(outlineRowNumber[i])+1):
                summaryfile.insertRow(titlePos[0],len(outlineRowNumber[i])-titlePos[0])    

                for idx in xrange(2,outlineRowNumber[i][-1]+1):
                    summaryfile.setValue(idx,ScriptColLoc,outLineTitle[idx-1])  

                titlePos=summaryfile.findValue("ScriptName",xrange(1,ScriptLastRow+1),ScriptColLoc,False)   

            for idx in xrange(titlePos[1],lastColPostion+1):
                if (cycleName==summaryfile.getValue((titlePos[0],idx))):
                    alreadyExist=idx
                    print ".....This Cycle Exists! It will be updated!!"
                    break   

            if alreadyExist==None:
                print ".....new CycleInfo will be added"
                operationCol=lastColPostion+1
                for idx in xrange(1,outlineRowNumber[i][-1]+1):
                    summaryfile.setValue(idx,operationCol,cycleInfoList[i][idx-1])
                summaryfile.setValue(titlePos[0],operationCol,cycleName)
                # summaryfile.setValue(1,operationCol,cycleName)
                summaryfile.setCellFormat(1,operationCol,CellColor,TitleColor)
                summaryfile.setCellFormat(titlePos[0],operationCol,CellColor,TitleColor)
                
            else:
                operationCol=alreadyExist
                for idx in xrange(1,outlineRowNumber[i][-1]+1):
                    summaryfile.setValue(idx,operationCol,cycleInfoList[i][idx-1])
                summaryfile.setValue(titlePos[0],operationCol,cycleName)
                # summaryfile.setValue(1,operationCol,cycleName)
                summaryfile.setCellFormat(1,operationCol,CellColor,TitleColor)
                summaryfile.setCellFormat(titlePos[0],operationCol,CellColor,TitleColor)
                    
    

            existScriptName=summaryfile.getColRangeList(ScriptColLoc,titlePos[0]+1,ScriptLastRow)
            for oneScript in oneCycleResult[i]:

                oneScriptName=oneScript[0]
                status=oneScript[1]
                duration=oneScript[2]
                script_idx=None
                try:
                    for idx in xrange(len(existScriptName)):
                        if (oneScriptName.upper()==existScriptName[idx].upper()):
                            script_idx=idx
                            break
                except Exception, e:

                    print oneScript,idx,existScriptName[idx]
                    raise e
                    
                
                if (script_idx!=None):     
                    summaryfile.setValue(titlePos[0]+1+script_idx,operationCol,status)

                    if (status==None):
                        print "the status of {} in {}th csv file is None".format(existScriptName[idx],i+1)
                    elif ("PASS" not in status or "pass" not in status):
                        summaryfile.changeColor(titlePos[0]+1+script_idx,operationCol,ERRORColor)   

                    summaryfile.setValue(titlePos[0]+1+script_idx,DuratimeLoc,duration)
                else:
                    print "------------------------------------"
                    print "this scriptname will be added in {}".format(ScriptLastRow+ScriptAdd)
                    print "------------------------------------"
                    summaryfile.setValue(ScriptLastRow+ScriptAdd,titlePos[1],oneScriptName)
                    summaryfile.setValue(ScriptLastRow+ScriptAdd,operationCol,status)
                    summaryfile.setValue(ScriptLastRow+ScriptAdd,DuratimeLoc,duration)
                    if (status!=None):
                        if ("PASS"not in status or "pass" not in status):
                            summaryfile.changeColor(ScriptLastRow+ScriptAdd,operationCol,ERRORColor)
                    ScriptAdd+=1    

            #set Border
            Range1=summaryfile.getRangeByCells((1,titlePos[1]),(summaryfile.getLastRow(operationCol),operationCol))
            summaryfile.borderRange(Range1)  
            Range2=summaryfile.getRangeByCells((titlePos[0],1),(summaryfile.getLastRow(operationCol),titlePos[1]-1))
            summaryfile.borderRange(Range2)  
                     
            summaryfile.save() 
        print "......CycleInfo has been added!!!"
    finally:
        summaryfile.close()

def countPassFail(summaryfile,summaryfileSheetName):
    ScriptColLoc=5
    PassLoc=2
    FailLoc=3
    count=Excel(summaryfile)
    count.worksheet(summaryfileSheetName)

    ScriptLastRow=count.getLastRow(ScriptColLoc)

    titlePos=count.findValue("ScriptName",xrange(1,ScriptLastRow+1),ScriptColLoc,False)
    try:
        print ".......Counting the total number of 'PASS' and 'FAIL' "
        row=0
        for idx in xrange(titlePos[0]+1,count.getLastRow(ScriptColLoc)+1):
            row+=1
            start=titlePos[1]+1
            end=count.getLastColumn(titlePos[0])
            rangelist1=count.getRowRangeList(idx,start,end)
            ok,fail=count.count_T_and_F(rangelist1)
            count.setValue(idx,PassLoc,ok)
            count.setValue(idx,FailLoc,fail)
        print "......count Done!"
    except Exception,e:
        raise Exception("{}th row,{} column has somthing wrong! {}".format(row,count.countIdx,count.getValue((row,count.countIdx))))
    finally:
        count.save()
        count.close()


    
def parserArgument():

    parser = argparse.ArgumentParser()
    parser.add_argument('-project',metavar='k',type=str,default="acadia",help="Project Name")
    parser.add_argument('-cycle',metavar='c',type=str,default="cyclename.txt",help="Cycle Name")
    parser.add_argument('-sheetname',metavar='r',type=str,default="WRT Heat Map(A25)",help="Result_Summay sheetname")
    parser.add_argument('-summaryfile',metavar='s',type=str,default="Acadia_WRT_Result_Summay.xlsx",help="the summary File name")

    return parser.parse_args()

def getCycleNameList(cycle_argv):
    EMPTY=''
    if (cycle_argv.endswith(".txt")):
        f=open(os.getcwd()+"\\"+cycle_argv)
        lines=f.readlines()
        f.close()
        NameList=[]
        for name in lines:
            if(EMPTY!=name.strip('\n')):

                temp=name.strip()
                NameList.append(temp.strip('\n'))
        return NameList
    else:
        return [cycle_argv]


def main(): 
    #"cycleCSVTitle" is the names of every column of cycleinfo
    #"excel_corresponding_row" is the Row number of the excel file;if you want to add some items, please revise these two variables.
    #Now I just use the "RELATION_BETWEEN_CYCLECSVTILTLE_AND_EXCEL_ROW" 
    #every tuple of "RELATION_BETWEEN_CYCLECSVTILTLE_AND_EXCEL_ROW" is a relation between cycleCSVTitle and excel row
    #NOT_RUN_POSITION_IN_EXCEL:beacuse the value in the cycleinfo is not correct, so I should recalculate it. 
    #So I mark the tuple "notruncnt" is none
    #
    #ACTUAL_RUN_POSITION_EXCEL: because the value is not in the cycleinfo.csv. so I should calculate it use other info
    #-----------------------------------------------------------------------------------------------------
    # cycleCSVTitle=['cyclename', 'product', 'starttime', 'endtime', 'createTime', 'status', 'no','fwrepo', 'fwrev', 'srtrepo', 'srtrev', 'fwcfg', 'srtcfg', 'totalcnt', 'passedcnt', 'failedcnt', 'errorcnt', 'skippedcnt', 'runningcnt', 'notruncnt', 'passrate', 'finishrate']
    # excel_corresponding_row=[1, None, 9, 10, None, None, None, 11, 12, 13, 14, None, None, 2, 4, 5, None, None, None, None, 6, 7]
    python_start=time.time()
    RELATION_BETWEEN_CYCLECSVTILTLE_AND_EXCEL_ROW=[('cyclename', 1), ('product', None), ('createTime', None),('starttime', 9), ('endtime', 10), ('status', None), ('no', None), ('fwrepo', 11), ('fwrev', 12), ('srtrepo', 13), ('srtrev', 14), ('fwcfg', None), ('srtcfg', None), ('totalcnt', 2), ('passedcnt', 4), ('failedcnt', 5), ('errorcnt', None), ('skippedcnt', None), ('runningcnt', None), ('notruncnt', None), ('passrate', 6), ('finishrate', 7)]
 
    NOT_RUN_POSITION_IN_EXCEL=8
    ACTUAL_RUN_POSITION_EXCEL=3
    
    outLineTitle=['Test Info', 'Ready to Run', 'Actually run', 'Pass', 'ERROR', 'Pass Rate', 'Completion Rate', 'Not Run', 'StartTime', 'EndTime', 'FW Repo', 'FW Version', 'Script Repo', 'Script Version']

    FILELOCATION=r"\\SHWSJENKINS03\testcycle"
    cycleSheetName='cycle'
    resultSheetName='result'

    # INPUT PARAMETER
    argv=parserArgument()
    Result_SummarySheetName=argv.sheetname
    project=argv.project.lower()

    Result_SummaryDir=os.getcwd()
    Result_SummayPath  =Result_SummaryDir+'\\'+argv.summaryfile 

    cycledir=FILELOCATION+"\\"+project
    cyclecsvPath=cycledir+'\\'+'cycle.csv'

    #it is used to get cycleinfo from local
    #cyclecsvPath=os.getcwd()+"\\"+'cycle.csv'

    cyclenameList=getCycleNameList(argv.cycle)



    print "Step1: get data from cycle.csv"
    cycleOutline,outlineRowNumber=CycleInfo(cyclenameList,cyclecsvPath,cycleSheetName,RELATION_BETWEEN_CYCLECSVTILTLE_AND_EXCEL_ROW,NOT_RUN_POSITION_IN_EXCEL,ACTUAL_RUN_POSITION_EXCEL)

    resultcsvPathlst=[]
    for cyclename in cycleOutline:
        cycleResultdir=FILELOCATION+"\\"+project+"\\"+cyclename[0]
        resultcsvPathlst.append(cycleResultdir+'\\'+'result.csv')

    print "Step2: get data from result.csv"
    oneCycleInfo=oneCycleResultInfo(resultcsvPathlst,resultSheetName)
    print "Step3: add data into .xlsx"
    addIntoXlsx(Result_SummayPath,Result_SummarySheetName,cycleOutline,outlineRowNumber,oneCycleInfo,outLineTitle)
    print "Step4: count PASS and FAIL"
    countPassFail(Result_SummayPath,Result_SummarySheetName)
    print ".....All Done!!!"
    python_end=time.time()
    print "It has run: ",python_end-python_start,"socends"
if __name__ == '__main__':
    main()