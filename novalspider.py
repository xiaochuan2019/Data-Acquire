import requests
from bs4 import BeautifulSoup
import collections
import re
import sys

class Spider_novel(object):
	"""
	类说明:下载《笔趣看》网小说: url:https://www.biqukan.com/
	Parameters:
		target - 《笔趣看》网指定的小说目录地址(string)例如：https://www.biqukan.com/1_1094/
	Returns:
		无
	Modify:
		2019-9-19
	"""

	def __init__(self, target):
		self.__target_url = target
		self.__head = {'User-Agent' : 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'}

	def spidertext(self, text_url):
		"""
		函数说明:爬取文章内容
		Parameters:
			text_url - 下载连接(string)
		Returns:
			text - 章节内容(string)
		Modify:
			2019-9-19
		"""	

		text_html = requests.get(text_url, headers = self.__head).content.decode('gbk', 'ignore')
		text_soup = BeautifulSoup(text_html, 'html.parser')
		text_tagset = text_soup.find_all('div',id = 'content', class_ = 'showtxt')
		text = text_tagset[0].get_text().replace('\xa0','')
		return text

	def spiderlink(self):
		"""
		函数说明:获取下载链接
		Parameters:
			无
		Returns:
			novel_name + '.txt' - 保存的小说名(string)
			numbers - 章节数(int)
			link_dict - 保存章节名称[key]和下载链接[value]的字典(OrderedDict)
		Modify:
			2019-9-19
		"""

		link_dict = collections.OrderedDict()#有序字典用来存放链接
		numbers = 0
		IScharter = re.compile(r'[第弟](.+)章')
		
		link_html = requests.get(self.__target_url, headers = self.__head).content.decode('gbk', 'ignore')
		link_soup = BeautifulSoup(link_html, 'html.parser')
		link_tagset = link_soup.find_all('div', class_ = 'listmain')

		novel_name = re.split(r'[\《\》]',str(link_tagset[0].dl.dt))[1]

		switch = "《" + novel_name + "》" + "正文卷"
		begin_switch = False
		for child in link_tagset[0].dl.children: 
			if child != '\n':
				if child.string == switch:
					begin_switch = True
				if begin_switch == True and child.a != None:
						charter_url = 'https://www.biqukan.com' + child.a.get('href')
						charter_name1 = child.get_text() #未略去请假章节
						#charter_name2 = str(charter_name1).split('章') #正规章节切分两块(章字没了)，请假章节题目不含章
						ISleave = IScharter.findall(charter_name1) #如果不是正规章节则返回[]
						if ISleave:
							charter_name = charter_name1
							link_dict[charter_name] = charter_url
							numbers += 1 
		return novel_name + '.txt', numbers, link_dict

	def mywriter(self, path, charter_name, text):
		"""
		函数说明:将爬取的文章内容写入文件
		Parameters:
			path - 当前路径下,小说保存名称(string)
			charter_name - 章节名称(string)
			text - 章节内容(string)
		Returns:
			无
		Modify:
			2019-9-19
		"""

		with open(path, 'a', encoding='utf-8') as f:
			f.write(charter_name + '\n\n')
			for each in text:
				if each != ' ':
					f.write(each)
				if each == '\r':
					f.write('\n')			
			f.write('\n\n')

if __name__ == "__main__":
	print("\n\t\t欢迎使用《笔趣看》小说下载小工具\n\n\t\t作者:xiaochuan\t时间:2018-10-28\n")
	print("*************************************************************************")
	
	#小说地址
	target_url = str(input("请输入小说目录下载地址:\n"))
	
	#实例化下载类
	d = Spider_novel(target = target_url)
	path, numbers, link_dict = d.spiderlink()
	index = 1
	
	#下载中
	print("《%s》下载中:" % path[:-4])
	for key, value in link_dict.items():
		charter_name = key
		text = d.spidertext(value)
		d.mywriter(path, charter_name, text)
		sys.stdout.write("已下载:%.3f%%" %  float(index/numbers) + '\r')#两个百分号是为了输出%本身
		sys.stdout.flush()#在Linux系统下，能一秒输一个数字在,Windows系统下随意
		index += 1	
	print("《%s》下载完成！" % path[:-4])
