# kth_navigator
This program helps students at KTH to read their schedule and navigate campus.

The agent has access to two functions: 'get_locations' and 'get_schedule'.

'get_locations' takes a list of locations as an argument and finds the closest match within the database to each location. It then returns a google-maps link, along with a floor number if it's a room, as context back to the original question.

'get_schedule' takes a time span as an argument and returns the schedule within that time span as context to the original question. 

The agent has access to all of the data within the Data folder, and can utilize the functions above to showcase it or answer questions about it.

Here is an example use case of this program:
```
INPUT: what happens on 14th december?

Final Answer: On 14th December:

1. 'Lecture' for course 'SF1681' will be held at room 'E1' from 08:00 to 10:00

2. 'Exercise' for course 'SF1683' will be held at rooms 'Q17' and 'Q21-22' from 10:00 to 12:00.


INPUT: where can I find the lecture and exercise?

Final Answer: Here are the locations you asked for:

Lecture:
[E1] - https://www.google.com/maps/place/59.34704027500101,18.072885775270187 (Floor 3)

Exercise:
[Q17] - https://www.google.com/maps/place/59.35024453850851,18.06714300371682 (Floor 1)
[Q21-22] - https://www.google.com/maps/place/59.35024453850851,18.06714300371682 (Floor 2)

```
