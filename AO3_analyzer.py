import AO3
import math
import csv


class Fandom:
    def __init__(self, fandomName: str,
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
                revisedAt: str=""):
        """
        Initializes the fandom object with the name of the fandom and the total amount of works in the fandom, given the specified filters.
        Args:
        fandomName: the name of the fandom.
        All args below are optional filters that restrict the search to the given constraints.
        singleChapter (optional): Only include one-shots.
        wordCountMin (optional): The minimum word count a fic can have.
        wordCountMax (optional): The maximum word count a fic can have.
        language (optional): The language the fic is written in. The categories are Not Rated (9), General Audiences (10), Teen and Up Audiences (11), Mature (12), and Explicit (13).
        minHits (optional): The minimum hits/views a work can have.
        maxHits (optional): The maximum hits/vies a work can have.
        crossover (optional): Whether or not to filter crossovers. None includes crossovers, True includes crossovers and excludes all other fics, and False excludes crossovers.
        completionStatus (optional): Only include complete works. None defaults to including both complete and in-progress works.
        revisedAt (optional): Filter works that are either older / more recent than the specified date.        
        """
        self.fandomName = fandomName
        self.singleChapter = singleChapter
        self.language = language
        self.crossover = crossover
        self.completionStatus = completionStatus
        self.revisedAt = revisedAt
        self.session = session

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
                                   completion_status = self.completionStatus, revised_at = self.revisedAt, session = self.session)
        searchResults.update()
        self.totalWorks = searchResults.total_results

    def getRatingComposition(self)->str:
        """
        Returns the percent composition and number of fics as a string in each rating category of AO3. Includes crossovers.
        The categories are Not Rated (9), General Audiences (10), Teen and Up Audiences (11), Mature (12), and Explicit (13).
        """
        ratingResults = ["Not Rated: ", "General Audiences: ", "Teen and Up Audiences: ", "Mature: ", "Explicit: "]
        #ratings are represented by the iintegers 9-13 in the AO3 API.
        for i in range(0, 5):
            searchResults = AO3.Search(fandoms=self.fandomName, single_chapter=self.singleChapter, word_count = self.wordCountConstraint, language = self.language,
                                   hits = self.hitConstraint, bookmarks = self.bookmarkConstraint, comments = self.commentConstraint, crossover = self.crossover, 
                                   completion_status = self.completionStatus, revised_at = self.revisedAt, session = self.session, rating = i+9)
            searchResults.update()
            ratingPercentage = round(100 * searchResults.total_results / self.totalWorks, 2)
            ratingResults[i] = ratingResults[i] + f"{searchResults.total_results} fics, {ratingPercentage} percent of the fandom.\n"
        
        return f'{self.fandomName} Fandom\n' + ''.join(ratingResults)

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
            searchResults = AO3.Search(fandoms=self.fandomName, single_chapter=self.singleChapter, word_count = self.wordCountConstraint, language = self.language,
                                   hits = self.hitConstraint, bookmarks = self.bookmarkConstraint, comments = self.commentConstraint, crossover = self.crossover, 
                                   completion_status = self.completionStatus, revised_at = self.revisedAt, session = self.session, warnings = [value], rating = ratingRestriction)
            searchResults.update()
            warningPercentage = round(100 * searchResults.total_results / self.totalWorks, 2)
            warningResults[index] = warningResults[index] + f"{searchResults.total_results} fics, {warningPercentage} percent of the fandom.\n"
        
        return f'{self.fandomName} Fandom\n' + ''.join(warningResults)
    
    def attributeCounter(self, type: str, rating: int = None, warnings: list = None, 
                         sampleSize: int = None, sortColumn: str = "", sortDirection: str = "") -> dict:
        """
        Given the initial filters specified in the constructor and any additional filters given as args, 
        return a dictionary of all attributes of a given types and how frequently they occur.
        If a fandom is too large, args specified below can count the tags of a smaller sample of the fandom.
        Args:
            type: the specified type of attribute to be counted. Options are 'tags', 'relationships', and 'characters'. 
        Function will default to tags for any other string provided in this parameter. 
            rating (optional): Only sample fics of the specified rating. Ratings are represented as an integer from 9 to 13. 
        Defaults to None (all works are included regardless of rating)
            warnings (optional): The works being counted must include the warnings within the list. 
        Warnings are represented as an integer. Defaults to None.
            sampleSize (optional): only counts the tags of the top n results, where n is sampleSize. 
            sortColumn (optional): How to sort the list (e.g. by hits, title, comments, etc.)
            sortDirection (optional): Which direction to sort (ascending (asc) or descending (desc) order).
        """
        tagCount = dict()
        ficsCounted = 0
        pageNumber = 1  
        if sampleSize is not None:
            totalWorkCount = sampleSize
        else:
            totalWorkCountTemp = AO3.Search(fandoms=self.fandomName, single_chapter=self.singleChapter, word_count = self.wordCountConstraint, language = self.language,
                                   hits = self.hitConstraint, bookmarks = self.bookmarkConstraint, comments = self.commentConstraint, crossover = self.crossover, 
                                   completion_status = self.completionStatus, revised_at = self.revisedAt, session = self.session, warnings = warnings, rating = rating)
            totalWorkCountTemp.update()
            totalWrokCount = totalWorkCountTemp.total_results
        
        while ficsCounted <= totalWorkCount:
            currentPage = AO3.Search(fandoms=self.fandomName, single_chapter=self.singleChapter, word_count = self.wordCountConstraint, language = self.language,
                                     hits = self.hitConstraint, bookmarks = self.bookmarkConstraint, comments = self.commentConstraint, crossover = self.crossover, 
                                     completion_status = self.completionStatus, revised_at = self.revisedAt, session = self.session, 
                                     warnings = warnings, rating = rating, sort_column = sortColumn, sort_direction = sortDirection, page = pageNumber)
            currentPage.update()
            #iterate through entire page (each page contains up to 20 works)
            for work in currentPage.results:
                if type == 'relationships': attributeList = work.relationships
                elif type == 'characters': attributeList = work.characters
                else: attributeList = work.tags
                #initalize attributes as a key in the dictionary or increment the counter by 1.
                for attribute in attributeList:
                    currentCount = tagCount.setdefault(attribute, 0)
                    tagCount[attribute] = currentCount + 1
                ficsCounted += 1
            pageNumber += 1
        return tagCount





