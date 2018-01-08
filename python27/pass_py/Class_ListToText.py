#coding=utf-8 测试通过：将数组保存为txt，从txt读出数组 2017-12-26
class ListTextHelp:
    ipTable = []
    Return_List = []
    txtFileName = "IpTable.txt"
    def ToText(self):
        if self.ipTable :
            fileObject = open(self.txtFileName, 'w')
            for ip in self.ipTable:
                fileObject.write(ip)
                fileObject.write('\n')
            fileObject.close()
        else:
            print ("No List!")
    def ReadText(self):
        file = open(self.txtFileName)
        for line in file:
            self.Return_List.append(line.replace("\n",""))

if __name__ == '__main__':
    ipTable = ['11', '222', '33']
    td = ListTextHelp()
    # td.ipTable = ipTable
    td.ReadText()
    arr = td.Return_List
    print  (arr)

