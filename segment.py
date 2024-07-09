from pydub import AudioSegment
import os
from pydub.silence import split_on_silence, detect_silence

#SELECTING AND LOADING THE AUDIO FILE
audio_file_path = "audio.wav"  # Replace with path
audio = AudioSegment.from_wav(audio_file_path)

#GENERATING THE FILE SIZE OF THE AUDIO
file_size = os.path.getsize(audio_file_path)
#<------------------------------------DEBUG STEP------------------------------------->#
print(file_size) #returns in bytes. Eg:802kb -> 80256
#<------------------------------------DEBUG STEP------------------------------------->#


#<------------------------------------ADJUST THESE VALUES---------------------------------->#
#LIMIT OF EACH SEGMENT 
max_size = 3000000 #ALMOST 3 MB OUTPUT SEGEMENTS WILL BE GENERATED. 
#<------------------------------------ADJUST THESE VALUES---------------------------------->#


#CALCULATING MINIMUM NUMBER OF SEGMENTS
#Eg: If FILE_SIZE = 300Kb and MAX_SIZE of segments = 90Kb, Minimum of 4 segments are to be generated.
no_seg = (int)(file_size/max_size)

#<------------------------------------DEBUG STEP------------------------------------->#
print("no of segemnts : ", no_seg)
#<------------------------------------DEBUG STEP------------------------------------->#

#CALULATING TOATL DURATION OF THE AUDIO FILE
audio_duration = len(audio)  #in ms  

#CALCULATING DUARTION OF EACH SEGMENTS
#THIS IS CALCULATED AS PROPOTIONAL TO -> SIZES OF AUDIO / MAX SIZE OF SEGMENTS -> NO OF SEGMENTS
max_segment_length = audio_duration/no_seg

#<------------------------------------DEBUG STEP------------------------------------->#
print(max_segment_length)
#<------------------------------------DEBUG STEP------------------------------------->#


#<------------------------------------ADJUST THESE VALUES---------------------------------->#
# TUNING SILENCE DURATION AND THRESHOLD
# min_silence_len = 100 IMPLIES that a minimum of 100ms of silence is required to 
# identify that duration as a point of silence
min_silence_len = 100  # in ms
silence_thresh = audio.dBFS - 14  
#<------------------------------------ADJUST THESE VALUES---------------------------------->#



# DETECT ALL SILENCE POINTS AND STORE IN A 2D ARRAY
# ARRAY FORMAT IS {start,end} 
# where start and end marks time stamp of silence points
silence_points = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

# Convert silence points from ms to seconds
silence_points_seconds = [(start / 1000, stop / 1000) for start, stop in silence_points]

#<------------------------------------DEBUG STEP------------------------------------->#
print(silence_points)
#<------------------------------------DEBUG STEP------------------------------------->#

# CALCULATING SIZE OF SILENCE POINTS ARRAY
n = len(silence_points)
#ITERATOR TO ITERATE THROUGH SILENCE POINT ARRAY
i=0


#CURR MARKS THE DURATION UPTO WHERE THE ITERATION HAS BEEN DONE
curr =silence_points[0][1]
#LAST MARKS THE PREVIOUS SILENCE POINT
last =0.0
#max_distance MARKS THE LIMIT DURATION IN WHICH THE NEXT SEGMENT SHOULD BE FOUND
max_distance = 0 + max_segment_length



#ARRAY TO STORE ALL THE POINTS WHERE CUTTING CAN BE DONE
# Example: If cut_points = {4.01, 5.03, 6.07}
# Then the final segments shall be 0->4.01, 4.01->5.03, 5.03->6.07 and 6.07 to EOF
cut_points = []


#<------------------------------------DEBUG STEP------------------------------------->#
print("****")
#<------------------------------------DEBUG STEP------------------------------------->#

#<------------------------------------EDGE CASE FLAG--------------------------------->#
flag = 0
#<------------------------------------EDGE CASE FLAG--------------------------------->#

#RUNNING LOOP INSIDE THE SILENCE_POINTS ARRAY
while i<n:

    curr = silence_points[i][1]
    print("max",max_distance)
    if curr > max_distance: # CHECKING IF CURRENT SILENCE POINT IS GREATER THAN THE LIMIT DURATION OF THE SEGMENT

        # EDGE CASES WHERE "NO" SILENCE POINTS ARE FOUND INSIDE THE SEGMENT'S LIMIT
        if i == 0: # First pause is happening after the first segment's duration limit
            print("No pause found before segment 1")
            flag =1
            
        if silence_points[i-1][1] < (max_distance - max_segment_length): # Last silence point was before the current segment
            print(f"No pause found in segment {i+1}")
            flag =1
        
        # IF ANY OF EDGE CASE IS TRUE, THE SEGMENT IS CUT AT SEGMENT'S LIMIT
        # THIS CUT COULD BE POSSIBLY NOT AT PAUSES
        # HENCE WORDS MAYBE SEGEMENTED
        if flag==1:
            #ADDING THE LIMIT TIME STAMP TO CUT_POINTS ARRAY
            cut_points.append(max_distance)
            #UPDATING THE LIMIT TO NEXT SEGMENT'S LIMIT DURATION
            max_distance = max_distance + max_segment_length
            #CONTINUE THE LOOP 
            flag = 0
            continue


        
        # ONCE A SILENCE POINT IS FOUND THAT IS LARGER THAN SEGMENT DURATION LIMIT
        # SILENCE POINT PRIOR TO THAT IS USED AS THE CUT POINT FOR THE SEGMENT
        # HENCE THE SEGMENT IS LESS THAN SEGMENT DURATION LIMIT

        last = silence_points[i-1][1]  #Note: Edge case of i-1 < 0 is handled above 

        #SAVING THE CUT POINTS
        cut_points.append(last)

        #<------------------------------------DEBUG STEP------------------------------------->#
        print(last)
        #<------------------------------------DEBUG STEP------------------------------------->#

        #UPDATING MAX_DISTANCE FOR NEXT SEGMENT'S DURATION LIMIT
        max_distance = last + max_segment_length

    #UPDATING LOOP VARIABLES
    last = curr     
    i = i+1


#<------------------------------------DEBUG STEP------------------------------------->#

print("****")     
print(cut_points)
print("******")
    
#<------------------------------------DEBUG STEP------------------------------------->#



#audio_segments IS AN ARRAY THAT STOREs ALL THE AUDIO SEGMENTS
audio_segments = []

#STORING THE FIRST SEGMENT
audio_segments.append(audio[:cut_points[0]])
#<------------------------------------DEBUG STEP------------------------------------->#
print("0 ",cut_points[0])
#<------------------------------------DEBUG STEP------------------------------------->#

#ITERATING THROUGH CUTPOINTS TO STORE INBETWEEN SEGMENTS
seg_size = len(cut_points)

for i in range(1,seg_size):
    audio_segments.append(audio[cut_points[i-1]:cut_points[i]])
    #<------------------------------------DEBUG STEP------------------------------------->#
    print(cut_points[i-1]," ",cut_points[i])
    #<------------------------------------DEBUG STEP------------------------------------->#

#STORING THE FINAL SEGMENT
audio_segments.append(audio[cut_points[seg_size-1]:])
#<------------------------------------DEBUG STEP------------------------------------->#
print(cut_points[seg_size-1]," EOF")
#<------------------------------------DEBUG STEP------------------------------------->#

#ITERAING THROUGH audio_segment ARRAY
n = len(audio_segments)

#STORING THE SEGMENTS LOCALLY IN .wav format
for i in range(0,n):
    print("audio saved ",{i+1})
    audio_segments[i].export(f"audio{i+1}.wav", format="wav")  #provide export path

#END
print("end")

