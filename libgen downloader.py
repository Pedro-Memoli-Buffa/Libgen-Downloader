from tkinter import *
import os
import bs4
import requests

currentLibgenWebsite = 'https://libgen.is'


os.makedirs('.\\downloaded_books', exist_ok = True)

os.chdir('.\\downloaded_books')


root = Tk()
root.title("E-Book downloader")


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]




#TODO: Hago una clase que scrapee libgen
class LibgenScrapper:
	def __init__(self):
		self.bookList = []



	def provideBooks(self, name, fileType = None):
		#Puedo sortear por extension aca. Spater practicar con tkinter y hacer la interfaz para el programa.
		print('Searching Libgen for %s...' % name)

		linkName = name.replace(' ', '+')
		originalLink = currentLibgenWebsite + '/search.php?req=' + linkName
		link = originalLink

		res = requests.get(link)
		soup = bs4.BeautifulSoup(res.text, 'html.parser')

		bookNameLink = []
		extensionesRespectivas = []
		booksRemain = True

		currentPage = 1		
		while booksRemain:
			print('Looking for books in page %d' % currentPage)


			for tr in soup.find_all('tr'):
				bookFound = False

				for i in tr.find_all('td'):
					possibleBooks = i.find_all('a')

					for possibleBook in possibleBooks:
						if possibleBook != None:
							possibleBookLink = possibleBook.get('href')
							possibleBookName = possibleBook.text

							toDeleteStrings = []

							for possibleToDeleteString in possibleBook.find_all('font'):
								if possibleToDeleteString != None:
									toDeleteString = possibleToDeleteString.text
									toDeleteStrings.append(toDeleteString)


							if 'book/index.php' in possibleBookLink:
								#This is the proper book link. Ich brauche der Name.
								bookLink = currentLibgenWebsite + '/' + possibleBookLink

								for i in toDeleteStrings:
									possibleBookName = possibleBookName.replace(i, '')

								bookNameLink.append((bookLink, possibleBookName))
								bookFound = True


				if len(tr.find_all('td')) == 15:
					extensionesRespectivas.append(tr.find_all('td')[8].text)

						



			#Ahora cambio el objeto en la variable soup y determino si seguir el loop o terminarlo.

			currentPage += 1

			pageModifier = '&page=%d' % currentPage
			link = originalLink + pageModifier

			res = requests.get(link)
			soup = bs4.BeautifulSoup(res.text, 'html.parser')

			#Condicion de break loop.
			overLastPage = True
			for i in soup.find_all('td'):
				possibleBooks = i.find_all('a')

				for possibleBook in possibleBooks:
					if possibleBook != None:
						possibleBookLink = possibleBook.get('href')

						if 'book/index.php' in possibleBookLink:						
							overLastPage = False
							break

			if overLastPage:
				break


		properList = []

		for i in range(len(bookNameLink)):
			if fileType != None:
				if fileType in extensionesRespectivas[i]:
					completeTuple = (bookNameLink[i][0], bookNameLink[i][1], extensionesRespectivas[i])

					properList.append(completeTuple)

			else:
				completeTuple = (bookNameLink[i][0], bookNameLink[i][1], extensionesRespectivas[i])

				properList.append(completeTuple)



		self.bookList = properList


		print('Done searching!\n')

		return self.bookList





	def downloadBook(self, bookIndex = None, notIndexTuple = None):
		if notIndexTuple != None:
			link, name, extension = notIndexTuple


		else:
			link, name, extension = self.bookList[bookIndex]




		res = requests.get(link)
		soup = bs4.BeautifulSoup(res.text, 'html.parser')



		for i in soup.find_all('a'):
			if i != None:
				if 'Gen.lib.rus.ec' in i.text:
					possibleLink = i.get('href')
					if 'http://gen.lib.rus.ec/' not in possibleLink:
						rusDownloadLink = possibleLink
						break


		res = requests.get(rusDownloadLink)
		soup = bs4.BeautifulSoup(res.text, 'html.parser')


		for i in soup.find_all('a'):
			if i != None:
				if 'GET' == i.text:
					print('downloading %s' % name)

					downloadLink = i.get('href')

					#Conseguir la extension del libro
					fileExtension = os.path.splitext(downloadLink)[1]

					downloadedBook = requests.get(downloadLink, stream=True)

					bookFile = open(name + fileExtension, 'wb')

					for chunk in downloadedBook.iter_content(100000):
						bookFile.write(chunk)	

					bookFile.close()

					break			

		print('Done downloading!')




	def downloadBooks(self, indexList):
		for i in indexList:
			self.downloadBooks(bookIndex = i)








#TODO: practicar tkinter
class Gui:
	def __init__(self):
		self.searchFrame = LabelFrame(root, text = 'Book Search')
		self.searchFrame.pack()

		self.booksFoundFrame = LabelFrame(root, text = 'Books Found')


		self.libgenScrapper = LibgenScrapper()

		self.extensionEntry = Entry(self.searchFrame, borderwidth = 3)
		self.dontFilterButton = Button(self.searchFrame, text = "Don't filter", command = lambda : (self.extensionRemover(self.extensionEntry, self.dontFilterButton)))


		self.extension = None

		self.currentPage = 1

		self.booksShown = 10

		self.bookList = []





	def run(self):
		searchLabel = Label(self.searchFrame, text = 'Book to search for: ')
		searchLabel.grid(row = 0, column = 0, padx = 5, pady = 7)

		searchInput = Entry(self.searchFrame, width = 50, borderwidth = 3)
		searchInput.grid(row = 0, column = 1)

		extensionButton = Button(self.searchFrame, text = 'Filter by extension', command = self.extensionFilter)
		extensionButton.grid(row = 1, column = 0, padx = 5, pady = 7)

		searchButton = Button(self.searchFrame, text = '    Search    ', command = lambda: (self.search(searchInput.get(), self.extensionEntry.get())))
		searchButton.grid(row = 0, column = 2, padx = 5)






	def extensionFilter(self):
		self.extensionEntry.grid(row = 1, column = 1, sticky = 'W', padx = 1)

		self.dontFilterButton.grid(row = 1, column = 2, padx = 5, pady = 7)





	def extensionRemover(self, widget1, widget2):
		widget1.destroy()
		widget2.destroy()

		self.extensionEntry = Entry(self.searchFrame, borderwidth = 3)
		self.dontFilterButton = Button(self.searchFrame, text = "Don't filter", command = lambda : (self.extensionRemover(self.extensionEntry, self.dontFilterButton)))




	def search(self, name, extension):
		self.currentPage = 1
		self.bookList = []
		searchingLabel = Label(self.searchFrame, text = 'Finding books...')
		searchingLabel.grid(row = 2, column = 1)

		root.update()

		try:
			self.bookList = self.libgenScrapper.provideBooks(name, fileType = extension)
			self.printSearch()

		except:
			pass

		searchingLabel.destroy()




	def printSearch(self):
		self.booksFoundFrame.destroy()
		self.booksFoundFrame = LabelFrame(root, text = 'Books Found')

		self.booksFoundFrame.pack()

		nextButton = Button(self.booksFoundFrame, text = '>>', command = self.nextPage)
		backButton = Button(self.booksFoundFrame, text = '<<', command = self.backPage)


		#Voy a mostrar 6 libros
		if len(self.bookList) > self.booksShown and self.currentPage == 1:
			nextButton.grid(row = self.booksShown, column = 1, sticky = 'E')


		elif len(self.bookList) > self.booksShown and (self.currentPage * (self.booksShown + 1)) >= len(self.bookList):
			backButton.grid(row = self.booksShown, column = 0, sticky = 'W')


		elif len(self.bookList) > self.booksShown:
			nextButton.grid(row = self.booksShown, column = 1, sticky = 'E')			
			backButton.grid(row = self.booksShown, column = 0, sticky = 'W')			



		separatedByPagesBooks = list(chunks(self.bookList, self.booksShown))


		q = 0
		for i in separatedByPagesBooks[self.currentPage - 1]:
			link = i[0]
			name = i[1]
			extension = i[2]

			bookData = Label(self.booksFoundFrame, text = name + ' - %s' % extension)
			bookData.grid(row = q, column = 0, sticky = 'W')

			dataTuple = (link, name, extension)

			downloadButton = Button(self.booksFoundFrame, text = 'Download', command = lambda dataTuple = dataTuple : (self.download(dataTuple)))
			downloadButton.grid(row = q, column = 1)
			q += 1


	def nextPage(self):
		self.currentPage += 1
		self.printSearch()



	def backPage(self):
		self.currentPage -= 1
		self.printSearch()



	def download(self, notIndexTuplee):
		top = Toplevel()
		downloadingLabel = Label(top, text = 'Downloading   %s   to downloadedBooks directory...' % notIndexTuplee[1])
		downloadingLabel.pack()

		root.update()

		self.libgenScrapper.downloadBook(notIndexTuple = notIndexTuplee)

		downloadingLabel.destroy()
		top.destroy()



app = Gui()
app.run()

root.mainloop()
