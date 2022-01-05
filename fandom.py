import AO3
import math
import csv
import time

def counter(countDict: dict, itemList: list)->None:
    """
    Destructive helper function.
    Given a dict with items as a key and integers corresponding to the frequency of the items
    and a list of items, increments the value of the item by 1 in the given dictionary each 
    time it appears in the list. If the item does not show up in the dict, a new entry in the
    dictionary is added.
    Args:
        countDict: the dictionary of frequencies
        itemList: the list of items to be counted.
    """
    for item in itemList:
        currentCount = countDict.setdefault(item, 0)
        countDict[item] = currentCount + 1    

class Fandom:
    def __init__(self, fandomName: str = '',
                session: AO3.Session = None,
                singleChapter: bool=False,
                wordCountMin: int=None,
                wordCountMax: int=None,
                language: str="",
                minHits: int=None,
                maxHits: int=None,
                minBookmarks: int=None,
                maxBookmarks: int=None,
                minComments: int=None,
                maxComments: int=None,
                crossover: bool=None,
                completionStatus: bool=None,
                revisedAt: str= "",
                characters: str= "",
                relationships: str= "",
                tags: str = "",):
        """
        Initializes the fandom object with the name of the fandom and the total amount of works in the fandom, given the specified filters.
        All args are optional filters:
        fandomName (optional): the name of the fandom.
        session (optional): the session to use. Specify a user session to access member-only content.
        singleChapter (optional): Only include one-shots.
        wordCountMin (optional): The minimum word count a fic can have.
        wordCountMax (optional): The maximum word count a fic can have.
        language (optional): The language the fic is written in. The categories are Not Rated (9), General Audiences (10), Teen and Up Audiences (11), Mature (12), and Explicit (13).
        minHits (optional): The minimum hits/views a work can have.
        maxHits (optional): The maximum hits/vies a work can have.
        crossover (optional): Whether or not to filter crossovers. None includes crossovers, True includes crossovers and excludes all other fics, and False excludes crossovers.
        completionStatus (optional): Only include complete works. None defaults to including both complete and in-progress works.
        revisedAt (optional): Filter works that are either older / more recent than the specified date.
        characters (optional): Filter to works that must include the specified character. Defaults to "".
        relationships (optional): Filter to works that must include the specified relationship. Defaults to "".
        tags (optional): Filter to works that must include the specified tag. Defaults to "".        
        """
        self.fandomName = fandomName
        self.singleChapter = singleChapter
        self.language = language
        self.crossover = crossover
        self.completionStatus = completionStatus
        self.revisedAt = revisedAt
        self.session = session
        self.characters = characters
        self.relationships = relationships
        self.tags = tags

        if (wordCountMin is not None or wordCountMax is not None):
            if wordCountMin is not None:
                self.wordCountConstraint = AO3.utils.Constraint(wordCountMin, wordCountMax)
            else:
                self.wordCountConstraint = AO3.utils.Constraint(0, wordCountMax)
        else:
            self.wordCountConstraint = None
        
        if (minHits is not None or maxHits is not None):
            if minHits is not None:
                self.hitConstraint = AO3.utils.Constraint(minHits, maxHits)
            else:
                self.hitConstraint = AO3.utils.Constraint(0, maxHits)
        else:
            self.hitConstraint = None
        
        if (minBookmarks is not None or maxBookmarks is not None):
            if minBookmarks is not None:
                self.bookmarkConstraint = AO3.utils.Constraint(minBookmarks, maxBookmarks)
            else:
                self.bookmarkConstraint = AO3.utils.Constraint(0, maxBookmarks)
        else:
            self.bookmarkConstraint = None
        
        if (minComments is not None or maxComments is not None):
            if minComments is not None:
                self.commentConstraint = AO3.utils.Constraint(minComments, maxComments)
            else:
                self.commentConstraint = AO3.utils.Constraint(0, maxComments)
        else:
            self.commentConstraint = None
        
        searchResults = AO3.Search(fandoms=self.fandomName, single_chapter=self.singleChapter, word_count = self.wordCountConstraint, language = self.language,
                                   hits = self.hitConstraint, bookmarks = self.bookmarkConstraint, comments = self.commentConstraint, crossover = self.crossover, 
                                   completion_status = self.completionStatus, revised_at = self.revisedAt, relationships = self.relationships, characters = self.characters, 
                                   tags = self.tags, session = self.session)
        searchResults.update()
        self.totalWorks = searchResults.total_results

    def search(self, rating: int = None, warnings: list = None, sampleSize: int = None, sortColumn: str = "", sortDirection: str = "", pageNumber: int = 1)-> AO3.Search:
        """
        Initializes a new search object based on the specified parameters in __init__ and any additional specifications.
        Args:
            rating (optional): Only sample fics of the specified rating. Ratings are represented as an integer from 9 to 13. 
        Defaults to None (all works are included regardless of rating)
            warnings (optional): The works being counted must include the warnings within the list. 
        Warnings are represented as an integer. Defaults to None.
            sampleSize (optional): only counts the tags of the top n results, where n is sampleSize. 
            sortColumn (optional): How to sort the list (e.g. by hits, title, comments, etc.)
            sortDirection (optional): Which direction to sort (ascending (asc) or descending (desc) order).
        """
        return AO3.Search(fandoms=self.fandomName, single_chapter=self.singleChapter, word_count = self.wordCountConstraint, language = self.language,
                                   hits = self.hitConstraint, bookmarks = self.bookmarkConstraint, comments = self.commentConstraint, crossover = self.crossover, 
                                   completion_status = self.completionStatus, revised_at = self.revisedAt, relationships = self.relationships, characters = self.characters, 
                                   tags = self.tags, session = self.session, rating = rating, warnings = warnings, sort_column = sortColumn, sort_direction = sortDirection, page = pageNumber)

    def getRatingComposition(self)->dict:
        """
        Returns the percent composition and number of fics as a dict of tuples in each rating category of AO3. 
        Tuple consists of total number of fics of that rating and the percent of the total fandom that rating consists of.
        Includes crossovers.
        The categories are Not Rated (9), General Audiences (10), Teen and Up Audiences (11), Mature (12), and Explicit (13).
        """
        ratingResults = {9 : None, 10: None, 11: None, 12: None, 13: None}
        #ratings are represented by the iintegers 9-13 in the AO3 API.
        for i in range(0, 5):
            searchResults = self.search(rating = i + 9)
            searchResults.update()
            ratingPercentage = round(100 * searchResults.total_results / self.totalWorks, 2)
            ratingResults[i + 9] = (searchResults.total_results, ratingPercentage)
            #ratingResults[i] = ratingResults[i] + f"{searchResults.total_results} fics, {ratingPercentage} percent of the fandom.\n"
        return ratingResults

    def getWarningComposition(self, ratingRestriction: int=None)->str:
        """
        Returns the percent composition and number of fics as a string for each warning category of AO3. Includes crossovers.
        The categories are 14 for Creator Chose Not To Use Archive Warnings, 16 for No Archive Warnings Apply, 
        17 for Graphic Depictions Of Violence, 18 for Major Character Death, 19 for Rape/Non-Con, and 20 for Underage.
        Args:
        ratingRestriction (optional): causes function to search only in the specified warning (General, Teen and Up, Mature, etc.). Integers 9-13 correspond to a rating.
        """
        warningValues = [14, 16, 17, 18, 19, 20]
        warningResults = ["Creator Chose Not To Use Archive Warnings: ", "No Archive Warnings Apply: ", 
                          "Graphic Depictions Of Violence: ", "Major Character Death: ", "Rape/Non-Con: ", "Underage: "]
        for index, value in enumerate(warningValues):
            searchResults = self.search(rating = ratingRestriction, warnings = [value])
            searchResults.update()
            warningPercentage = round(100 * searchResults.total_results / self.totalWorks, 2)
            warningResults[index] = warningResults[index] + f"{searchResults.total_results} fics, {warningPercentage} percent of the fandom.\n"
        
        return f'{self.fandomName} Fandom\n' + ''.join(warningResults)
    
    def attributeCounter(self, type: str, rating: int = None, warnings: list = None, 
                         sampleSize: int = None, sortColumn: str = "", sortDirection: str = "", 
                         startPage: int = 1, waitTime: int = 0, tagCount: dict = None) -> dict:
        """
        Given the initial filters specified in the constructor and any additional filters given as args, 
        return a dictionary of dictionaries, where each subdictionary contains the frequencies of all
        tags of the specified type(s). The key of each subdictionary is a string corresponding to a tag,
        while the corresponding value is the frequency that tag occurs represented as an integer.
        If a fandom is too large, args specified below can count the tags of a smaller sample of the fandom.
        Args:
            type: the specified type of attribute to be counted. Options are 'tags', 'relationships', 'characters', or 'all'. 
        Function will default to all for any other string provided in this parameter. 
            rating (optional): Only sample fics of the specified rating. Ratings are represented as an integer from 9 to 13. 
        Defaults to None (all works are included regardless of rating)
            warnings (optional): The works being counted must include the warnings within the list. 
        Warnings are represented as an integer. Defaults to None.
            sampleSize (optional): only counts the tags of the top n results, where n is sampleSize. 
            sortColumn (optional): How to sort the list (e.g. by hits, title, comments, etc.)
            sortDirection (optional): Which direction to sort (ascending (asc) or descending (desc) order).
            startPage (optional): the page of the search to start counting attributes at. Defaults to 1 (first page)
            waitTime (optional): how long to wait between searches. Avoids hitting the rate limit. Defaults to 0 seconds.
            tagCount(optional): an existing tag count to be added to.
        """
        if tagCount == None:
            if (type == 'tags' or type == 'relationships' or type == 'characters'): tagCount = {type: dict()}
            else: tagCount = {'tags': dict(), 'relationships': dict(), 'characters': dict()}
        ficsCounted = 0
        pageNumber = startPage
        relationshipList, characterList, tagList = None, None, None  
        if sampleSize is not None:
            totalWorkCount = sampleSize
        else:
            totalWorkCountTemp = self.search(warnings = warnings, rating = rating)
            totalWorkCountTemp.update()
            totalWorkCount = totalWorkCountTemp.total_results
        
        while ficsCounted < totalWorkCount:
            currentPage = self.search(warnings = warnings, rating = rating, sortColumn = sortColumn, 
                                      sortDirection = sortDirection, pageNumber = pageNumber)
            currentPage.update()
            #iterate through entire page (each page contains up to 20 works)
            for work in currentPage.results:
                if type == 'relationships': relationshipList = work.relationships
                elif type == 'characters': characterList = work.characters
                elif type == 'tags': tagList = work.tags
                else: relationshipList, characterList, tagList = work.relationships, work.characters, work.tags
                if 'relationships' in tagCount: counter(tagCount['relationships'], relationshipList)
                if 'characters' in tagCount: counter(tagCount['characters'], characterList)
                if 'tags' in tagCount: counter(tagCount['tags'], tagList)
                ficsCounted += 1
            pageNumber += 1
            time.sleep(waitTime)
        return tagCount



