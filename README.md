# Frogcast Transcription
Transcription service for the best frogcast in all of Willi!

## Transcribing Audio
1. Start up the GUI and you will see the image below (look at that beautiful mustache) 
![](images/gui_start_up.png)
2. Click the "Select Audio File" button to find your file to transcribe
   1. The Output Directory is automatically selected to be a "transcription" directory at the level of the Audio File
3. Optional Updates:
   1. Model Size:
      1. Select the transcription model. A larger model will run with more accuracy but will run slower
         1. ![](images/whisper_models.png)
   2. Time Interval:
      1. Increase/decrease the number of seconds to divide up the final results
4. Click Transcribe and the real time transcription will output to the GUI
![](images/gui_transcribing.png)
5. The result will be shown in GUI or select the Open Transcribed File to open the output in your default text editor
