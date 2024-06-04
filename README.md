# CSNavBot: Campus Smart Navigation Bot

## Introduction
Welcome to CSNavBot, the intelligent navigation assistant designed for campus environments. Leveraging advanced algorithms and AI, CSNavBot helps users find their way across complex buildings and facilities with ease.<br>
It operates on a keyword-based system, providing users with a selection of options to choose from, ensuring that the keywords match the desired destination or service within the campus.

## Features
- **A* Pathfinding Algorithm**: Utilizes a custom implementation of the A* algorithm for efficient route calculation.
- **Multi-floor Navigation**: Seamlessly guides users through different floors with elevator and stair accessibility options.
- **User-friendly Interface**: Simple and intuitive UI for effortless interaction.

## Presentation Slide
[First Presentation](G5_Presentation_Slide.pdf)
<br>
[Second Presentation](NLP_G5.pdf)

## Infographic
![Info.png](static/Info.png)
![Info2.png](static/Info2.png)
![Info3.png](static/Info3.png)
![Info4.png](static/Info4.png)
![Info4.png](static/Info5.png)

## How to use
This is the main page of the CSNavBot<br>
![1.png](Documentation_Image/1.png)<br>
To know more about this system, you can get more information from the proposal, presentation and infographic.<br>
![2.png](Documentation_Image/2.png)<br>
You can also get the source code of the project from the Github<br>
![3.png](Documentation_Image/3.png)<br>
To open the chatbot, click the chat box button at the bottom right.<br>
![4.png](Documentation_Image/4.png)<br>
GUI for the chatbot<br>
![5.png](Documentation_Image/5.png)<br>
### Navigation
After you click the `Navigation` button, list of selections of the locations will be shown. <br>
The location is sorted by Faculty => Block => Floor<br>
![6.png](Documentation_Image/6.png)<br>
The chatbot reply will slightly different if the mode of the user input is different.<br>
Case Positive:<br>
![image2.png](Documentation_Image/image2.png)<br>
Case Negative:<br>
![image.png](Documentation_Image/image.png)<br>
You can filter the selections by faculty, block, floor and the room/ facilities name.<br>
![8.png](Documentation_Image/15.png)<br>
![8.png](Documentation_Image/16.png)<br>
You should enter your **destination** first, then the **start point**.<br>
After that, if you identify yourself as a person with a disability, then you should input `y` or `yes`, otherwise will consider as NO.<br>
![7.png](Documentation_Image/7.png)<br>
The system will calculate the path and return image showing the path. 
It might take a while to load. During this time, the send button is disabled, so no new message can be sent.<br>
<br>
*If you will the image is too small, click the image, then the image will show in full screen.*
### Course
Below this the GUI for Course Part. List of courses selections will show.<br>
The courses are sorted by Faculty => Course Code => Occurrence Number<br>
![8.png](Documentation_Image/8.png)<br>
You can also filter the selection by typing keyword in textbox.<br>
For example, you can search by lecturer name:<br>
![9.png](Documentation_Image/9.png)<br>
Search by course code or course name:<br>
![10.png](Documentation_Image/10.png)<br>
Then the system will ask for you start point, assuming the location of course you asked is the destination you want.<br>
![11.png](Documentation_Image/11.png)<br>
The output is similar with navigation.
### Events
Below is the GUI of the events part. The list of events are sorted by the date and time of the events.<br>
![13.png](Documentation_Image/13.png)<br>
Similarly, you can search by event name too.
![14.png](Documentation_Image/14.png)<br>
The events details will show.<br>
![details.png](Documentation_Image/details.png)<br>

For all the sections, there will be a `Return` button below.<br>
You can exit the section by clicking the button or type `return` in the text box.
![return.png](Documentation_Image/return.png)