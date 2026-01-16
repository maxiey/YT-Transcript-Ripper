# https://www.youtube.com/playlist?list=PLHBf9_NALwsa6ODtIOqroonaOy-xAmNeh

#Libraries:
# youtube_transcript_api
# pytube3, NOT PYTUBE, PYTUBE WITH A 3

from youtube_transcript_api import YouTubeTranscriptApi
import urllib.request
import json
import urllib
from pytube import Playlist
from threading import Thread
from queue import Queue
import logging

#-----------------------------------------------------------------------------

playlist = "https://www.youtube.com/watch?v=5SkJdPp35pM"
output_folder = "C:\\temp\\" 
num_worker_threads = 32

#-----------------------------------------------------------------------------

file_name = output_folder + playlist[-13:] + ".txt"

def worker_transcripts():
    while True:
        item = the_queue.get()
        
        params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % item}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string
        
        print("getting transcript for: " + params["url"])

        try:
          with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            #print('Title: ' + data['title'])
        except:
          logging.warning("got an error for url: " + url)
          
          the_queue.task_done()
          continue  # skip loop iteration
          
        # retrieve the available transcripts
        try:
          transcript = YouTubeTranscriptApi.get_transcript(item, languages=['en'])
        except:          
          the_queue.task_done()
          continue  # skip loop iteration

        #data = transcript.fetch() # [{'text': "i'm gonna attempt to collect 30 million", 'start': 0.0, 'duration': 4.16}, {'text': '...
        #print(type(data)) # <class 'list'>

        # Add "video_id" for recover it later: 
        transcript.insert(0, {'video_id': item})

        # Add the fetched data to the "all_transcripts" global variable.
        global all_transcripts
        all_transcripts += transcript

        #print("LES GOOO")

        the_queue.task_done()

def get_playlist(playlist):
  urls = []
  playlist_urls = Playlist(playlist)

  for url in playlist_urls:
    #print("getting video url #" + str(len(urls)))
    url = url[-11:] #only iD is interesting to us
    
    urls.append(url)
  
  return urls

# Get user input here: 
# N.B: You should validate for avoid a blank line or some invalid input...
#user_input = input("Enter a word or sentence: ")
#user_input = user_input.lower()

pl_urls = get_playlist(playlist)
list_of_video_ids = pl_urls

#How can I iterate over this list to return every time stamp?

the_queue = Queue()

for i in range(num_worker_threads):
  t = Thread(target=worker_transcripts)
  t.daemon = True
  t.start()

# Contains all transcripts found: 
all_transcripts = []

# Loop videos: 
for VideoID in list_of_video_ids: 
  the_queue.put(VideoID)

the_queue.join()

# Function to loop all transcripts and search the captions thath contains the 
# user input.
# TO-DO: Validate when no data is found.

def output_transcripts_to_file(dictionary): 
  link = 'https://youtu.be/'

  # Get the video_id: 
  v_id  = ""

  # I add here the debbuged results: 
  lst_results = []

  # You're really looping a list of dictionaries: 
  for i in range(len(dictionary)): # <= this is really a "list".
    try:
      #print(type(dictionary[i])) # <= this is really a "dictionary".
      #print(dictionary[i])

      # now you can iterate here the "dictionary": 
      for x, y in dictionary[i].items():
        #print(x, y)
        if (x == "video_id"): 
          v_id = y
          continue
        elif (x == "text"):
          cur_line = str(dictionary[i]['text']) + ' ...' + str(dictionary[i]['start']) + ' min and ' + str(dictionary[i]['duration']) + ' sec :: ' + link + v_id + '?t=' + str(int(dictionary[i]['start'] - 1)) + 's'
          lst_results.append(cur_line)

    except Exception as err: 
      print('Unexpected error - see details bellow:')
      print(err)

  file = open(file_name, 'w') # PRINTING BABY
  for item in lst_results:
    file.write(item+"\n")
  file.close()
# Function ends here.

# Call function: 
output_transcripts_to_file(all_transcripts) 

# Show message - indicating end of the program - just informative :)
print("End of the program")