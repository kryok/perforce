import os
import time
import operator
import shutil
import re
import stat
import filecmp
from sys import argv

alist={}
now = time.time()

#path of results
result_home_dir = '/home/xtapi/regression_results/'

#path of a local temp dir and create dirs
script_dir = '/home/xtapi/jeff/Spirent_Temp'
local_dst_dir = '/home/xtapi/jeff/Spirent_Temp/temp'
path_listfile = '/home/xtapi/jeff/Spirent_Temp/listfile'
path_descfile = '/home/xtapi/jeff/Spirent_Temp/submit'

#delete 'd:/Spirent_Temp' and its sub_dirs
try:
    shutil.rmtree(r'%s' %script_dir)
except Exception,e:
    print Exception,":",e

#create 3 sub_dirs in 'd:/Spirent_Temp'

os.makedirs('%s' %local_dst_dir)
os.makedirs('%s' %path_listfile)
os.makedirs('%s' %path_descfile)

#path of p4 depot
depot = '//TestCenter/integration/content/HltAPI'
depot_j = '//TestCenter/p2_dev_jtapi'
#path of p4 workspace
#workspace = 'D:/Jeff/perforce/TestCenter/integration/content/HltAPI'
#path of p4 workspace_jtapi
#workspace_j = 'D:/Jeff/perforce/TestCenter/p2_dev_jtapi'

filename,workspace,workspace_j,desc,regression_name = argv

def get_lastest_dir(result_home_dir,regression_name):
#get into dir of chosen regression_name
    os.chdir('%s/%s/' %(result_home_dir,regression_name))

#find the newest folder in regression_name dir
    for file in os.listdir("."):
        if os.path.isdir(file):
            timestamp = os.path.getmtime( file )
# get timestamp and directory name and store to dictionary
            alist[os.path.join(os.getcwd(),file)]=timestamp


# sort the timestamp 
    for i in sorted(alist.iteritems(), key=operator.itemgetter(1)):
        latest="%s" % ( i[0])

    b = r'%s' %latest
#get the newest dir
    latest_dir = re.split(r"/",b)[-1]
    print "latest_dir : %s" %latest_dir
# latest=sorted(alist.iteritems(), key=operator.itemgetter(1))[-1]
    # print "The newest directory is ", latest
    #os.chdir(latest)
    return latest_dir

def copy_running_2_dst(local_dst_dir,result_home_dir,regression_name,latest_dir):
    num = 0
    filename1 = []
    os.chdir ('%s/%s/%s' % (result_home_dir,regression_name,latest_dir))
    print "\nWe are listing out dirs whose name are same as script_name"
    directories_in_curdir = filter(os.path.isdir, os.listdir(os.curdir))
    print directories_in_curdir
    for i in directories_in_curdir:
        os.chdir('%s/%s/%s/%s' % (result_home_dir,regression_name,latest_dir,i))
#get directories in current_dir(current_dir whose dir_name is each script_name)
        directories_in_curdir1 = filter(os.path.isdir, os.listdir(os.curdir))
        for j in directories_in_curdir1:
            if j =='running':
                os.chdir ('%s/%s/%s/%s/%s' % (result_home_dir,regression_name,latest_dir,i,j))
#find out conf file and copy it to local_dst_dir                                    
                for filename in os.listdir('.'):
                    if filename.endswith('conf'):
                       num += 1
                       shutil.copy('./%s' %filename,'%s' %local_dst_dir)
                       filename1.append('%s' %filename)
    print "%s conf files has been copied" %num
    print "copied file(s) are : "
    print filename1

def copy_running_2_dst_hltapiGen(result_home_dir,regression_name,latest_dir,local_dst_dir):
    os.chdir ('%s/%s/%s/start' % (result_home_dir,regression_name,latest_dir))
    a = "./expected"
    b = "./running"
    dirobj=filecmp.dircmp(a,b)
    c = dirobj.diff_files
    print "diff_files: %s" %c
    os.chdir ('%s/%s/%s/start/running' % (result_home_dir,regression_name,latest_dir))
    print "current dir is : %s" %(os.path.abspath(os.curdir))
    d = os.path.abspath(os.curdir)
    i = 0
    for filename in c:
        i += 1
        shutil.copy('%s/%s' %(d,filename),'%s' %local_dst_dir)
        print "File %s has been copied to local_dst_dir : %s" %(filename,local_dst_dir)
    print "%s files has been copied" %i
    print "the files copied are:"
    print c

def copy_dst_2_workspace(regression_name,suffix,local_dst_dir,workspace_dir):
    num = 0
    for filename in os.listdir('%s' %local_dst_dir):
        if filename.endswith('%s' %suffix):
            num += 1
            shutil.copyfile('%s/%s' %(local_dst_dir,filename),'%s/%s' %(workspace_dir,filename))
            print "File %s has been copied to workspace : %s" %(filename,workspace_dir)
        else:
            pass

#script_dir is the dir of this python script,list_filename is the full name of the list file,including suffix
def create_listfile (script_dir,list_filename) :
    listfile = open('%s/listfile/%s' %(script_dir,list_filename),'w')
    for filename in os.listdir('%s/temp' %script_dir):
         listfile.write('%s\n' %filename)
    listfile = open('%s/listfile/%s' %(script_dir,list_filename))
    content = listfile.read()
    listfile.close()
    print "the content of listfile are :\n"
    print content

#script_dir is the dir of this python script,desc_filename is the full name of the description file,including suffix
#depot_dir is the dir of current regression workspace of p4
def create_descfile (desc,depot_dir,script_dir,desc_filename) :
    #depot_dir = '//TestCenter/integration/content/HltAPI/SampleScripts/hltapi'
    #desc = raw_input("Please input description of submit:")
    description = """
#  Date:        The date this specification was last modified.
#  Client:      The client on which the changelist was created.  Read-only.
#  User:        The user who created the changelist.
#  Status:      Either 'pending' or 'submitted'. Read-only.
#  Type:        Either 'public' or 'restricted'. Default is 'public'.
#  Description: Comments about the changelist.  Required.
#  regression_names:        What opened regression_names are to be closed by this changelist.
#               You may delete regression_names from this list.  (New changelists only.)
#  Files:       What opened files from the default changelist are to be added
#               to this changelist.  You may delete files from this list.
#               (New changelists only.)

Change:	new

Client:	Conf-Scripts-Replacement

User:	xtapi

Status:	new

Description:
     Description:%s
     Change Type:DevTest 
     Change #:DevTest
     Reviewed by: None 
     Review ID: None 
     Approved by: None  
     Designer Testing:None 
     Testing Impact: None\n
Files:\n""" %desc

    submit = open('%s/submit/%s' %(script_dir,desc_filename),'a')

    submit.write('%s' %description)

    for filename in os.listdir('%s/temp' %script_dir):
         format = '%s/%s # edit' %(depot_dir,filename)
         submit.write('    %s\n' %format)
    submit = open('%s/submit/%s' %(script_dir,desc_filename))
    content = submit.read()
    submit.close()
    print "the content of desc file are :\n"
    print content

def submit_edit(workspace_dir,script_dir,list_filename,desc_filename,regression_name,suffix,local_dst_dir):
#change dir
    os.chdir ('%s' %workspace_dir)
    print "We've changed path to workspace,and current dir is : %s" %(os.path.abspath(os.curdir))

    list_filename = '%s/listfile/%s' %(script_dir,list_filename)
    desc_filename = '%s/submit/%s' %(script_dir,desc_filename)

#execute p4 edit
    edit = "p4 -s -x %s edit" %list_filename
    os.system('%s' %edit)
    print "p4 edit is done,and then copy files to workspace."

#execute copy from local_dst_dir to workspace
    copy_dst_2_workspace(regression_name,suffix,local_dst_dir,workspace_dir)
    print "copy is done,and then ready to submit."

#execute p4 submit
    submit = "p4 submit -i < %s" %desc_filename
    os.system('%s' %submit)


def edit_copy_submit (depot,workspace,path,regression_name,script_dir,suffix,local_dst_dir):
    current_depot = "%s/%s" %(depot,path)
    #workspace = '%s/UnitTest/HLTAPI_UT' %workspace
    workspace = '%s/%s' %(workspace,path)
    print "\ncurrent depot is %s\n" %current_depot
    print "current workspace is %s\n" %workspace

    list_filename = time.strftime("filelist_%Y-%m-%d-%H-%M-%S", time.localtime())
    desc_filename = time.strftime("descfile_%Y-%m-%d-%H-%M-%S", time.localtime())
    create_listfile(script_dir,list_filename)
    create_descfile(desc,current_depot,script_dir,desc_filename)
    submit_edit(workspace,script_dir,list_filename,desc_filename,regression_name,suffix,local_dst_dir)


# print  "    1 : hltapi-dev-regression\n\
    # 2 : hltapi-samplescript-regression\n\
    # 3 : jtapi-dev-regression\n\
    # 4 : jtapi-samplescript-regression\n\
    # 5 : regression-hlapiGen-unitTest\n\
    # 6 : python-sample-regression\n\
    # 7 : regression-hlapiGen-robot"
# a = raw_input("Please choose a regression regression_name above: ")
# if a == '1':
    # regression_name = "hltapi-dev-regression"
# if a == '2':
    # regression_name = "hltapi-samplescript-regression"
# if a == '3':
    # regression_name = "jtapi-dev-regression"
# if a == '4':
    # regression_name = "jtapi-samplescript-regression"
# if a == '5':
    # regression_name = "regression-hlapiGen-unitTest"
# if a == '6':
    # regression_name = "python-sample-regression"
# if a == '7':
    # regression_name = "regression-hlapiGen-robot"

# print "Your choice is %s : %s\n" % (a,regression_name)

# #prepare description of submission
# desc = raw_input("Please input description of submit,which will be used later:")

#get latest_dir of chosen regression in dir results
latest_dir = get_lastest_dir(result_home_dir,regression_name)

#hltapi-dev-regression
#Tested all OK on Sep6
if regression_name == 'hltapi-dev-regression':
    suffix = 'conf'
    path = 'UnitTest/HLTAPI_UT'
    print "You've chosen %s" %regression_name

#copy conf files from running to local_dst_dir
    copy_running_2_dst(local_dst_dir,result_home_dir,regression_name,latest_dir)
    
#check out and then copy conf files from local_dst_dir to workspace and then submit to depot
    edit_copy_submit (depot,workspace,path,regression_name,script_dir,suffix,local_dst_dir)
        

#OK on Aug16,2017
if regression_name == 'hltapi-samplescript-regression':
    suffix = 'conf'
    path = 'SampleScripts/hltapi'
    print "You've chosen %s" %regression_name

#copy conf files from running to local_dst_dir
    copy_running_2_dst(local_dst_dir,result_home_dir,regression_name,latest_dir)
    
#check out and then copy conf files from local_dst_dir to workspace and then submit to depot
    edit_copy_submit (depot,workspace,path,regression_name,script_dir,suffix,local_dst_dir)


#jtapi-dev-regression
if regression_name == 'jtapi-dev-regression':
    suffix = 'conf'
    path = 'UnitTest/JTAPI_UT'
    print "You've chosen %s" %regression_name

#copy conf files from running to local_dst_dir
    copy_running_2_dst(local_dst_dir,result_home_dir,regression_name,latest_dir)
    
#check out and then copy conf files from local_dst_dir to workspace and then submit to depot
    edit_copy_submit (depot_j,workspace_j,path,regression_name,script_dir,suffix,local_dst_dir)


#jtapi-samplescript-regression
if regression_name == 'jtapi-samplescript-regression':
    suffix = 'conf'
    path = 'ReleaseFolder/SampleScripts'
    print "You've chosen %s" %regression_name

#copy conf files from running to local_dst_dir
    copy_running_2_dst(local_dst_dir,result_home_dir,regression_name,latest_dir)
    
#check out and then copy conf files from local_dst_dir to workspace and then submit to depot
    edit_copy_submit (depot_j,workspace_j,path,regression_name,script_dir,suffix,local_dst_dir)


#regression-hlapiGen-unitTest
#OK on Sep18,2017
if regression_name == 'regression-hlapiGen-unitTest':
    suffix = 'tcl'
    path = 'UnitTest/hlapiGen_tcl'
    print "You've chosen %s" %regression_name

#copy tcl scripts from running to local_dst_dir
    copy_running_2_dst_hltapiGen(result_home_dir,regression_name,latest_dir,local_dst_dir)

#check out and then copy tcl scripts from local_dst_dir to workspace and then submit to depot
    edit_copy_submit (depot,workspace,path,regression_name,script_dir,suffix,local_dst_dir)


#python-sample-regression
if regression_name == 'python-sample-regression':
    suffix = 'conf'
    path = 'SampleScripts/hltapiForPython'
    print "You've chosen %s" %regression_name

#copy conf files from running to local_dst_dir
    copy_running_2_dst(local_dst_dir,result_home_dir,regression_name,latest_dir)
    
#check out and then copy conf files from local_dst_dir to workspace and then submit to depot
    edit_copy_submit (depot,workspace,path,regression_name,script_dir,suffix,local_dst_dir)


#regression-hlapiGen-robot
#OK on Oct16,2017
if regression_name == 'regression-hlapiGen-robot':
    suffix = 'robot'
    path = 'UnitTest/hlapiGen_robot'
    print "You've chosen %s" %regression_name

#copy robot files from running to local_dst_dir
    copy_running_2_dst_hltapiGen(result_home_dir,regression_name,latest_dir,local_dst_dir)
    
#check out and then copy robot files from local_dst_dir to workspace and then submit to depot
    edit_copy_submit (depot,workspace,path,regression_name,script_dir,suffix,local_dst_dir)
        
    


        
    