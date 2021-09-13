# Scraping Instagram profilees

File [inst_scraping.py](https://github.com/coolyashovaaa/InstagramScraping/blob/main/inst_scraping.py) contains code for scraping Instagram profiles with the help of [Selenium](https://www.selenium.dev/). The initial idea of the project was to collect data on Instagram shops by category. The objective included obtain profile statistics and search for keywords in the bio to test marketing hypotheses. Two ways of working with JSON objects obtained with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) were suggested, these are `dict` and [@dataclass](https://docs.python.org/3/library/dataclasses.html). 

## Dictionary

The basic idea is to decode JSON response to a dictionary and access fields as values by keys. First, the class `ProfileRequest` is used, the instance of which will be the Instagram profile in the form of a dictionary. Then the class `ProfileData` is applied, the attribute `.response_dict` of which is the instance of the first class, and its methods allow to get the required fields.

### Class ProfileRequest

Class attributes are profile username `username` and path to [ChromeDriver](https://chromedriver.chromium.org/) on your computer `driver_path`. The latter is required for `get_dict_response()` method implementation, you can download it [here](https://chromedriver.chromium.org/downloads). If you are a Mac user and have problems with opening ChromeDriver, see [this discussion](https://stackoverflow.com/questions/60362018/macos-catalinav-10-15-3-error-chromedriver-cannot-be-opened-because-the-de).

Method `get_dict_response()` collects data from instagram profile and returns a *dictionary*. Source: [tutorial "Scraping Instagram with python (using Selenium and Beautiful Soup)" by Srujana Takkallapally on medium.com](https://medium.com/@srujana.rao2/scraping-instagram-with-python-using-selenium-and-beautiful-soup-8b72c186a058). 

The two major reasons for using Selenium with Beautiful Soup are:

* [Beautiful Soup restrctions:](https://towardsdatascience.com/real-world-example-on-web-scraping-with-selenium-and-beautiful-soup-3e615dbc1fa1) it is not possible to collect information on profiles and on publications with the same request (note, if you open a profile in a browser and click on a publication, then we will not leave the profile page; such a transition is carried out with a javascript, which BS cannot handle).
* [Simulation of human behavior:](https://towardsdatascience.com/in-10-minutes-web-scraping-with-beautiful-soup-and-selenium-for-data-professionals-8de169d36319) Selenium simulates normal user behavior by opening and closing a page in a browser, which will protect you from being blocked by Instagram.

### Class ProfileData

Attribute `response_dict` is expected to be a dictionary obtained from `get_dict_response()` method apllied to `ProfileRequest` class instance. Class `ProfileData` includes the following attributes:

* *`get_profile_inf(self, fields)`* returns a dict fields such as 'seo_category_infos', 'logging_page_id', 'show_suggested_profiles', 'show_follow_dialog', passed as a list to `fields` parameter.
* *`user_inf(self, fields)`* returns a dict with user data, similar to the above function.
* *`get_publications_stats(self, statistic = 'mean')`* returns a dict with *mean* or *median* number of likes, comments, and videos of last publications (number of publications depends on page size defined in `get_dict_response()`, in this case 12).
* *`search_bio(self, key_words)`* looks for keywords from a list `key_words` and returns a dictionary with words as keys and `True/False` as values.

Below the classes declaration, you can find an example of scraping data of four shops. As a result, `pandas DataFrame` is obtained. 

## Data Class

Python 3.7 and above allowed to store data in [@dataclass](https://realpython.com/python-data-classes/#alternatives-to-data-classes) object. In contrast to the above solution, the shortcoming of this approach is the need to define the fields in advance. However, its advantage is the ability to check the received data types. To decode JSON to Data Class module [dataclasses-json](https://lidatong.github.io/dataclasses-json/) can be applied.

First, you need to create a Data Class which reflects the JSON object structure. Instagram profile response structure is quite complex (probably it was done to push you to use Facebook ads :) ). Therefore, a nested class should be created. Then JSON response object is given to the `from_json()` function, and you can access fields as class attributes. 


